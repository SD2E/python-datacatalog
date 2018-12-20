import os
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
DATADIR = os.path.join(PARENT, 'pipeline')

CASES = [('manual-upload.json', '106a1208-c416-5d0f-9df1-f047e1589895', True),
         ('platereader.json', '106865e3-98e3-5a14-896c-841db46f3692', True),
         ('rnaseq.json', '106c3ebc-345b-5ed6-a973-97574b6f06fb', True),
         ('tacobot.json', '1064aaf1-459c-5e42-820d-b822aa4b3990', True),
         ('tasbe.json', '106de934-ea53-5a5a-aeb9-0d38ba9c6191', True),
         ('novel_chassis_rnaseq.json', '106bd127-e2d2-57ac-b9be-11ed06042e68', True),
         ('metadata_capture.json', '10662d69-6a3d-5589-a226-fff72e70baf2', True)]

COMPONENTS = [('web_service', {'uri': 'https://sd2e.org/data-depot'}),
              ('abaco_actor', {'id': 'wgqobY6wgkQJQ',
                               'options': {},
                               'repo': 'index.docker.io/jurrutia/rnaseq_manifest_agent:0.5'}),
              ('agave_app', {'id': 'bbq-brisket-0.5.0', 'inputs': {}, 'parameters': {'smoke': True}}),
              ('deployed_container', {'repo': 'sd2e/process_uploads_json:latest', 'hostname': 'services.sd2e.org'})]

LOADS = [
    ('manual-upload.json', '106a1208-c416-5d0f-9df1-f047e1589895'),
    ('metadata_capture.json', '10662d69-6a3d-5589-a226-fff72e70baf2'),
    ('novel_chassis_rnaseq.json', '106bd127-e2d2-57ac-b9be-11ed06042e68'),
    ('platereader.json', '106865e3-98e3-5a14-896c-841db46f3692'),
    ('rnaseq.json', '106c3ebc-345b-5ed6-a973-97574b6f06fb'),
    ('tacobot.json', '1064aaf1-459c-5e42-820d-b822aa4b3990'),
    ('urrutia-aggregation.json', '106231a1-0c78-5067-b53b-11a33f4e1495'),
    ('urrutia-multiqc.json', '106cfa30-c4b5-56c2-8eaa-9c67a0d1eb62'),
]
