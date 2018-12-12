CASES = [('tacobot.json', '10797ce0-c130-5738-90d5-9e854adc67dd', True)]
EVENTS = [('tacobot-run.json', '10797ce0-c130-5738-90d5-9e854adc67dd', True),
          ('tacobot-update.json', '10797ce0-c130-5738-90d5-9e854adc67dd', True),
          ('tacobot-resource.json', '10797ce0-c130-5738-90d5-9e854adc67dd', True),
          ('tacobot-finish.json', '10797ce0-c130-5738-90d5-9e854adc67dd', True)]

FAILED_EVENTS = [('tacobot-run-wrong-uuid.json', '1070761d-1a7a-535e-b6d3-a1a728a249ce', True)]

from .files import get_jobs, get_events, get_events_wrong_uuid
