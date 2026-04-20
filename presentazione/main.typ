#import "@preview/diatypst:0.9.1": *

#let presentation-title = "Sensitive Data Detector:\nIdentificazione automatica di dati sensibili all'interno di log"
#let presentation-subtitle = "Laurea triennale in Sicurezza dei Sistemi e delle Reti Informatiche"
#let presentation-date = "A.A. 2024-2025"
#let presentation-authors = "Emanuele Magon (matr. 909482)\nProf. Marco Anisetti, Dott. Antongiacomo Polimeno"
#let presentation-title-color = blue.darken(60%)

// Geometria usata da diatypst per il layout "small"
#let first-slide-space = 1.4cm
#let first-slide-height = 9cm
#let first-slide-width = (4 / 3) * first-slide-height

#set text(lang: "it")

// Regole dello stile di footnote
#show footnote.entry: set text(size: 8pt)

// Regole dello stile delle tabelle
#show table: set text(size: 9pt)
#show table: content => [
  #align(center)[
    #content
  ]
]

// Regole per le figure
#show figure: set text(size: 9pt)

// Disabilita l'underline per il link
#show underline: it => it.body

// Regole dello stile dei TODO
#let todo(body) = {
  place(
    top + right,
    dy: -7pt,
    dx: 20pt,
    text(size: 8pt, fill: red, weight: "bold", "TODO " + body),
  )
}

// Riduce di 1 il numero di pagine (per non contare quella dei ringraziamenti)
#counter(page).update(v => v - 1)

// Prima slide: clonata dalla title slide di default di diatypst, con logo in overlay
#set page(
  footer: none,
  header: none,
  margin: 0cm,
  width: first-slide-width,
  height: first-slide-height,
)

#block(
  inset: (x: 0.5 * first-slide-space, y: 1em),
  fill: presentation-title-color,
  width: 100%,
  height: 60%,
  align(bottom)[#text(2.0em, weight: "bold", fill: white, presentation-title)],
)

#block(
  height: 33%,
  width: 100%,
  inset: (x: 0.5 * first-slide-space, top: 0cm, bottom: 1em),
  if presentation-subtitle != none {
    [
      #text(1.4em, fill: presentation-title-color, weight: "bold", presentation-subtitle)
    ]
  }
    + if presentation-subtitle != none and presentation-date != none { text(1.4em)[ \ ] }
    + if presentation-date != none { text(1.1em, presentation-date) }
    + align(left + bottom, presentation-authors),
)

#place(
  top + right,
  dx: -0.1cm,
  dy: 0.1cm,
  image("immagini/unimi_transparent.png", width: 180pt),
)

#show: slides.with(
  title: presentation-title,
  subtitle: presentation-subtitle,
  date: presentation-date,
  authors: presentation-authors,

  layout: "small",
  theme: "full",
  title-color: presentation-title-color,
  toc: false,
  count: "number",
  footer-title: "Sensitive Data Detector",
  footer-subtitle: "Emanuele Magon",
  first-slide: false,
)

= Introduzione

== Contesto e obiettivo

- *Log*: registrazioni cronologiche che tracciano eventi, operazioni e stati interni dei sistemi informatici

- Spesso contengono dati sensibili (_Personal Identifiable Information_, PII), diventando bersaglio di *fughe e sottrazioni di dati*#footnote[_Samira Aghili et al. Protecting privacy in software logs: What should be anonymized?, 2024_]

- Circa il *6%* delle app Android espone dati personali nei log e circa l'*81%* delle app pre-installate legge i log di sistema#footnote[_Chenxi Hou et al. Catamaran: User privacy violation detection in mobile logging, 2025_]

- *Rischi significativi* per la privacy degli utenti e la sicurezza dei sistemi

#pagebreak()

- *Contesto*: piattaforma IoT di servizi _smart city_ →~micro-servizi eterogenei che generano grandi volumi di log

- Presenza occasionale di *dati sensibili* in forme strutturate e non (PII, credenziali, token di accesso, coordinate geografiche e simili)

