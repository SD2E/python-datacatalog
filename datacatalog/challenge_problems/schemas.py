from .store import ChallengeDocument

def get_schemas():
    d = ChallengeDocument()
    fname = getattr(d, '_filename')
    return {fname: d.to_jsonschema()}
