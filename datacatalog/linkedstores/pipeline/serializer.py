from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import *

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
    APP_KEYS = ('id', 'modules', 'inputs', 'outputs', 'uuid')
    JOB_KEYS = ('appId', 'uuid')
    ACTOR_KEYS = ('id', 'image', 'opts')

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

    def __init__(self, component_list):
        comps = list()
        self.components = comps

        for c in component_list:
            if 'appId' in c:
                c['id'] = c.pop('appId')
                comps.append(self.filter_app_job_def(c))
            elif 'actorId' in c:
                c['id'] = c.pop('actorId')
                comps.append(self.filter_actor_def(c))
            elif 'id' in c:
                comps.append(self.filter_actor_def(c))

        sorted_comps = sorted(comps, key=lambda k: k['id'])

        setattr(self, 'components', sorted_comps)

    def to_json(self):
        """Renders the pipeline as minified JSON"""
        j = json.dumps(getattr(self, 'components', []),
                       indent=0, sort_keys=True,
                       separators=(',', ':'))
        return j