- Componenti di *terze parti* →~impossibile intervenire sul codice sorgente per mitigare il problema alla fonte

#v(16pt)

*Obiettivo*: sviluppare _Sensitive Data Detector_, un sistema *automatico*, *scalabile* e *integrato con il sistema di log management* per il rilevamento di dati sensibili nei log

= Stato dell'arte

== Stato dell'arte: Analisi dei log

#table(
  columns: (auto, auto),
  inset: 5pt,
  align: (left, left),
  table.header([*Strumento*], [*Limite principale*]),
  [Microsoft Presidio], [Non specializzato per flussi continui di log],
  [anonympy], [Solo documenti strutturati, pre-elaborazione necessaria],
  [Data Protection Framework], [Incompleto, orientato a dati tabellari],
  [NgAnonymize], [Nessun rilevamento automatico],
  [ARX], [Orientato a dati tabellari],
  [LogAnalyzer], [Analisi manuale tramite GUI, no API],
  [logredactor], [Solo durante generazione, pattern predefiniti],
)

Nessuna di queste soluzioni combina *analisi sintattica* + *analisi semantica* + *integrazione con sistema di log management*

== Stato dell'arte: LLM

- *Large Language Models*: modelli AI basati su architettura *Transformer* con meccanismi di *self-attention* →~migliore comprensione contestuale del testo rispetto ad altri sistemi di Natural Language Processing

- *Modelli proprietari* (OpenAI, Anthropic, Google) vs *open weight* (esecuzione locale):
  - Open weight: *privacy*, *costi ridotti*, *no dipendenze* da servizi cloud
  - Proprietari: *context window*#footnote[Quantità di testo elaborabile in una singola interazione] e numero di *parametri*#footnote[Numero di connessioni neurali] generalmente superiori rispetto a modelli open weight →~maggiore comprensione e accuratezza

#figure(
  image("../elaborato/immagini/white2024livebench-1.png", height: 96%),
  caption: [Confronto performance su LiveBench: proprietari vs open weight],
)

= Architettura e tecnologie

== Approccio ibrido: Regex & LLM

#grid(
  columns: (1fr, 1fr),
  gutter: 16pt,
  [
    *Layer 1: Analisi sintattica*
    - Espressioni regolari
    - Pattern: email, CF, JWT, coordinate
    - Veloce e deterministico
  ],
  [
    *Layer 2: Analisi semantica*
    - Large Language Model
    - Log non strutturati e formati non convenzionali
    - Flessibile e contestuale
  ],
)

*Vantaggi*:
- *Copertura completa*: dati strutturati + non strutturati
- *Riduzione dei falsi negativi*: l'LLM cattura ciò che sfugge alle regex
- *Adattabilità*: bilanciamento tra velocità e accuratezza
- *Evoluzione continua*: nuovi pattern identificati dall'LLM →~nuove regex

== Stack tecnologico

#text(
  size: 9pt,
  grid(
    columns: (1fr, 1fr),
    gutter: 16pt,
    [
      *Graylog*:
      - Log management
      - L1: Sintassi (regex)

      *Docker*:
      - Container Graylog (+~MongoDB e datanode)
    ],
    [
      *Ollama*:
      - API REST, Modelfile
      - L2: Semantica (LLM open weight)

      *Python 3.12*:
      - Codifica del progetto
      - lib: `asyncio`, `ollama`, `httpx`
    ],
  ),
)

#text(size: 9pt)[*LLM utilizzati*:]

#table(
  columns: (auto, auto, auto),
  inset: 4pt,
  align: (left, center, left),
  table.header([*Modello*], [*Num. di parametri*], [*Caratteristiche*]),
  [Llama 3.1 / 3.2], [8B / 3B], [Modelli generali],
  [Mistral / Nemo], [7B / 12B], [Mixture of Experts],
  [Qwen 2.5], [7B], [Multilingue],
  [Gemma 3], [4B / 12B], [Ottimizzati per task specifici],
  [DeepSeek R1], [7B / 8B], [Reasoning avanzato],
)

