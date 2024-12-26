'''
Script che chiama il modello llama3 (4.7 GB) tramite le API REST ollama e cerca
di estrarre tutti i dati privati presenti in un estratto dei log.
Questa versione (v3) accetta come argomento il path del file di log da analizzare.
Il file viene aperto come stream e letto riga per riga, quindi è possibile far analizzare
anche file di grandi dimensioni.
'''
import sys
import httpx
import ollama

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

num_righe = None


def main() -> None:
    global n_messaggi_prima_di_cambiare_chat
    global llm
    global num_righe

    # Legge i log e li aggiunge al prompt
    n_righe_aggiunte = 0
    n_messaggi_inviati_chat_corrente = 0
    messaggi = []

    with open(log_filename, 'r') as file:
        for line_number, riga in enumerate(file, start=1):
            # Se è il momento di cambiare chat, resetta l'elenco dei messaggi
            if (
                n_messaggi_prima_di_cambiare_chat != 0 and
                n_messaggi_inviati_chat_corrente == n_messaggi_prima_di_cambiare_chat
            ):
                # print('\tRipristino chat, limite messaggi ({}) raggiunto\n'.format(
                #     n_messaggi_prima_di_cambiare_chat
                # ))
                n_messaggi_inviati_chat_corrente = 0
                messaggi = []

            n_righe_aggiunte += 1

            messaggi.append({  # type: ignore
                'role': 'user',
                'content': riga
            })

            try:
                response = ollama.chat(
                    model=llm,
                    messages=messaggi  # type: ignore
                )
            except httpx.ConnectError as e:
                print(
                    'Errore: impossibile connettersi al server Ollama. Assicurarsi che sia attivo.')
                sys.exit(1)
            except Exception as e:
                print(e)
                sys.exit(1)

            risposta: str = response['message']['content']  # type: ignore
            if risposta.lower().strip() != 'none':  # type: ignore
                # type: ignore
                print('Riga {}: {}'.format(line_number, risposta))  # type: ignore

            messaggi.append(response['message'])  # type: ignore
            n_messaggi_inviati_chat_corrente += 1


if __name__ == '__main__':
    try:
        if len(sys.argv) < 2:
            print('Specificare il nome del file di log da analizzare')
            sys.exit(1)

        log_filename = sys.argv[1]
        print(f'Avvio in corso. Lettura del file {
              log_filename}. Premere Ctrl+C per interrompere in qualsiasi momento.')
        main()
    except KeyboardInterrupt:
        exit(0)
