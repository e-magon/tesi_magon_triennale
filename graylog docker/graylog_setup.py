#!/usr/bin/env python3
'''
Script per automatizzare la configurazione di Graylog usando le API REST.
Questo script:
1. Crea input TCP per l'acquisizione dei log
2. Crea stream per l'elaborazione
3. Crea regole pipeline per il matching delle regex
4. Collega tutti i componenti tra loro
'''

import requests
import time
import sys
from typing import Dict, Any

# Configurazione
GRAYLOG_URL = 'http://localhost:9000/api'
USERNAME = 'admin'
PASSWORD = 'admin'

class GraylogSetup:
    def __init__(self):
        self.session = requests.Session()
        self.session.auth = (USERNAME, PASSWORD)
        self.session.headers.update({'X-Requested-By': 'Python Script'})

        # Memorizza gli ID delle risorse create
        self.input_ids = {}
        self.stream_ids = {}
        self.rule_ids = {}
        self.pipeline_id = None

    def create_input(self, title: str, port: int) -> str:
        """Crea un input TCP"""
        url = f'{GRAYLOG_URL}/system/inputs'

        data = {
            'title': title,
            'type': 'org.graylog2.inputs.raw.tcp.RawTCPInput',
            'global': True,
            'configuration': {
                'bind_address': '0.0.0.0',
                'port': port,
                'recv_buffer_size': 1048576,
                'tcp_keepalive': False,
                'tls_cert_file': '',
                'tls_enable': False,
                'tls_key_file': '',
                'tls_key_password': '',
                'use_null_delimiter': True,
                'max_message_size': 2097152,
                'number_worker_threads': 2,
            }
        }

        response = self.session.post(url, json=data)
        response.raise_for_status()

        input_id = response.json()['id']
        self.input_ids[title] = input_id
        print(f'Creato input {title} con ID {input_id}')
        return input_id

    def get_default_index_set_id(self) -> str:
        """Ottiene l'ID dell'index set predefinito"""
        url = f'{GRAYLOG_URL}/system/indices/index_sets'
        response = self.session.get(url)
        response.raise_for_status()

        index_sets = response.json()['index_sets']
        default_index_set = next(
            (index_set for index_set in index_sets if index_set['default']),
            None
        )

        if not default_index_set:
            raise Exception('Nessun index set predefinito trovato')

        return default_index_set['id']

    def create_stream(self, title: str, description: str, matching_input_id: str) -> str:
        """Crea uno stream con una regola per il matching dell'ID dell'input"""
        url = f'{GRAYLOG_URL}/streams'

        # Ottiene l'ID dell'index set predefinito
        index_set_id = self.get_default_index_set_id()

        data = {
            'title': title,
            'description': description,
            'remove_matches_from_default_stream': True,
            'matching_type': 'AND',
            'index_set_id': index_set_id,  # Aggiunge l'ID dell'index set
            'rules': [{
                'field': 'gl2_source_input',
                'type': 1,  # Match esatto
                'inverted': False,
                'value': matching_input_id
            }]
        }

        response = self.session.post(url, json=data)
        response.raise_for_status()

        stream_id = response.json()['stream_id']
        self.stream_ids[title] = stream_id
        print(f'Creato stream {title} con ID {stream_id}')

        # Avvia lo stream
        self.session.post(f'{GRAYLOG_URL}/streams/{stream_id}/resume')
        print(f'Avviato stream {title}')

        return stream_id

    def create_gelf_output(self, stream_id: str, title: str, host: str, port: int) -> None:
        """Crea un output GELF per uno stream"""
        url = f'{GRAYLOG_URL}/system/outputs'

        data = {
            'title': title,
            'type': 'org.graylog2.outputs.GelfOutput',
            'configuration': {
                'hostname': host,
                'protocol': 'tcp',
                'port': port,
                'connect_timeout': 1000,
                'reconnect_delay': 500,
                'tcp_no_delay': False,
                'tcp_keep_alive': False
            }
        }

        response = self.session.post(url, json=data)
        response.raise_for_status()
        output_id = response.json()['id']

        # Associa l'output allo stream
        url = f'{GRAYLOG_URL}/streams/{stream_id}/outputs'
        data = {
            'outputs': [output_id]
        }
        response = self.session.post(url, json=data)
        response.raise_for_status()
        print(f'Creato e associato output GELF {title} allo stream')

    def create_pipeline_rule(self, title: str, source: str) -> str:
        """Crea una regola pipeline"""
        url = f'{GRAYLOG_URL}/system/pipelines/rule'

        data = {
            'title': title,
            'description': f'Regola per {title}',
            'source': source
        }

        response = self.session.post(url, json=data)
        response.raise_for_status()

        rule_id = response.json()['id']
        self.rule_ids[title] = rule_id
        print(f'Creata regola pipeline {title} con ID {rule_id}')
        return rule_id

    def create_pipeline(self, title: str, rule_ids: list) -> str:
        """Crea una pipeline con le regole specificate"""
        url = f'{GRAYLOG_URL}/system/pipelines/pipeline'

        # Crea una source pipeline con tutte le regole nello stage 0
        pipeline_source = "pipeline \"" + title + "\"\n"
        pipeline_source += "stage 0 match either\n"
        for rule_id in rule_ids:
            pipeline_source += f"  rule \"{rule_id}\";\n"
        pipeline_source += "end"

        data = {
            'title': title,
            'description': 'Pipeline per il matching delle regex',
            'source': pipeline_source,
            'stages': [{
                'stage': 0,
                'match': 'EITHER',
                'rules': rule_ids
            }]
        }

        response = self.session.post(url, json=data)
        response.raise_for_status()

        pipeline_id = response.json()['id']
        self.pipeline_id = pipeline_id
        print(f'Creata pipeline {title} con ID {pipeline_id}')
        return pipeline_id

    def connect_pipeline_to_stream(self, stream_id: str, pipeline_id: str) -> None:
        """Collega una pipeline a uno stream"""
        url = f'{GRAYLOG_URL}/system/pipelines/connections/to_stream'

        data = {
            'stream_id': stream_id,
            'pipeline_ids': [pipeline_id]
        }

        response = self.session.post(url, json=data)
        response.raise_for_status()
        print(f'Pipeline collegata allo stream')

