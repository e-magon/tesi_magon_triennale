'''
Script che chiama il modello llama3.1:3b (4.7 GB) tramite le API REST ollama e cerca
di estrarre tutti i dati privati presenti in un estratto dei log.
'''
import datetime
import os
import re
import sys
import httpx
import ollama

# Numero di messaggi da inviare prima di cambiare chat.
# Serve per evitare di saturare la "memoria" (token) del modello.
# Dopo aver inviato `n_messaggi_prima_di_cambiare_chat` messaggi, la chat
# viene resettata e quindi riparte.
# Mettere 0 per non cambiare mai chat.
n_messaggi_prima_di_cambiare_chat = 15

avviato_timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
risposte_formattate = ''

# llm = 'sensitive-data-extractor-llama3.1:8b'
# llm = 'sensitive-data-extractor-llama3.2:3b'
# llm = 'sensitive-data-extractor-mistral:7b'
# llm = 'sensitive-data-extractor-mistral-nemo:12b'
# llm = 'sensitive-data-extractor-qwen2.5:7b'
# llm = 'sensitive-data-extractor-gemma3:4b'
llm = 'sensitive-data-extractor-gemma3:12b'
# llm = 'sensitive-data-extractor-deepseek-r1:7b'
# llm = 'sensitive-data-extractor-deepseek-r1:8b'

log_filename = 'messages_100.log'
# log_filename = 'messages_200.log'
# log_filename = 'messages_1000.log'

num_righe = None
veri_negativi = None
veri_negativi_p = None
veri_positivi = None
veri_positivi_p = None
falsi_negativi = None
falsi_negativi_p = None
falsi_positivi = None
falsi_positivi_p = None
risposte_corrette = None
risposte_corrette_p = None
risposte_errate = None
risposte_errate_p = None


