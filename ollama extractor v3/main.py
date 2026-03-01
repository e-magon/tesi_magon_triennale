"""
Script che utilizza degli LLM tramite le API REST ollama e prova ad identificare
tutti i dati privati presenti all'interno di righe di log.
In questa versione (v3) lo script ascolta sulla porta TCP 24367 dalla quale
legge le righe di log in formato GELF, inoltrate da GrayLog.
"""

import asyncio
import json
import re
import socket
import sys
import time
import httpx
import ollama
import requests
import regex_list

port = 24367

# GrayLog applica già delle regex per cercare dati sensibili.
# Per evitare duplicazioni, la gestione delle regex manuali di questo script
# è disabilitata di default.
regex_enabled = False

# Numero di messaggi da inviare prima di cambiare chat.
# Serve per evitare di saturare la "memoria" (token) del modello.
# Dopo aver inviato `n_messaggi_prima_di_cambiare_chat` messaggi, la chat
# viene resettata e quindi riparte.
# Mettere 0 per non cambiare mai chat.
n_messaggi_prima_di_cambiare_chat = 15

# Se si avvia lo script con `--pull-last-logs-from-stream <stream_id>` si attiva la modalità pull_mode.
# In questa modalità, invece di ascoltare sulla porta TCP, lo script ottiene i log
# direttamente chiamando le API REST di Graylog, ottenendo le righe con un timestamp maggiore
# di quello usato l'ultima volta che è stato eseguito lo script.
pull_mode = False
pull_from_stream_id = None

# Modello utilizzato di default.
llm = 'sensitive-data-detector-llama3.1:8b'
# llm = 'sensitive-data-detector-llama3.2:3b'
# llm = 'sensitive-data-detector-mistral:7b'
# llm = 'sensitive-data-detector-mistral-nemo:12b'
# llm = 'sensitive-data-detector-qwen2.5:7b'
# llm = 'sensitive-data-detector-gemma3:4b'
# llm = 'sensitive-data-detector-gemma3:12b'
# llm = 'sensitive-data-detector-deepseek-r1:7b'
# llm = 'sensitive-data-detector-deepseek-r1:8b'

n_messaggi_inviati_chat_corrente = 0
messaggi = []


async def handle_message(log_id, riga):
    """
    Metodo che invia al modello LLM tramite le API REST
    di Ollama il messaggio ricevuto, e invia la risposta a GrayLog tramite una connessione TCP
    sulla porta 5556.
    """
    global n_messaggi_inviati_chat_corrente
    global messaggi

    # Se è il momento di cambiare chat, resetta l'elenco dei messaggi
    if (
        n_messaggi_prima_di_cambiare_chat != 0 and
        n_messaggi_inviati_chat_corrente == n_messaggi_prima_di_cambiare_chat
    ):
        n_messaggi_inviati_chat_corrente = 0
        messaggi = []

    if regex_enabled:
        # Se regex_enabled è True, viene eseguita l'analisi statica
        # attraverso le regex manuali.
        # La soluzione migliore è utilizzare GrayLog per l'analisi
        # statica, ma rimane comunque la possibilità di utilizzare
        # le regex manuali in questo script.

        # Applica le regex manuali per cercare dati sensibili
        all_regex_matches = []
        for regex in regex_list.regex_list:
            matches = re.findall(regex['regex'], riga)
            if matches:
                for m in matches:
                    all_regex_matches.append(f"{regex['name']} {m}")

        # Se sono già stati trovati dati sensibili con la regex, vengono
        # già inviati a GrayLog.
        if len(all_regex_matches) > 0:
            for match in all_regex_matches:
                msg = f'{log_id}: {match}'
                print(msg)
                # Invio della risposta allo stream apposito di GrayLog
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect(('localhost', 5556))
                msg = msg + '\x00'
                client.send(msg.encode('utf-8'))
                client.close()

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
        # Invio della risposta allo stream di GrayLog, in modo che possa
        # catalogarla e salvarla all'interno del sistema.
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', 5556))
        msg = msg + '\x00'
        client.send(msg.encode('utf-8'))
        client.close()
    else:
        print(risposta)

    messaggi.append(response['message'])
    n_messaggi_inviati_chat_corrente += 1


