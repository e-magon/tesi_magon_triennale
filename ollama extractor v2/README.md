# Ollama test

Script che chiama un modello personalizzato con ollama (`llama3.1:8b` con prompt personalizzato, `sensitive-data-extractor`)
tramite le API REST ollama e cerca di estrarre tutti i dati privati presenti in un estratto dei log.

## Installazione Ollama

```sh
# Installazione di ollama (macOS)
brew install homebrew/cask/ollama

# Installazione dei modelli
ollama pull llama3.1
cd "ollama extractor v2"
ollama create sensitive-data-extractor -f Modelfile
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
