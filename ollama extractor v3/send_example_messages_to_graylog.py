"""
Semplice script per inviare i messaggi di esempio a GrayLog,
in modo da testare tutto il flusso di analisi dei log.
"""
import socket
import time

log_filename = 'messages_100.log'
# log_filename = 'messages_200.log'
# log_filename = 'messages_1000.log'


def main() -> None:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 5555))

    with open(f'../example_logs/{log_filename}', 'r') as file:
        righe = file.readlines()
        for riga in righe:
            # Rimuove `N\t` e `Y\t` da inizio riga, usato negli
            # altri script per calcolare correttezza dell'LLM
            riga = riga.replace('N\t', '').replace('Y\t', '')
            print('Invio: ' + riga)

            msg = riga + '\x00'
            client.send(msg.encode('utf-8'))
            time.sleep(0.5)

    client.close()


if __name__ == '__main__':
    main()