= Sensitive Data Detector

== V1: Proof of Concept

*Obiettivo*: valutare la *fattibilità* dell'uso di LLM open weight per rilevare dati sensibili

- Elaborazione *batch* di file di log pre-esistenti
- LLM base senza personalizzazioni, guidato da _user prompt_#footnote[Istruzioni iniziali fornite al modello all'inizio di ogni sessione]
- Gestione del *context window*: segmentazione delle righe + ripristino periodico della sessione in base al modello usato
- 2 modelli testati: Llama3 8B, Llama3.1 8B
- Output su file per analisi successiva

*Limitazioni*: gestione del context window fragile, nessuna integrazione real-time, nessuna metrica formale

== V2: Valutazione quantitativa

#text(size: 10pt)[
  *Obiettivo*: metriche formali e modelli personalizzati

  - Elaborazione *riga per riga* →~gestione più robusta del context window
  - Personalizzazione tramite *Modelfile* (_system prompt_#footnote[Istruzioni globali che guidano il comportamento del modello], temperatura#footnote[Regola la variabilità delle risposte del modello]...) →~modelli più performanti
  - *Ground truth* per la valutazione dei risultati: file di log annotati, per ogni riga viene indicata la presenza (o meno) di dati sensibili
  - Metriche _TP_/_TN_, _FP_/_FN_ →~*accuracy*, *precision*, *specificity*, *recall*
  - 9 modelli testati (con personalizzazioni): Llama 3.1/3.2, Mistral Nemo 7B/12B, Qwen 2.5, Gemma 3 4B/12B, DeepSeek R1 7B/8B

  *Limitazioni*: nessuna integrazione real-time, dataset pre-annotati
]

== V3: Integrazione con Graylog

*Obiettivo*: soluzione _production-ready_ con integrazione Graylog

- *Analisi sintattica*: utilizzo regex tramite le pipeline di Graylog
- *Analisi semantica*, con due modalità di funzionamento:
  - *Push*: stream real-time\
    #text(size: 8pt)[
      Log~→~*Graylog*~→~`TCP 24367`~→~*SDD*~→~`TCP 5556`~→~*Graylog*
    ]
  - *Pull*: acquisizione incrementale in batch via API di Graylog\
    #text(size: 8pt)[
      Log~→~*Graylog*~↔~`API REST`~←~*SDD*~→~`TCP 5556`~→~*Graylog*
    ]
- Architettura *asincrona* (`asyncio`) per gestione concorrente
- *Feedback loop*: risultati inviati a Graylog per consentirne il monitoraggio
- Stessi 9 modelli personalizzati da Modelfile della V2

= Test e risultati\ (SDD V2)

== Metodologia e metriche

- *Hardware di test*:
  - *Apple M1 Max*: 32 GB memoria unificata, 32 GPU Core
  - *AMD RX6950XT*: 16 GB VRAM, 80 Compute Unit

- *Dataset*: log annotati manualmente con etichette binarie (non fornite al modello) indicanti la presenza di dati sensibili

#table(
  columns: (auto, auto, auto),
  inset: 4pt,
  align: (left, left, left),
  table.header([*Metrica*], [*Formula*], [*Significato*]),
  [_Accuracy_], [$("TP" + "TN") / "Totale"$], [% classificazioni corrette],
  [_Precision_], [$"TP" / ("TP" + "FP")$], [% segnalati realmente positivi],
  [_Specificity_], [$"TN" / ("TN" + "FP")$], [% negativi correttamente ignorati],
  [_Recall_], [$"TP" / ("TP" + "FN")$], [% positivi correttamente segnalati],
)

- *Recall* è la metrica più critica (falsi negativi = rischio sicurezza), ma anche *Precision* è essenziale (falsi positivi = inefficienza)

== Risultati sperimentali

*AMD RX6950XT, dataset: 1000 righe di log pre-annotate*

