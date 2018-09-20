
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *
from builtins import object

from transitions.extensions import GraphMachine as Machine

from .fsm import JobStateMachine

class Model(object):
    pass

def plot_graph():

    class Model(object):
        pass

    m = Model()
    machine = Machine(model=m, states=JobStateMachine.states,
                      transitions=JobStateMachine.transitions, initial='created', title='PipelineJob.FSM')

    # draw the whole graph ...
    machine.get_graph().draw('pipelinejob-fsm.png', prog='dot')
