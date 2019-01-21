from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import *
from future import standard_library
standard_library.install_aliases()

import copy
from pprint import pprint
from .store import ManagedPipelineJob, ManagedPipelineJobError


class ReactorManagedPipelineJob(ManagedPipelineJob):
    def __init__(self,
                 reactor,
                 data={},
                 *args,
                 **kwargs):

        mongodb = reactor.settings.mongodb
        pipelines = reactor.settings.pipelines
        rxagent = reactor.uid
        rxtask = reactor.execid
        rxsession = reactor.nickname
        rxclient = reactor.client

        super(ReactorManagedPipelineJob, self).__init__(mongodb,
                                                        pipelines,
                                                        data=data,
                                                        agave=rxclient,
                                                        agent=rxagent,
                                                        session=rxsession,
                                                        task=rxtask,
                                                        **kwargs)