async def handle_connection(reader, _writer):
    """
    Metodo di callback eseguito ad ogni connessione in entrata da GrayLog.
    Legge i messaggi in arrivo, li invia al modello LLM tramite le API REST
    di Ollama, e invia la risposta a GrayLog tramite una connessione TCP
    sulla porta 5556.
    """
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
            log_id = messaggio['_id']

            # Elabora il messaggio ricevuto tramite regex e LLM, e invia la risposta a GrayLog
            await handle_message(log_id, riga)


async def main_push() -> None:
    """
    Metodo principale per la modalità push, nella quale lo script ascolta
    sulla porta TCP per ricevere i log in arrivo da GrayLog.
    """
    global n_messaggi_prima_di_cambiare_chat
    global llm

    server = await asyncio.start_server(
        handle_connection,
        '0.0.0.0',
        port
    )

    async with server:
        await server.serve_forever()

async def main_pull() -> None:
    """
    Metodo principale per la modalità pull, nella quale lo script ottiene i log
    direttamente chiamando le API REST di GrayLog, filtrate per timestamp.
    """
    global n_messaggi_prima_di_cambiare_chat
    global llm

    # Configurazione
    GRAYLOG_URL = 'http://localhost:9000/api'
    USERNAME = 'admin'
    PASSWORD = 'admin'

    now = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime(time.time()))

    # Prova a leggere il file "last_run_timestamp.txt" per ottenere il timestamp dell'ultima esecuzione.
    # Se il file non esiste, utilizza now - 24h come timestamp di partenza.
    try:
        with open('last_run_timestamp.txt', 'r') as f:
            last_run_timestamp = f.read().strip()
    except FileNotFoundError:
        last_run_timestamp = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime(time.time() - 24*3600))

    print(f"Da {last_run_timestamp} a {now}")

    url = f'{GRAYLOG_URL}/search/universal/absolute'
    params = {
        'query': '*',
        'filter': f'streams:{pull_from_stream_id}',
        'from': last_run_timestamp,
        'to': now
    }

    http_session = requests.Session()
    http_session.auth = (USERNAME, PASSWORD)
    http_session.headers.update({'X-Requested-By': 'Python Script'})
    http_session.headers.update({'Accept': 'application/json'})

    response = http_session.get(url, params=params)
    response.raise_for_status()

    results = response.json()['messages']
    for result in results:
        messaggio = result['message']
        riga = messaggio['message']
        log_id = messaggio['_id']

        # Elabora il messaggio ricevuto tramite regex e LLM, e invia la risposta a GrayLog
        await handle_message(log_id, riga)

    # Una volta terminata l'elaborazione, salva il timestamp utilizzato nel filtro "to" come "last_run_timestamp"
    with open('last_run_timestamp.txt', 'w') as f:
        f.write(now)


if __name__ == '__main__':
    if len(sys.argv) >= 3 and sys.argv[1] == '--pull-last-logs-from-stream':
        pull_mode = True
        pull_from_stream_id = sys.argv[2]
        print(pull_mode)
        print(pull_from_stream_id)

    try:
        if pull_mode:
            print(f'Ottengo gli ultimi log dallo stream GrayLog {pull_from_stream_id}...')
            asyncio.run(main_pull())
        else:
            print(f'Avvio in corso, in ascolto sulla porta {port}.')
            print('Premere Ctrl+C per interrompere in qualsiasi momento.')
            # Avvia tramite asyncio il server TCP, in modo da poter gestire
            # multiple connessioni in entrata contemporaneamente.
            asyncio.run(main_push())

    except KeyboardInterrupt:
        exit(0)
