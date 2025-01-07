'''
Script che chiama il modello llama3 (4.7 GB) tramite le API REST ollama e cerca
di estrarre tutti i dati privati presenti in un estratto dei log.
Questa versione (v3) ascolta sulla porta TCP 24367 dalla quale legge righe di log in formato GELF.
'''

import asyncio
import json
import re
import socket
import sys
import httpx
import ollama
# import regex_list

port = 24367

# Numero di messaggi da inviare prima di cambiare chat.
# Serve per evitare di saturare la "memoria" (token) del modello.
# Dopo aver inviato `n_messaggi_prima_di_cambiare_chat` messaggi, la chat
# viene resettata e quindi riparte.
# Mettere 0 per non cambiare mai chat.
n_messaggi_prima_di_cambiare_chat = 15

# llm = 'sensitive-data-extractor-llama3.1:8b'
# llm = 'sensitive-data-extractor-llama3.2:3b'
# llm = 'sensitive-data-extractor-mistral:7b'
# llm = 'sensitive-data-extractor-mistral-nemo:12b'
llm = 'sensitive-data-extractor-qwen2.5:7b'

n_messaggi_inviati_chat_corrente = 0
messaggi = []


async def handle_connection(reader, _writer):
    global n_messaggi_inviati_chat_corrente
    global messaggi

    while True:
        payload = (await reader.read(16384)).decode('utf-8')
        if not payload:
            continue

        payload = payload.split('\x00')

        for messaggio in payload:
            if messaggio == '':
                continue

            messaggio = json.loads(messaggio)
            riga = messaggio['_message']
            riga = messaggio['_message']
            log_id = messaggio['_id']

            # Se è il momento di cambiare chat, resetta l'elenco dei messaggi
            if (
                n_messaggi_prima_di_cambiare_chat != 0 and
                n_messaggi_inviati_chat_corrente == n_messaggi_prima_di_cambiare_chat
            ):
                n_messaggi_inviati_chat_corrente = 0
                messaggi = []

            # Gestione regex disabilitata: viene già applicata nelle pipeline di GrayLog.
            # Applica le regex manuali per cercare dati sensibili
            # all_regex_matches = []
            # for regex in regex_list.regex_list:
            #     matches = re.findall(regex['regex'], riga)
            #     if matches:
            #         for m in matches:
            #             all_regex_matches.append(f"{regex['name']} {m}")

            # Se sono già stati trovati dati sensibili con la regex, vengono
            # già inviati a GrayLog.
            # if len(all_regex_matches) > 0:
            #     for match in all_regex_matches:
            #         msg = f'{log_id}: {match}'
            #         print(msg)
            #         # Invio della risposta allo stream apposito di GrayLog
            #         client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #         client.connect(('localhost', 5556))
            #         msg = msg + '\x00'
            #         client.send(msg.encode('utf-8'))
            #         client.close()

            messaggi.append({
                'role': 'user',
                'content': riga
            })

            try:
                response = ollama.chat(
                    model=llm,
                    messages=messaggi
                )
            except httpx.ConnectError as e:
                print(
                    'Errore: impossibile connettersi al server Ollama. Assicurarsi che sia attivo.')
                sys.exit(1)
            except Exception as e:
                print(e)
                sys.exit(1)

            risposta: str = response['message']['content']
            if risposta.lower().strip() != 'none':
                msg = f'{log_id}: {risposta}'
                print(msg)
                # Invio della risposta allo stream apposito di GrayLog
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect(('localhost', 5556))
                msg = msg + '\x00'
                client.send(msg.encode('utf-8'))
                client.close()
            else:
                print(risposta)

            messaggi.append(response['message'])
            n_messaggi_inviati_chat_corrente += 1


async def main() -> None:
    global n_messaggi_prima_di_cambiare_chat
    global llm

    server = await asyncio.start_server(
        handle_connection,
        '0.0.0.0',
        port
    )

    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    try:
        print(f'Avvio in corso, in ascolto sulla porta {
              port}. Premere Ctrl+C per interrompere in qualsiasi momento.')
        asyncio.run(main())
    except KeyboardInterrupt:
        exit(0)
