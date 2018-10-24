from jsonschemas import JSONSchemaBaseObject
from .store import JobDocument as Doc
from .fsm import JobStateMachine
from pprint import pprint

def get_schemas():
    document_schemas = get_document_schemas()
    primitive_schemas = get_primitives()
    definition_schemas = get_definitions()
    schemas = {**document_schemas, **primitive_schemas}
    schemas = {**schemas, **definition_schemas}
    return schemas

def get_document_schemas():
    schemas = dict()
    d1 = Doc()
    d2 = Doc()
    fname = getattr(d1, '_filename')
    document_schema = d1.to_jsonschema(document=True)
    object_schema = d2.to_jsonschema(document=False)
    schemas[fname] = object_schema
    schemas[fname + '_document'] = document_schema
    return schemas

def get_definitions():
    return dict()

def get_primitives():
    events = get_fsm_schema_events()
    states = get_fsm_schema_states()
    schemas = {**events, **states}
    return schemas

def get_fsm_schema_events():
    events = JobStateMachine.get_events()
    setup_args = {'_filename': 'pipelinejob_eventname',
                  'title': 'PipelineJob event name',
                  'type': 'string',
                  'enum': events}
    schema = JSONSchemaBaseObject(**setup_args).to_jsonschema()
    return {'pipelinejob_event': schema}

def get_fsm_schema_states():
    states = JobStateMachine.get_states()
    setup_args = {'_filename': 'pipelinejob_statename',
                  'title': 'PipelineJob state name',
                  'type': 'string',
                  'enum': states}
    schema = JSONSchemaBaseObject(**setup_args).to_jsonschema()
    return {'pipelinejob_state': schema}