def main():
    setup = GraylogSetup()

    try:
        # Crea gli input
        input_log = setup.create_input('Raw tcp 5555: input log', 5555)
        input_sensitive = setup.create_input('Raw tcp 5556: input segnalazioni log sensibili', 5556)

        # Attende che gli input siano pronti
        # time.sleep(2)

        # Crea gli stream
        stream_log = setup.create_stream(
            'Sensitive Data Detector log stream',
            'Stream per l\'elaborazione dei log in ingresso',
            input_log
        )

        stream_sensitive = setup.create_stream(
            'Sensitive Data Detector segnalazioni log sensibili stream',
            'Stream per le notifiche di dati sensibili',
            input_sensitive
        )

        # Crea l'output GELF
        setup.create_gelf_output(
            stream_log,
            'Sensitive Data Detector GELF output',
            'host.docker.internal',
            24367
        )

        # Crea le regole pipeline
        email_rule = setup.create_pipeline_rule(
            'Regex email',
            r'''
rule "Regex email"
when
    regex("[^\\s@]+@[^\\s@]+\\.[^\\s@]+", to_string($message.message)).matches == true
then
    let newMsg = create_message(
        to_string($message._id) +
        ": regex email " +
        to_string($message.message)
    );
    route_to_stream(id: "''' + stream_sensitive + '''", message: newMsg);
end
'''
        )

        jwt_rule = setup.create_pipeline_rule(
            'Regex JWT',
            r'''
rule "Regex JWT"
when
    regex("[A-Za-z0-9-_]*\\.[A-Za-z0-9-_]*\\.[A-Za-z0-9-_]*", to_string($message.message)).matches == true
then
    let newMsg = create_message(
        to_string($message._id) +
        ": regex JWT " +
        to_string($message.message)
    );
    route_to_stream(id: "''' + stream_sensitive + '''", message: newMsg);
end
'''
        )

        coordinates_rule = setup.create_pipeline_rule(
            'Regex coordinate',
            r'''
rule "Regex coordinate"
when
    regex("(?:latitude.{0,4}\\d+\\.\\d+|longitude.{0,4}\\d+\\.\\d+)", lowercase(to_string($message.message))).matches == true
then
    let newMsg = create_message(
        to_string($message._id) +
        ": regex coordinate " +
        to_string($message.message)
    );
    route_to_stream(id: "''' + stream_sensitive + '''", message: newMsg);
end
'''
        )

        # Crea la pipeline
        pipeline = setup.create_pipeline(
            'Segnalazioni log regex pipeline',
            [email_rule, jwt_rule, coordinates_rule]
        )

        # Collega la pipeline allo stream
        setup.connect_pipeline_to_stream(stream_log, pipeline)

        print('\nConfigurazione di Graylog completata con successo')

    except requests.exceptions.RequestException as e:
        print(f'Errore durante la configurazione: {e}')
        if hasattr(e.response, 'text'):
            print(f'Risposta: {e.response.text}')
        sys.exit(1)

if __name__ == '__main__':
    main()