def main() -> None:
    global risposte_formattate
    global n_messaggi_prima_di_cambiare_chat
    global llm
    global num_righe
    global veri_negativi
    global veri_negativi_p
    global veri_positivi
    global veri_positivi_p
    global falsi_negativi
    global falsi_negativi_p
    global falsi_positivi
    global falsi_positivi_p
    global risposte_corrette
    global risposte_corrette_p
    global risposte_errate
    global risposte_errate_p

    # Legge i log e li aggiunge al prompt
    n_righe_aggiunte = 0
    n_messaggi_inviati_chat_corrente = 0
    prompt = ''
    messaggi = []

    with open(f'../example_logs/{log_filename}', 'r') as file:
        veri_negativi = 0
        veri_positivi = 0
        falsi_negativi = 0
        falsi_positivi = 0

        righe = file.readlines()
        num_righe = len(righe)

        while True:
            # Se è il momento di cambiare chat, resetta l'elenco dei messaggi
            if (
                n_messaggi_prima_di_cambiare_chat != 0 and  # type: ignore
                n_messaggi_inviati_chat_corrente == n_messaggi_prima_di_cambiare_chat
            ):
                print('\tRipristino chat, limite messaggi ({}) raggiunto\n'.format(
                    n_messaggi_prima_di_cambiare_chat
                ))
                n_messaggi_inviati_chat_corrente = 0
                prompt = ''
                messaggi = []

            righe_da_aggiungere = righe[n_righe_aggiunte: n_righe_aggiunte + 1]
            if len(righe_da_aggiungere) == 0:
                # Finito il file
                break

            # Toglie la Y o N a inizio messaggio (che indica se la riga contiene dati sensibili,
            # usata per misurare la correttezza del modello)
            riga = righe_da_aggiungere[0]
            riga_sensibile = riga.startswith('Y\t')

            riga = riga.replace('Y\t', f'').replace('N\t', f'')
            prompt += riga
            n_righe_aggiunte += 1

            messaggi.append({  # type: ignore
                'role': 'user',
                'content': prompt
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
            risposta_formattata: str = risposta + '\n\n'  # type: ignore
            print(risposta_formattata)  # type: ignore

            # Elimina i tag <think>, </think> e tutto ciò che è contenuto in mezzo
            risposta = re.sub(r'<think>.*?</think>', '', risposta)
            risposta = risposta.strip()

            # Controlla la correttezza della risposta del modello
            riga_segnalata = not risposta.lower().startswith("none")  # type: ignore
            # 1. Se la riga non contiene dati sensibili (inizia con N) e il modello non l'ha segnalata come sensibile,
            # aggiunge 1 a veri_negativi
            if not riga_sensibile and not riga_segnalata:
                veri_negativi += 1
                print(f'\tRisposta corretta. Veri negativi totali {
                      veri_negativi}')
            # 2. Se la riga contiene dati sensibili (inizia con Y) e il modello l'ha segnalata come sensibile,
            # aggiunge 1 a veri_positivi
            elif riga_sensibile and riga_segnalata:
                veri_positivi += 1
                print(f'\tRisposta corretta. Veri positivi totali {
                      veri_positivi}')
            # 3. Se la riga non contiene dati sensibili (inizia con N) e il modello l'ha segnalata come sensibile,
            # aggiunge 1 a falsi_positivi
            elif not riga_sensibile and riga_segnalata:
                falsi_positivi += 1
                print(f'\tRisposta errata. Falsi positivi totali {
                      falsi_positivi}')
            # 4. Se la riga contiene dati sensibili (inizia con Y) e il modello non l'ha segnalata come sensibile,
            # aggiunge 1 a falsi_negativi
            elif riga_sensibile and not riga_segnalata:
                falsi_negativi += 1
                print(f'\tRisposta errata. Falsi negativi totali {
                      falsi_negativi}')

            print('\tRighe rimanenti: {}\n'.format(
                len(righe) - n_righe_aggiunte))
            risposte_formattate += risposta_formattata  # type: ignore

            messaggi.append(response['message'])  # type: ignore
            n_messaggi_inviati_chat_corrente += 1

            # Ripristina il prompt
            prompt = '\n'

        risposte_corrette = veri_negativi + veri_positivi
        risposte_errate = falsi_negativi + falsi_positivi

        # :.3f serve per arrotondare a 3 cifre decimali
        veri_negativi_p = f"{veri_negativi / num_righe * 100:.3f}"
        veri_positivi_p = f"{veri_positivi / num_righe * 100:.3f}"
        falsi_negativi_p = f"{falsi_negativi / num_righe * 100:.3f}"
        falsi_positivi_p = f"{falsi_positivi / num_righe * 100:.3f}"

        risposte_corrette_p = f"{risposte_corrette / num_righe * 100:.3f}"
        risposte_errate_p = f"{risposte_errate / num_righe * 100:.3f}"

        print(
            f'Su un totale di {num_righe} righe, il modello ha riportato:\n'
        )
        print(f'{veri_negativi} veri negativi ({veri_negativi_p}%)')
        print(f'{veri_positivi} veri positivi ({veri_positivi_p}%)')
        print(f'{falsi_negativi} falsi negativi ({falsi_negativi_p}%)')
        print(f'{falsi_positivi} falsi positivi ({falsi_positivi_p}%)')

        print('Totale risposte corrette: '
              + f'{risposte_corrette} ({risposte_corrette_p}%)')
        print('Totale risposte errate: '
              + f'{risposte_errate} ({risposte_errate_p}%)')

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
        file.write(f'+ Log file: {log_filename} +\n')
        file.write(f'+ Analyzed lines: {num_righe} +\n')
        file.write(f'+ True negatives: {veri_negativi} ({veri_negativi_p}%) +\n')
        file.write(f'+ True positives: {veri_positivi} ({veri_positivi_p}%) +\n')
        file.write(f'+ False negatives: {falsi_negativi} ({falsi_negativi_p}%) +\n')
        file.write(f'+ False positives: {falsi_positivi} ({falsi_positivi_p}%) +\n')
        file.write(f'+ Correct answers: {risposte_corrette} ({risposte_corrette_p}%) +\n')
        file.write(f'+ Wrong answers: {risposte_errate} ({risposte_errate_p}%) +\n')

        file.write('\n+ LLM answers: +\n')
        file.write(risposte_formattate)

    print('\n\n\n***Output salvato***')


if __name__ == '__main__':
    try:
        print('Avvio in corso. Premere Ctrl+C per interrompere in qualsiasi momento, i risultati verranno salvati.')
        print('Modello: ' + llm)
        main()
    except KeyboardInterrupt:
        # Se l'utente interrompe il programma, salva l'output
        salva_output()
