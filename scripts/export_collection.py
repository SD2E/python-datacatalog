import argparse
import json
import logging
import os
import sys
import tempfile
from pprint import pprint
from agavepy.agave import Agave
from tacconfig import config

HERE = os.getcwd()
SELF = __file__
THIS = os.path.dirname(SELF)
PARENT = os.path.dirname(THIS)
GPARENT = os.path.dirname(PARENT)
DATA = os.path.join(THIS, 'experiment_designs')

# Use local not installed install of datacatalog
if GPARENT not in sys.path:
    sys.path.insert(0, GPARENT)
import datacatalog
from datacatalog.jsonschemas.encoders import DateTimeEncoder

# TODO Build this dynamically, possibly using managers.common.Manager
COLLECTIONS = ['challenge_problem', 'experiment_design', 'experiment', 'measurement', 'sample', 'reference']

logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.DEBUG)
loghandler = logging.StreamHandler()
loghandler.setFormatter(logging.Formatter('%(name)s.%(levelname)s: %(message)s'))
logger.addHandler(loghandler)

from datetime import date, datetime

def json_datetime_serializer(obj):
    """JSON serializer for datetime objects
    """

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    raise TypeError("Type %s not serializable" % type(obj))

def main(args):

    logger.debug('Reading project config')
    project_settings = config.read_config(places_list=[PARENT])
    logger.debug('Reading config from ' + THIS + '/config.yml')
    bootstrap_settings = config.read_config(places_list=[THIS])
    settings = datacatalog.dicthelpers.data_merge(
        project_settings, bootstrap_settings)

    env = args.environment
    if env is None:
        env = 'production'
    if args.verbose is True:
        settings['verbose'] = True
    mongodb = settings.get(env).get('mongodb')
    agave_client = Agave.restore()

    mgr = datacatalog.managers.common.Manager(mongodb, agave_client)
    resp = mgr.stores[args.collection].query(query={}, attr_dict=True)
    json.dump(resp, args.output, sort_keys=True, indent=2, separators=(',', ':'), default=json_datetime_serializer)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('collection', help="collection", choices=COLLECTIONS)
    parser.add_argument('-v', help='verbose output', action='store_true', dest='verbose')
    parser.add_argument('-o', '--output', dest='output', type=argparse.FileType('w'), default=sys.stdout)
    parser.add_argument('-production', help='manage production deployment', action='store_const',
                        const='production', dest='environment')
    parser.add_argument('-staging', help='manage staging deployment', action='store_const',
                        const='staging', dest='environment')
    parser.add_argument('-development', help='manage development deployment', action='store_const',
                        const='development', dest='environment')
    parser.add_argument('-localhost', help='manage localhost deployment', action='store_const',
                        const='localhost', dest='environment')
    args = parser.parse_args()
    main(args)
