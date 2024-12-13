# Ollama test

Script che chiama un modello personalizzato con ollama (`llama3.1` con prompt personalizzato, `sensitive-data-extractor`)
tramite le API REST ollama e cerca di estrarre tutti i dati privati presenti in un estratto dei log.
Questa versione (v3) legge il file specificato come argomento.
Il file viene aperto come stream e letto riga per riga, quindi è possibile far analizzare
anche file di grandi dimensioni.

## Installazione Ollama

```sh
# Installazione di ollama (macOS)
brew install homebrew/cask/ollama

# Installazione dei modelli
ollama pull llama3.1
cd "ollama extractor v3"
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
python3 main.py <file da analizzare>
```
