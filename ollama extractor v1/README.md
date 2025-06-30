# # Sensitive Data Detector v1

Script che chiama un modello con ollama (`llama3`, `llama3:70b`, `llama3.1`, `llama3.1:70b` o `command-r`)
tramite le API REST ollama e cerca di estrarre tutti i dati privati presenti in un estratto dei log.

## Installazione Ollama

```sh
# Installazione di ollama (macOS)
brew install homebrew/cask/ollama

# Installazione dei modelli
ollama pull llama3
ollama pull llama3:70b
ollama pull llama3.1
ollama pull llama3.1:70b
ollama pull command-r
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

# Avviare lo script con il modello llama3
python main.py llama3
# o con il modello llama3:70b
python main.py llama3:70b
# o con il modello llama3.1
python main.py llama3.1
# o con il modello llama3.1:70b
python main.py llama3.1:70b
# o con il modello command-r
python main.py command-r
```
