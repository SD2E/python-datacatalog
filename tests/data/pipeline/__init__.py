CASES = [('manual-upload.json', '106a1208-c416-5d0f-9df1-f047e1589895', True),
         ('platereader.json', '106865e3-98e3-5a14-896c-841db46f3692', True),
         ('rnaseq.json', '106c3ebc-345b-5ed6-a973-97574b6f06fb', True),
         ('tacobot.json', '1064aaf1-459c-5e42-820d-b822aa4b3990', True),
         ('tasbe.json', '106de934-ea53-5a5a-aeb9-0d38ba9c6191', True),
         ('novel_chassis_rnaseq.json', '106bd127-e2d2-57ac-b9be-11ed06042e68', True),
         ('metadata_capture.json', '10619ec7-a70e-55aa-ba36-20baa8eabd18', True)]

COMPONENTS = [('web_service', {'uri': 'https://sd2e.org/data-depot'}),
              ('abaco_actor', {'id': 'wgqobY6wgkQJQ',
                               'options': {},
                               'repo': 'index.docker.io/jurrutia/rnaseq_manifest_agent:0.5'}),
              ('agave_app', {'id': 'bbq-brisket-0.5.0', 'inputs': {}, 'parameters': {'smoke': True}}),
              ('deployed_container', {'repo': 'sd2e/process_uploads_json:latest', 'hostname': 'services.sd2e.org'})]

from .files import get_files
