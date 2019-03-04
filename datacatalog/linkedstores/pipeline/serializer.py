import json

INDENT = 0
"""Default indentation for JSON rendering"""
SORT_KEYS = True
"""Default behavior for sorting keys when rendering to JSON"""
SEPARATORS = (',', ':')
"""Default tuple of JSON separators"""

class SerializedPipeline(object):
    """Helper class for serializing a pipeline definition

    Args:
        list: pipeline components expressed as `dict` objects
    """

    # TODO - Re-implement this with schema-informed classes
    COMPONENT_KEYS = {'agave_app': (('id', True), ('modules', False), ('inputs', True), ('outputs', False), ('parameters', True), ('uuid', False)),
                      'abaco_actor': (('id', True), ('image', True), ('options', False), ('uuid', False)),
                      'agave_job': (('appId', True), ('id', True), ('uuid', False)),
                      'deployed_container': (('image', True), ('hostname', True), ('hash', False), ('options', False), ('uuid', False)),
                      'web_service': (('uri', True), ('identifier', False), ('options', False), ('uuid', False))}
    """Fields to include in component definitions. Key is named after jsonschema. Tuple is (field, required)"""
    # APP_KEYS = ('id', 'modules', 'inputs', 'outputs', 'parameters', 'uuid')
    # JOB_KEYS = ('appId', 'uuid')
    # ACTOR_KEYS = ('id', 'repo', 'options', 'uuid')
    # REPO_KEYS = ('repo', 'hash', 'options', 'uuid')
    # WEBSERVICE_KEYS = ('uri', 'identifier', 'options', 'uuid')

    def filter_app_job_def(self, app_job_def):
        """Filter out extraneous keys in Agave app definitions"""
        new_def = {}
        for key in self.APP_KEYS + self.JOB_KEYS:
            if key in app_job_def:
                new_def[key] = app_job_def.get(key)
        return app_job_def

    def filter_actor_def(self, actor_def):
        """Filter out extraneous keys in Abaco actor definitions"""
        new_def = {}
        for key in self.ACTOR_KEYS:
            if key in actor_def:
                new_def[key] = actor_def.get(key)
        return actor_def

    @classmethod
    def classify_component(cls, component):
        """Determine type for a 'component' based on whether it contains mandated keys
        """
        for component_type, keyset in cls.COMPONENT_KEYS.items():
            try:
                for keyname, required in keyset:
                    if required:
                        if keyname not in component:
                            raise KeyError('Required key {} missing'.format(key))
                return component_type
            except Exception:
                pass
        return None

    @classmethod
    def filter_component(cls, component):
        ctype = SerializedPipeline.classify_component(component)
        if ctype is None:
            return None
        else:
            filtered_comp = dict()
            for key, req in cls.COMPONENT_KEYS[ctype]:
                if key in component:
                    filtered_comp[key] = component.get(key, '')
            return filtered_comp

    def __init__(self, component_list):
        comps = list()
        self.components = comps

        for comp in component_list:
            fcomp = SerializedPipeline.filter_component(comp)
            if fcomp is not None:
                comps.append(fcomp)

        # sorted_comps = sorted(comps, key=lambda k: k['id'])
        setattr(self, 'components', comps)

    def to_json(self):
        """Renders the pipeline as minified JSON"""
        j = json.dumps(getattr(self, 'components', []),
                       sort_keys=True,
                       separators=(',', ':'))
        return j
