__1. Ente presso cui è stato svolto il lavoro di stage__

Il tirocinio interno è stato svolto presso il Dipartimento di Informatica dell'Università degli Studi di Milano, sotto la supervisione del Prof. Marco Anisetti e del Dott. Antongiacomo Polimeno.

__2. Contesto iniziale__

Il contesto di partenza era caratterizzato dalla presenza di elevati volumi di log, generati da micro-servizi eterogenei appartenenti a una piattaforma di domotica e smart city, con formati e contenuti non uniformi. In tale scenario, i log possono contenere dati sensibili quali indirizzi email, token di autenticazione e coordinate geografiche, con conseguenti implicazioni in termini di tutela della privacy e di conformità normativa.

Nel contesto operativo considerato non era sempre possibile intervenire direttamente sul codice sorgente dei sistemi che producono i log; si è reso pertanto necessario progettare un sistema esterno in grado di analizzare automaticamente i messaggi e segnalare le occorrenze critiche.

__3. Obiettivi del lavoro__

Gli obiettivi prefissati all'avvio del lavoro erano i seguenti:

- progettare un sistema automatico per identificare dati sensibili nei log;
- bilanciare accuratezza e scalabilità, riducendo i falsi negativi;
- integrare la soluzione in un'infrastruttura di log management già in uso (Graylog);
- valutare in modo quantitativo l'efficacia dei Large Language Model su dataset annotati;
- produrre una base evolutiva riutilizzabile in ambiente di produzione.

__4. Descrizione lavoro svolto__

In una fase preliminare si è condotta un'analisi dello stato dell'arte riguardante strumenti e approcci esistenti per l'identificazione di dati sensibili nei log.

Il lavoro di sviluppo è stato condotto secondo un approccio iterativo e incrementale, articolato in tre versioni successive del sistema Sensitive Data Detector. Nel corso dello sviluppo sono stati inoltre confrontati diversi LLM su piattaforme hardware differenti (Apple M1 Max e AMD RX6950XT), valutando i compromessi tra tempi di inferenza e qualità del rilevamento.

La prima fase ha prodotto un proof-of-concept in modalità batch su file di log, finalizzato a validare la fattibilità dell'approccio basato su LLM. Ciò ha messo in evidenza i primi limiti pratici, con particolare riferimento alla scalabilità e alla misurabilità oggettiva delle prestazioni.

Nella seconda fase è stato introdotto un flusso di elaborazione riga per riga, con modelli personalizzati mediante Modelfile e un dataset corredato di ground truth. Questo ha consentito l'implementazione di un processo di valutazione automatica fondato su metriche di classificazione binaria (TP, TN, FP, FN) e su metriche derivate (accuracy, precision, specificity, recall).

Nella terza e ultima fase è stata realizzata l'integrazione con Graylog in modalità push (stream in tempo reale) e pull (batch incrementale), adottando programmazione asincrona e meccanismi di feedback verso la piattaforma di log management per la notifica dei rilevamenti.

__5. Tecnologie coinvolte__

Le principali tecnologie utilizzate nel corso dello stage sono le seguenti:

- Python 3.12 per logica applicativa, scripting e integrazione;
- librerie Python: ollama, asyncio, httpx, anyio, requests;
- Graylog per raccolta, stream, pipeline con espressioni regolari, output e API REST;
- protocollo GELF per lo scambio strutturato dei log;
- Ollama per l'esecuzione locale di modelli LLM;
- modelli LLM open weight personalizzati via Modelfile (llama3.1, llama3.2, mistral, mistral-nemo, qwen2.5, gemma3, deepseek-r1);
- Docker e Docker Compose per l'ambiente riproducibile di test e integrazione.

__6. Competenze e risultati raggiunti__

Quali risultati sono stati raggiunti rispetto agli obiettivi iniziali?

- È stato progettato e implementato un sistema ibrido con regex e LLM per l'identificazione di dati sensibili all'interno dei log.
- È stato dimostrato il percorso evolutivo da prototipo sperimentale a soluzione integrabile in un flusso operativo reale basato su Graylog.
- È stato introdotto un processo di valutazione quantitativa su dataset annotati, al fine di confrontare le prestazioni dei modelli in modo oggettivo.

Quali insegnamenti si possono trarre dall'esperienza effettuata?

- L'approccio ibrido consente di sfruttare la velocità e il determinismo delle espressioni regolari con la flessibilità semantica offerta dai modelli LLM.
- La qualità dei prompt e la configurazione del contesto esercitano un'influenza significativa sull'affidabilità del rilevamento.
- L'integrazione con i sistemi esistenti e la tracciabilità operativa rivestono un'importanza pari a quella dell'accuratezza del modello.

Quali i problemi incontrati? Quali risolti e quali no? Perché?

- Problema risolto: il limite di scalabilità della prima versione è stato superato mediante l'adozione di un'elaborazione riga per riga e di un'architettura asincrona.
- Problema risolto: l'assenza di metriche oggettive è stata affrontata introducendo un dataset con ground truth e un sistema di valutazione automatica nella seconda versione.
- Problema aperto: un adattamento più approfondito dei modelli al dominio specifico dei log, perseguibile in futuro mediante tecniche di fine-tuning dedicate (ad es. LoRA).

__7. Bibliografia significativa__

1. Ji, Y. et al. (2024). Adapting Large Language Models to Log Analysis with Interpretable Domain Knowledge. arXiv:2412.01377.
2. Beck, V. et al. (2025). System Log Parsing with Large Language Models: A Review. arXiv:2504.04877.
3. Karlsen, E. et al. (2023). Benchmarking Large Language Models for Log Analysis, Security, and Interpretation. arXiv:2311.14519.
4. Ma, Z. et al. (2024). LLMParser: An Exploratory Study on Using Large Language Models for Log Parsing. arXiv:2404.18001.
5. Kostina, A. et al. (2025). Large Language Models for Text Classification: Case Study and Comprehensive Review. arXiv:2501.08457.
6. Alassan, M. S. Y. et al. (2024). Comparison of Open-Source and Proprietary LLMs for Machine Reading Comprehension. arXiv:2406.13713.
7. White, C. et al. (2024). LiveBench: A Challenging, Contamination-Limited LLM Benchmark. arXiv:2406.19314.
