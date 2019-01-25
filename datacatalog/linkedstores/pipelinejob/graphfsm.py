from pprint import pprint
from transitions.extensions import GraphMachine as Machine
from . import fsm

STATES = fsm.JobStateMachine.states
TRANSITIONS = fsm.JobStateMachine.transitions

GRAPH_STATE = 'CREATED'
GRAPH_TITLE = 'PipelineJob.FSM'
GRAPH_BASENAME = 'pipelinejob-fsm'

def build_graph(pstate, ptitle, events=[]):
    m = get_machine_state(pstate, ptitle, events)
    g = m.get_graph()
    return g

def get_machine_state(pstate, ptitle, events=['create']):
    m = get_machine(pstate, ptitle)
    for e in events:
        pass
#        m.handle(e)
    return m

def get_machine(pstate, ptitle):
    class Model(object):
        pass

    m = Model()
    machine = Machine(model=m, states=STATES,
                      transitions=TRANSITIONS,
                      initial=pstate, title=ptitle)

    return machine

def render_graph(**kwargs):

    pstate = kwargs.get('state', GRAPH_STATE)
    ptitle = kwargs.get('title', GRAPH_TITLE)
    pfilename = kwargs.get('filename', GRAPH_BASENAME)
    pevents = kwargs.get('events', ['create'])

    graph = build_graph(pstate, ptitle, pevents)
    filename = pfilename + '-' + pstate.lower() + '.png'
    graph.draw(filename, prog='dot')
