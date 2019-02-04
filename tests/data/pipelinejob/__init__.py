CASES = [('tacobot.json', '107f299e-c477-51d7-93d1-b01cdf18674a', True)]
EVENTS = [('tacobot-run.json', '107f299e-c477-51d7-93d1-b01cdf18674a', True),
          ('tacobot-update.json', '107f299e-c477-51d7-93d1-b01cdf18674a', True),
          ('tacobot-resource.json', '107f299e-c477-51d7-93d1-b01cdf18674a', True),
          ('tacobot-finish.json', '107f299e-c477-51d7-93d1-b01cdf18674a', True)]

FAILED_EVENTS = [('tacobot-run-wrong-uuid.json', '1070761d-1a7a-535e-b6d3-a1a728a249ce', True)]

from .files import get_jobs, get_events, get_events_wrong_uuid
