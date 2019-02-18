import os
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
DATADIR = os.path.join(PARENT, 'pipeline')

CASES = [('manual-upload.json', '106a1208-c416-5d0f-9df1-f047e1589895', True),
         ('platereader.json', '106865e3-98e3-5a14-896c-841db46f3692', True),
         ('rnaseq.json', '10675194-f4d2-5a0c-9ce1-578670999e9c', True),
         ('tacobot.json', '10650844-1baa-55c5-a481-5e945b19c065', True),
         ('tasbe.json', '10617824-df0d-56c7-bdba-7829f6d3a86f', True),
         ('novel_chassis_rnaseq.json', '106bd127-e2d2-57ac-b9be-11ed06042e68', True),
         ('metadata_capture.json', '10621aa4-57fc-5ed9-ac10-03354f71fa3b', True)]

COMPONENTS = [('web_service', {'uri': 'https://sd2e.org/data-depot'}),
              ('abaco_actor', {'id': 'wgqobY6wgkQJQ',
                               'options': {},
                               'image': 'index.docker.io/jurrutia/rnaseq_manifest_agent:0.5'}),
              ('agave_app', {'id': 'bbq-brisket-0.5.0', 'inputs': {}, 'parameters': {'smoke': True}}),
              ('deployed_container', {'image': 'sd2e/process_uploads_json:latest', 'hostname': 'services.sd2e.org'})]

LOADS = [
    ('manual-upload.json', '106a1208-c416-5d0f-9df1-f047e1589895'),
    ('metadata_capture.json', '10662d69-6a3d-5589-a226-fff72e70baf2'),
    ('novel_chassis_rnaseq.json', '106bd127-e2d2-57ac-b9be-11ed06042e68'),
    ('platereader.json', '106865e3-98e3-5a14-896c-841db46f3692'),
    ('rnaseq.json', '106c3ebc-345b-5ed6-a973-97574b6f06fb'),
    ('tacobot.json', '10650844-1baa-55c5-a481-5e945b19c065'),
    ('urrutia-aggregation.json', '106231a1-0c78-5067-b53b-11a33f4e1495'),
    ('urrutia-multiqc.json', '106cfa30-c4b5-56c2-8eaa-9c67a0d1eb62'),
]
