#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

# Genera i grafici in formato PNG direttamente dai dati CSV usando pgfplots
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_dir"

tex_file="charts_from_csv.tex"
pdf_file="charts_from_csv.pdf"
output_dir="."

chart_names=(
  "accuratezza_amd"
  "precision_amd"
  "recall_amd"
  "specificity_amd"
  "tempo_amd"
  "accuratezza_m1"
  "precision_m1"
  "recall_m1"
  "specificity_m1"
  "tempo_m1"
)

if ! command -v latexmk >/dev/null 2>&1; then
  echo "latexmk non trovato nel PATH."
  exit 1
fi

if ! command -v pdftocairo >/dev/null 2>&1; then
  echo "pdftocairo non trovato nel PATH."
  exit 1
fi

# Compila il documento LaTeX e forza la rigenerazione per evitare stati di build obsoleti
if ! latexmk -g --pdf --interaction=nonstopmode --halt-on-error "$tex_file"; then
  echo "Compilazione LaTeX non riuscita."
  exit 1
fi

# Esporta ogni pagina del PDF in un file PNG
page=1
for chart_name in "${chart_names[@]}"; do
  if ! pdftocairo -png -singlefile -r 300 -f "$page" -l "$page" "$pdf_file" "$output_dir/$chart_name"; then
    echo "Esportazione della pagina $page in $chart_name.png non riuscita"
    exit 1
  fi

  page=$((page + 1))
done

# Rimuove i file di build di LaTeX
base_name="${tex_file%.tex}"
cleanup_files=(
  "${base_name}.aux"
  "${base_name}.fdb_latexmk"
  "${base_name}.fls"
  "${base_name}.log"
  "${base_name}.out"
  "${base_name}.synctex.gz"
  "${base_name}.toc"
  "${base_name}.pdf"
)

rm -f "${cleanup_files[@]}"

echo "File dei grafici generati in $script_dir:"
for chart_name in "${chart_names[@]}"; do
  echo "- $chart_name.png"
done

echo "File di build LaTeX rimossi per $base_name (mantenuto $tex_file)."
