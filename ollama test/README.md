# Ollama test

Script che chiama il modello llama3 (4.7 GB) tramite le API REST ollama e cerca di estrarre tutti i dati privati presenti
in un estratto dei log.

```sh
# Installazione di ollama (macOS)
brew install homebrew/cask/ollama

# Installazione del modello llama3
ollama pull llama3

# Avvio del server ollama
ollama serve
```

**TODO** creare un modello personalizzato con un prompt iniziale adatto al questo caso d'uso ([Customize a prompt](https://github.com/ollama/ollama?tab=readme-ov-file#customize-a-prompt)).
