import os
import sys
import copy
import json
import jsondiff
import tempfile
import argparse
import logging
from jinja2 import Template
from pprint import pprint
import datacatalog

logger = logging.getLogger(__name__)

HERE = os.getcwd()
THIS = os.path.dirname(__file__)
PARENT = os.path.dirname(THIS)

from datacatalog.linkedstores.pipelinejob import graphfsm

def main(args):
    argdict = vars(args)
    try:
        datacatalog.linkedstores.pipelinejob.graphfsm.render_graph(**argdict)
    except Exception as gexc:
        logger.critical('Failed to render graph: {}'.format(gexc))

if __name__ == '__main__':

    logger.setLevel(logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename",
                        default=graphfsm.GRAPH_BASENAME,
                        help="Output file basename")
    parser.add_argument("--state",
                        default=graphfsm.GRAPH_STATE,
                        help="State to show as active")
    parser.add_argument("--title",
                        default=graphfsm.GRAPH_TITLE,
                        help="Graph title")
    args = parser.parse_args()
    main(args)