#table(
  columns: (auto, auto, auto, auto, auto, auto),
  inset: 3pt,
  align: (left, center, center, center, center, right),
  table.header([*Modello*], [*Accuracy*], [*Precision*], [*Specificity*], [*Recall*], [*Tempo*]),
  [*gemma3:12b*], [*93%*], [*77%*], [*94%*], [86%], [12m 28s],
  [qwen2.5:7b], [84%], [54%], [80%], [*98%*], [24m 43s],
  [gemma3:4b], [85%], [56%], [86%], [79%], [7m 35s],
  [deepseek-r1:8b], [85%], [57%], [86%], [80%], [405m 14s],
  [llama3.1:8b], [83%], [54%], [88%], [66%], [7m 29s],
  [llama3.2:3b], [72%], [39%], [68%], [90%], [*7m 14s*],
  [mistral-nemo:12b], [70%], [34%], [71%], [67%], [17m 27s],
  [deepseek-r1:7b], [62%], [26%], [63%], [57%], [365m 17s],
  [mistral:7b], [40%], [23%], [27%], [97%], [21m 43s],
)

Risultati simili su *Apple M1 Max*, con tempi di elaborazione superiori (circa +85%)

== Analisi comparativa

#figure(
  image("immagini/accuratezza_amd.png", height: 98%),
  caption: [_Accuracy_ per modello, AMD RX6950XT],
)
#figure(
  image("immagini/precision_amd.png", height: 98%),
  caption: [_Precision_ per modello, AMD RX6950XT],
)
#figure(
  image("immagini/specificity_amd.png", height: 98%),
  caption: [_Specificity_ per modello, AMD RX6950XT],
)
#figure(
  image("immagini/recall_amd.png", height: 98%),
  caption: [_Recall_ per modello, AMD RX6950XT],
)

= Conclusioni

== Risultati raggiunti

- L'architettura ibrida *regex + LLM* è *efficace* per rilevare dati sensibili in log eterogenei
  - L'analisi sintattica (regex) è rapida e deterministica
  - L'analisi semantica (LLM) cattura pattern complessi

#v(8pt)

- Sviluppo *rapido* tramite approccio *progressivo*:
  - PoC →~valutazione quantitativa →~uso in produzione

#v(8pt)

- Integrazione completa con *Graylog*
  - Modalità push (stream) e modalità pull (batch)
  - Feedback loop per monitoraggio in tempo reale dei risultati

== Sviluppi futuri

*Addestramento LoRA*
- Fine-tuning specifico per il dominio dei log
- Partenza dal modello migliore e dai dati raccolti in produzione
- Adattamento più profondo rispetto ai soli Modelfile

*Integrazione con altre piattaforme*
- Definizione di un protocollo standard per adattatori modulari
- Elasticsearch, Splunk, Fluentd, SigNoz, ecc.
- Riduzione della complessità di rilascio in ambienti di produzione, potendo adattare SDD a sistemi di log management già in uso

// Ripristina lo stile della prima slide
#set page(
  footer: none,
  header: none,
  margin: 0cm,
  width: first-slide-width,
  height: first-slide-height,
)

==

#block(
  inset: (x: 0.5 * first-slide-space, y: 1em),
  fill: presentation-title-color,
  width: 100%,
  height: 50%,
  align(bottom)[#text(2.0em, weight: "bold", fill: white, "Fine")],
)

#block(
  height: 35%,
  width: 100%,
  inset: (x: 0.5 * first-slide-space, top: 0cm, bottom: 1em),
  if presentation-subtitle != none and presentation-date != none { text(1.4em)[ \ ] } + align(left + bottom)[
  #align(center)[*Grazie per l'attenzione*]
  #v(4pt)
  L'elaborato completo, il codice e la presentazione sono disponibili su GitHub:
  #v(4pt)
  #text(fill: blue)[https://github.com/e-magon/tesi_magon_triennale]
  ]
)

#place(
  top + right,
  dx: -0.1cm,
  dy: 0.1cm,
  image("immagini/unimi_transparent.png", width: 180pt),
)
