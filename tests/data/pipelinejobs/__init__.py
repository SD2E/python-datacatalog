CASES = [('tacobot.json', '107f0d2d-db27-5c78-a185-0de4b995da36', True), ('tacobot2.json', '1073f4ff-c2b9-5190-bd9a-e6a406d9796a', False)]
EVENTS = [('tacobot-run.json', '107f0d2d-db27-5c78-a185-0de4b995da36', True), ('tacobot-update.json', '107f0d2d-db27-5c78-a185-0de4b995da36', True), ('tacobot-finish.json', '107f0d2d-db27-5c78-a185-0de4b995da36', True)]

from .files import get_jobs, get_events
