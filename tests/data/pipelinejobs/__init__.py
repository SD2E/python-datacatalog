CASES = [('tacobot.json', '107a6c4a-f354-53d6-b97d-2c497b9b352e', True), ('tacobot2.json', '1073f4ff-c2b9-5190-bd9a-e6a406d9796a', False)]
EVENTS = [('tacobot-run.json', '107a6c4a-f354-53d6-b97d-2c497b9b352e', True), ('tacobot-update.json', '107a6c4a-f354-53d6-b97d-2c497b9b352e', True), ('tacobot-finish.json', '107a6c4a-f354-53d6-b97d-2c497b9b352e', True)]

from .files import get_jobs, get_events
