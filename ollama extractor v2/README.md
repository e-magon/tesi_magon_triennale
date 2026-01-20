# # Sensitive Data Detector v2

Script che chiama un modello personalizzato con ollama tramite le API REST ollama e cerca di estrarre tutti i dati privati presenti in un estratto dei log.

I modelli personalizzati sono:

1. sensitive-data-detector-llama3.1:8b
2. sensitive-data-detector-llama3.2:3b
3. sensitive-data-detector-mistral:7b
4. sensitive-data-detector-mistral-nemo:12b
5. sensitive-data-detector-qwen2.5:7b
6. sensitive-data-detector-gemma3:4b
7. sensitive-data-detector-gemma3:12b
8. sensitive-data-detector-deepseek-r1:7b
9. sensitive-data-detector-deepseek-r1:8b

## Installazione Ollama

```sh
# Installazione di ollama (macOS)
brew install homebrew/cask/ollama

# Installazione dei modelli
cd "ollama extractor v2"
ollama create sensitive-data-detector-llama3.1:8b -f ../modelfiles/sensitive-data-detector-llama3.1:8b.modelfile
ollama create sensitive-data-detector-llama3.2:3b -f ../modelfiles/sensitive-data-detector-llama3.2:3b.modelfile
ollama create sensitive-data-detector-mistral:7b -f ../modelfiles/sensitive-data-detector-mistral:7b.modelfile
ollama create sensitive-data-detector-mistral-nemo:12b -f ../modelfiles/sensitive-data-detector-mistral-nemo:12b.modelfile
ollama create sensitive-data-detector-qwen2.5:7b -f ../modelfiles/sensitive-data-detector-qwen2.5:7b.modelfile
ollama create sensitive-data-detector-gemma3:4b -f ../modelfiles/sensitive-data-detector-gemma3:4b.modelfile
ollama create sensitive-data-detector-gemma3:12b -f ../modelfiles/sensitive-data-detector-gemma3:12b.modelfile
ollama create sensitive-data-detector-deepseek-r1:7b -f ../modelfiles/sensitive-data-detector-deepseek-r1:7b.modelfile
ollama create sensitive-data-detector-deepseek-r1:8b -f ../modelfiles/sensitive-data-detector-deepseek-r1:8b.modelfile
```

Per selezionare il modello da utilizzare si possono usare due approcci:

1. Decommentare la relativa riga di codice nel file `main.py` (approccio statico)
2. Passare il nome del modello come argomento da riga di comando (approccio dinamico):

```sh
# Solo modello (usa il file di log di default)
python3 main.py sensitive-data-detector-mistral:7b

# Modello e file di log specifico
python3 main.py sensitive-data-detector-mistral:7b messages_1000.log
```

## Esecuzione dello script

```sh
# Creare il virtual environment (usare python 3.12)
python3 -m venv .venv

# Attivare il virtual environment
# bash:
source .venv/bin/activate
# fish:
source .venv/bin/activate.fish

# Installare le dipendenze
pip install -r requirements.txt

# Avviare del server ollama
ollama serve

# Avviare lo script
python3 main.py
```

## Esecuzione di tutti i test (tutti i modelli x tutti i log)

Lo script `test-all.sh` esegue automaticamente tutti i modelli custom su tutti i file di log di prova.

Per eseguirlo:

```sh
cd "ollama extractor v2"
chmod +x test-all.sh
./test-all.sh
```

Per ogni coppia modello/log:

- lancia `python3 main.py NOME_MODELLO NOME_FILE_LOG`
- utilizza `/usr/bin/time -p` per misurare il tempo di esecuzione
- inserisce una pausa di 60 secondi tra un test e il successivo, per evitare che il surriscaldamento della GPU influenzi i risultati successivi.

Tutti i risultati (metriche stampate da `main.py` più i tempi di esecuzione di `time`) vengono salvati in un file aggregato nella cartella `output` con nome del tipo:

- `output/test-all_YYYY-MM-DD_HH-MM-SS.txt`
