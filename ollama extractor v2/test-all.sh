#!/usr/bin/env bash

# Script di test automatico per tutti i modelli custom
# e tutti i file di log di prova.
# Richiede che il server Ollama sia già in esecuzione.

# Imposta opzioni della shell: -e interrompe in caso di errore,
# -u segnala l'uso di variabili non inizializzate e -o pipefail fa
# fallire le pipeline se uno qualsiasi dei comandi fallisce.
set -euo pipefail


SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

RESULTS_DIR="output"
mkdir -p "${RESULTS_DIR}"

# Crea una cartella per questa sessione di test all'interno
# della cartella di output.
TIMESTAMP="$(date '+%Y-%m-%d_%H-%M-%S')"
TEST_RUN_DIR="${RESULTS_DIR}/test-all_${TIMESTAMP}"
mkdir -p "${TEST_RUN_DIR}"

# Tutti i modelli da testare
MODELS=(
  "sensitive-data-detector-llama3.1:8b"
  "sensitive-data-detector-llama3.2:3b"
  "sensitive-data-detector-mistral:7b"
  "sensitive-data-detector-mistral-nemo:12b"
  "sensitive-data-detector-qwen2.5:7b"
  "sensitive-data-detector-gemma3:4b"
  "sensitive-data-detector-gemma3:12b"
  "sensitive-data-detector-deepseek-r1:7b"
  "sensitive-data-detector-deepseek-r1:8b"
)

# Tutti i file di log di prova da usare
LOG_FILES=(
  "messages_100.log"
  "messages_200.log"
  "messages_1000.log"
)

echo "Salvataggio risultati in: ${TEST_RUN_DIR}"

for MODEL in "${MODELS[@]}"; do
  for LOG_FILE in "${LOG_FILES[@]}"; do
    # Crea un nome di file rimuovendo caratteri speciali
    MODEL_CLEAN="${MODEL//[:\/]/_}"
    LOG_CLEAN="${LOG_FILE%.log}"
    OUTPUT_FILE="${TEST_RUN_DIR}/${MODEL_CLEAN}_${LOG_CLEAN}.txt"

    echo "=== MODEL: ${MODEL} | LOG: ${LOG_FILE} ==="
    {
      echo "Test automatici Sensitive Data Detector v2"
      echo "MODEL: ${MODEL}"
      echo "LOG FILE: ${LOG_FILE}"
      echo "Data di inizio: $(date)"
      echo
      # Esegue il programma principale misurando il tempo di esecuzione.
      # Usa /usr/bin/time su macOS, "time" integrato nella shell su altri sistemi
      if [[ "$OSTYPE" == "darwin"* ]]; then
        /usr/bin/time -p python3 main.py "${MODEL}" "${LOG_FILE}"
      else
        time python3 main.py "${MODEL}" "${LOG_FILE}"
      fi
      echo
      echo "Fine esecuzione: $(date)"
    } > "${OUTPUT_FILE}" 2>&1

    # Per evitare rallentamenti durante l'esecuzione del modello successivo
    # dati dal surriscaldamento del sistema, lo script attende 60 secondi prima
    # di procedere con il prossimo LLM.
    echo "Pausa 60 secondi prima del prossimo test..."
    sleep 60
  done
done

echo "Tutti i test completati. Risultati salvati in: ${TEST_RUN_DIR}"
