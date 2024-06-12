# Tesi Triennale Emanuele Magon, SSRI, Unimi

## Analisi automatica di file di log per la rilevazione di dati sensibili/privati

### Strumenti di analisi e anonimizzazione di log

| Strumento                                                                        | Descrizione                                                                                                                                | Pro                                                                                                                                                                                                           | Contro                                                                                                                                                                                                                                              |
| -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Presidio](https://microsoft.github.io/presidio/)                                | SDK per la protezione e anonimizzazione di dati privati in testi e immagini. Funziona tramite regex e NLP                                  | Ha il supporto alla ricerca tramite NLP e quindi dovrebbe essere più facile trovare dati non perfettamente rappresentabili con regex                                                                          | Lavorando con NLP potrebbe generare falsi negativi e falsi positivi                                                                                                                                                                                 |
| [anonympy](https://pypi.org/project/anonympy/)                                   | Libreria python per l'anonimizzazione di dati in tabelle, immagini e PDF                                                                   | È una libreria e quindi si può integrare facilmente in software custom                                                                                                                                        | Non è fatto per lavorare su testi semplici, anche se si potrebbe provare a modificare l'elaborazione dei PDF per renderlo possibile                                                                                                                 |
| [Data Protection Framework](https://github.com/thoughtworks-datakind/anonymizer) | Strumento molto simile a Microsoft Presidio, è una libreria Python che permette di trovare e anonimizzare dati privati tramite regex e NLP | Libreria FOSS integrabile in software custom oppure richiamabile direttamente da linea di comando                                                                                                             | Il progetto non è completo, mancano ancora alcuni detector                                                                                                                                                                                          |
| [NgAnonymize](https://github.com/sonbachmi/NgAnonymize)                          | Libreria Angular per anonimizzare dati                                                                                                     | Supporta diversi metodo per anonimizzare i dati                                                                                                                                                               | I dati da anonimizzare devono essere specificati singolarmente, non ha alcuna feature di rilevamento dei dati da anonimizzare                                                                                                                       |
| [arx-deidentifier](https://arx.deidentifier.org/)                                | OSS per l'anonimizzazione di dati personali                                                                                                | FOSS offerto sia come sw completo che libreria Java. È stato sviluppato come ricerca universitaria e ha paper associati                                                                                       | Supporta solo dati tabulari                                                                                                                                                                                                                         |
| [loganalyzer](https://github.com/pbek/loganalyzer)                               | FOSS software che trova e rimuove pattern pre-definiti da file di log                                                                      | Permette sia di rimuovere dati che di riportarli in un report, aiutando quindi la compilazione di un "punteggio" di sicurezza dei log. Scritto in C e quindi più veloce delle alternative in Angular o Python | Scritto in C, quindi il codice è più difficile da modificare. Non sembra essere offerto come libreria, quindi difficilmente integrabile in altri SW. Supporta solo ambienti grafici QT quindi la compilazione potrebbe dare problemi in base all'OS |
| [logredactor](https://pypi.org/project/logredactor/)                             | Libreria python che trova e rimuove pattern pre-definiti da file json                                                                      | Scritta in Python e quindi codice più facile da modificare                                                                                                                                                    | Supporta principalmente log in JSON quindi potrebbe essere necessaria qualche trasformazione sui log prima dell'elaborazione                                                                                                                        |

### Strumenti di raccoglimento e trattamento di log alternativi a [Graylog](https://graylog.org/)

| Strumento                                   | Descrizione                                                                           |
| ------------------------------------------- | ------------------------------------------------------------------------------------- |
| [SigNoz](https://signoz.io/)                | Pannello per visualizzare traces, metriche e log di OpenTelemetry                     |
| [Logstash](https://www.elastic.co/logstash) | Pipeline di data processing che permette di trasformare log in ingresso               |
| [FluentD](https://www.fluentd.org/)         | Data collector da multiple sorgenti, OSS, supporta plugin                             |
| [Syslog-ng](https://www.syslog-ng.com/)     | Implementazione FOSS di syslog, raccoglie, elabora e salva log da multiple sorgenti   |
| [Apache Flume](https://flume.apache.org/)   | Servizio per raccoglimento, aggregazione e spostamento di log. Basato su data streams |

### Elaborare i log in ingresso in Graylog

[Pipelines in Graylog](https://go2docs.graylog.org/5-0/making_sense_of_your_log_data/pipelines.html)

- Tramite le pipeline di Graylog si possono elaborare i log in ingresso per anonimizzare i dati sensibili o effettuare altre operazioni
- Esempio

```graylog
pipeline "Pipeline di test"
stage 1 match either
  rule "contiene password";
  rule "contiene username";
  rule "...";
end
```

- Dove la regola "contiene password" potrebbe essere

```graylog
rule "contiene password"
when
  contains(to_string($message.message), "password")
then
  set_field("message", replace(to_string($message.message), "password", "****"));
end
```
