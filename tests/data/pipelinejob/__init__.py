CASES = [('tacobot.json', '107b93f3-1eae-5e79-8a18-0a480f8aa3a5', True)]
EVENTS = [('tacobot-run.json', '107b93f3-1eae-5e79-8a18-0a480f8aa3a5', True),
          ('tacobot-update.json', '107b93f3-1eae-5e79-8a18-0a480f8aa3a5', True),
          ('tacobot-resource.json', '107b93f3-1eae-5e79-8a18-0a480f8aa3a5', True),
          ('tacobot-finish.json', '107b93f3-1eae-5e79-8a18-0a480f8aa3a5', True)]

FAILED_EVENTS = [('tacobot-run-wrong-uuid.json', '1070761d-1a7a-535e-b6d3-a1a728a249ce', True)]

from .files import get_jobs, get_events, get_events_wrong_uuid
