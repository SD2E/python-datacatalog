"""Transforms v1 (python-datacatalog 0.1.4) jobs to v2 (python-datacatalog 0.2.0)
"""
import argparse
import copy
import json
import os
import sys
import tempfile
from agavepy.agave import Agave
from pprint import pprint

HERE = os.getcwd()
THIS = os.path.dirname(__file__)
PARENT = os.path.dirname(THIS)
GPARENT = os.path.dirname(PARENT)

import datacatalog
from tacconfig import config

def main(args):
    settings = config.read_config()
    mongodb_v2 = settings.get('mongodb')
    mongodb_v1 = copy.copy(mongodb_v2)
    # Make overridable
    mongodb_v1['database'] = 'catalog'

    v2_stores = dict()
    v2_stores['pipeline'] = datacatalog.linkedstores.pipeline.PipelineStore(mongodb_v2)
    v2_stores['pipelinejob'] = datacatalog.linkedstores.pipelinejob.PipelineJobStore(mongodb_v2)

    db1 = datacatalog.mongo.db_connection(mongodb_v1)
    v1_stores = dict()
    v1_stores['pipeline'] = db1['pipeline']
    v1_stores['pipelinejob'] = db1['pipelinejob']

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--db1", help="Database holding v1 schema documents")
    parser.add_argument("--db2", help="Database holding v2 schema documents")
    args = parser.parse_args()
    main(args)
