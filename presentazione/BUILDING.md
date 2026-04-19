# Come compilare

Per compilare la presentazione, installare **Typst**.

Su macOS (Homebrew):

```sh
brew install typst
```

Questa presentazione usa il pacchetto Typst **@preview/diatypst:0.9.1** (vedi `main.typ`).
Il pacchetto viene scaricato automaticamente al primo comando di compilazione.

Per compilare la presentazione in PDF:

```sh
typst compile --root "../" main.typ "../Presentazione Magon 909482.pdf"
```

## Opzionale: rigenerare le immagini dei grafici

Se si desidera rigenerare i grafici PNG usati nelle slide, usare lo script in `immagini/`.

Dipendenze richieste:
- `latexmk`
- `pdftocairo`

Su macOS (Homebrew), `pdftocairo` è disponibile tramite `poppler`:

```sh
brew install poppler
```

Per eseguire la rigenerazione:

```sh
cd immagini
./generate_chart_images.sh
```

Dopo la rigenerazione delle immagini, ricompilare la presentazione con Typst.
