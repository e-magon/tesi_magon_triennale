# Come compilare

Per compilare l'elaborato, installare **MacTeX** oppure **BasicTeX** (o i relativi pacchetti in base al sistema operativo).

Successivamente installare le dipendenze di LaTeX eseguendo questo comando (potrebbe essere necessario eseguirlo con `sudo`):

```sh
tlmgr install babel babel-italian csvsimple hyphen-italian geometry newfile currfile graphics etoolbox fp l3kernel l3packages setspace hologo listings url xcolor pdfx hyperref libertine inconsolata newtx pgf pgfplots todonotes xkeyval tools oberdiek filehook greek-fontenc xmpincl
```

Infine eseguire questo comando per ottenere l'elaborato in pdf:

```sh
latexmk -pdf -f tesi.tex
```
