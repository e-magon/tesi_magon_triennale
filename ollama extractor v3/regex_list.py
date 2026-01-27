regex_list = [
    # Elenco di regex da applicare manualmente ai messaggi
    # di log per rilevare dati sensibili.
    # Serve solamente se si vuole eseguire l'analisi statica direttamente
    # nello script e non tramite GrayLog.
    {
        "name": "email_regex",
        "regex": r"[^\s@]+@[^\s@]+\.[^\s@]+",
    },
]
