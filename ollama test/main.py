'''
Script che chiama il modello llama3 (4.7 GB) tramite le API REST ollama e cerca di estrarre tutti i dati privati presenti
in un estratto dei log.
'''
import datetime
import os
import ollama

# Numero di righe da aggiungere ad ogni "messaggio" della chat
# 20 righe sono troppe, si perde la spiegazione a inizio prompt
n_righe_da_aggiungere = 5
risposte_formattate = ''
log_filename = 'messages_100.log'
initial_prompt = '''
Here is an extract of logs from an application server. Every line is a log entry.
The logs contain private information that should not be exposed.
You have to extract all the data you deem to be private from the logs and provide it in a bullet list so that I will be able to make regexes to redact it.

Do not say any additional information and do not say what you think isn't private, just provide the structured data. Do not add extra information, just the structured data.

Try not to repeat the same data multiple times, just once per type of data.

Here's an example of what I expect:

Example:
```
    Log extract:
    Method set_result_command for thing_id 59f3a8c5-a405-47a4-a2e0-e39909deac69 took: 9.693563ms to complete without errors.
    Method create_token for user: admin@revetec.it took: 97.468142ms to complete without errors
    eneltecService, login success: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MTI0NzcxMDAsImlhdCI6MTcxMjQ0MTEwMCwiaXNzIjoibWFpbmZsdXguYXV0aCIsInN1YiI6ImFkbWluQHJldmV0ZWMuaXQiLCJpc3N1ZXJfaWQiOiI2MzNmZWRiYS1hOGE4LTRhOWUtOTU1MC0xODNlN2Y2YjBmMjkiLCJ0eXBlIjowfQ._fdS_wKnl9ARlFYc6KwbMCYSMgj0sbwcQzEZSYzttcI

    Expected output:
    - thing_id 59f3a8c5-a405-47a4-a2e0-e39909deac69
    - user admin@revetec.it
    - token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MTI0NzcxMDAsImlhdCI6MTcxMjQ0MTEwMCwiaXNzIjoibWFpbmZsdXguYXV0aCIsInN1YiI6ImFkbWluQHJldmV0ZWMuaXQiLCJpc3N1ZXJfaWQiOiI2MzNmZWRiYS1hOGE4LTRhOWUtOTU1MC0xODNlN2Y2YjBmMjkiLCJ0eXBlIjowfQ._fdS_wKnl9ARlFYc6Kw
    * ...rest of the private data *
```

Log extract:
```

'''


def main():
    global risposte_formattate # global in modo da poterla modificare

    # Legge i log e li aggiunge al prompt
    n_righe_aggiunte = 0
    file_terminato = False
    prompt = initial_prompt
    messaggi = []

    with open(f'logs/{log_filename}', 'r') as file:
        righe = file.readlines()
        while file_terminato is False:
            righe_da_aggiungere = righe[n_righe_aggiunte:
                                        n_righe_aggiunte + n_righe_da_aggiungere]
            if len(righe_da_aggiungere) < n_righe_da_aggiungere:
                file_terminato = True

            prompt += ''.join(righe_da_aggiungere)
            prompt += '```'
            n_righe_aggiunte += len(righe_da_aggiungere)

            messaggi.append({
                'role': 'user',
                'content': prompt
            })

            risposta = ollama.chat(model='llama3', messages=messaggi)

            risposta_formattata = risposta['message']['content'] + '\n\n\n'
            print(risposta_formattata)
            risposte_formattate += risposta_formattata

            messaggi.append(risposta['message'])

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
        file.write(f'File di log: {log_filename}\n')
        file.write(f'Prompt iniziale:\n')
        file.write(initial_prompt + '\n\n\n')
        file.write('Risposte:\n')
        file.write(risposte_formattate)

    print('\n\n\n***Output salvato***')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        salva_output()
