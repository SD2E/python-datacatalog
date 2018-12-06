CASES = [('manual-upload.json', '106a1208-c416-5d0f-9df1-f047e1589895', True),
         ('platereader.json', '106865e3-98e3-5a14-896c-841db46f3692', True),
         ('rnaseq.json', '106dcb01-ab28-5b9e-8fc1-adcd37eeee2f', True),
         ('tacobot.json', '106bdffe-9a60-55fd-b41a-e303f7ad146a', True),
         ('tasbe.json', '1064e5a9-f7bd-5680-b94e-b629fa9d79a0', True),
         ('novel_chassis_rnaseq.json', '106bd127-e2d2-57ac-b9be-11ed06042e68', True),
         ('metadata_capture.json', '10602c0b-ec8f-5429-9f22-dbb8c790001f', True)]

COMPONENTS = [('web_service', {'uri': 'https://sd2e.org/data-depot'}),
              ('abaco_actor', {'id': 'wgqobY6wgkQJQ',
                               'options': {},
                               'repo': 'index.docker.io/jurrutia/rnaseq_manifest_agent:0.5'}),
              ('agave_app', {'id': 'bbq-brisket-0.5.0', 'inputs': {}, 'parameters': {'smoke': True}}),
              ('deployed_container', {'repo': 'sd2e/process_uploads_json:latest', 'hostname': 'services.sd2e.org'})]

from .files import get_files
