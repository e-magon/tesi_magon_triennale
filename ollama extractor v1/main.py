'''
Script che chiama il modello llama3 (4.7 GB) tramite le API REST ollama e cerca di estrarre tutti i dati privati presenti
in un estratto dei log.
'''
import datetime
import os
import sys
import httpx
import ollama

# Numero di righe da aggiungere ad ogni "messaggio" della chat.
# 20 righe sono troppe, si perde la spiegazione a inizio prompt.
# Viene impostato successivamente in base al modello avviato.
n_righe_da_aggiungere_in_ogni_messaggio = None

# Numero di messaggi da inviare prima di cambiare chat.
# Serve per evitare di saturare la "memoria" (token) del modello.
# Dopo aver inviato `n_messaggi_prima_di_cambiare_chat` messaggi, la chat viene resettata e quindi
# riparte con il prompt iniziale.
# Mettere 0 per non cambiare mai chat.
# Viene impostato successivamente in base al modello avviato
n_messaggi_prima_di_cambiare_chat = None

avviato_timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
risposte_formattate = ''

llm = None

# log_filename = 'messages_100.log'
log_filename = 'messages_1000.log'

with open('./prompt.txt', 'r') as file:
    initial_prompt = file.read()


def main() -> None:
    # global in modo da poterle modificare
    global risposte_formattate
    global n_righe_da_aggiungere_in_ogni_messaggio
    global n_messaggi_prima_di_cambiare_chat
    global llm

    args = sys.argv

    # Se non ci sono argomenti errore
    if len(args) == 1:
        print('Errore: chiamare lo script specificando il modello da usare (llama3, llama3:70b, llama3.1, llama3.1:70b, command-r)')
        print('Esempio: python main.py llama3')
        sys.exit(1)

    if len(args) != 2:
        print('Errore: troppi argomenti')
        sys.exit(1)

    llm = args[1].lower().strip()

    # https://ollama.com/library/llama3
    # https://ollama.com/library/llama3:70b
    # https://ollama.com/library/llama3.1
    # https://ollama.com/library/llama3.1:70b
    # https://ollama.com/library/command-r
    if llm == 'llama3':
        n_righe_da_aggiungere_in_ogni_messaggio = 3
        n_messaggi_prima_di_cambiare_chat = 1
    elif llm == 'llama3:70b':
        n_righe_da_aggiungere_in_ogni_messaggio = 10
        n_messaggi_prima_di_cambiare_chat = 5
    elif llm == 'llama3.1':
        n_righe_da_aggiungere_in_ogni_messaggio = 3
        n_messaggi_prima_di_cambiare_chat = 1
    elif llm == 'llama3.1:70b':
        n_righe_da_aggiungere_in_ogni_messaggio = 10
        n_messaggi_prima_di_cambiare_chat = 5
    elif llm == 'command-r':
        n_righe_da_aggiungere_in_ogni_messaggio = 5
        n_messaggi_prima_di_cambiare_chat = 5
    else:
        print(f'Errore: modello non riconosciuto ({llm})')
        sys.exit(1)

    # Legge i log e li aggiunge al prompt
    n_righe_aggiunte = 0
    n_messaggi_inviati_chat_corrente = 0
    file_terminato = False
    prompt = initial_prompt
    messaggi = []

    with open(f'../example_logs/{log_filename}', 'r') as file:
        righe = file.readlines()

        while file_terminato is False:
            # Se è il momento di cambiare chat, resetta l'elenco dei messaggi
            if (
                n_messaggi_prima_di_cambiare_chat != 0 and  # type: ignore
                n_messaggi_inviati_chat_corrente == n_messaggi_prima_di_cambiare_chat
            ):
                print('\tRipristino chat, limite messaggi ({}) raggiunto\n'.format(
                    n_messaggi_prima_di_cambiare_chat
                ))
                n_messaggi_inviati_chat_corrente = 0
                prompt = initial_prompt
                messaggi = []

            righe_da_aggiungere = righe[n_righe_aggiunte:
                                        n_righe_aggiunte + n_righe_da_aggiungere_in_ogni_messaggio]
            if len(righe_da_aggiungere) < n_righe_da_aggiungere_in_ogni_messaggio:
                file_terminato = True

            prompt += ''.join(righe_da_aggiungere) + '```'
            n_righe_aggiunte += len(righe_da_aggiungere)

            messaggi.append({  # type: ignore
                'role': 'user',
                'content': prompt
            })

            try:
                risposta = ollama.chat(
                    model=llm, messages=messaggi)  # type: ignore
            except httpx.ConnectError as e:
                print(
                    'Errore: impossibile connettersi al server Ollama. Assicurarsi che sia attivo.')
                sys.exit(1)
            except Exception as e:
                print(e)
                sys.exit(1)

            risposta_formattata = risposta['message']['content'] + '\n\n\n' # type: ignore
            print(risposta_formattata)  # type: ignore
            print('\tRighe rimanenti: {}\n'.format(
                len(righe) - n_righe_aggiunte))
            risposte_formattate += risposta_formattata  # type: ignore

            messaggi.append(risposta['message'])  # type: ignore
            n_messaggi_inviati_chat_corrente += 1

            # Ripristina il prompt
            prompt = 'Log extract:\n```\n'

    salva_output()


def salva_output():
    # Scrive tutte le risposte formattate in un file
    # Crea la cartella `out` se non esiste
    try:
        os.mkdir('output')
    except FileExistsError:
        pass

    data_formattata = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    with open(f'output/{data_formattata}.txt', 'w') as file:
        file.write(f'+ Started: {avviato_timestamp} +\n')
        file.write(f'+ Model: {llm} +\n')
        file.write(f'+ Log file: {log_filename} +\n\n')
        file.write(f'+ Initial prompt: +\n')
        file.write(initial_prompt + '\n\n\n')
        file.write('+ LLM answers: +\n')
        file.write(risposte_formattate)

    print('\n\n\n***Output salvato***')


if __name__ == '__main__':
    try:
        print('Avvio in corso. Premere Ctrl+C per interrompere in qualsiasi momento, i risultati verranno salvati.')
        main()
    except KeyboardInterrupt:
        # Se l'utente interrompe il programma, salva l'output
        salva_output()
