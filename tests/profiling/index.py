import time
import os

from datacatalog.linkedstores.fixity.indexer import FixityIndexer
from .data.fixity import files

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
DATA_DIR = os.path.join(PARENT, 'tests/data/fixity/files')

elapsed = list()

for use_cache in [True, False]:
    start_time = time.time()
    for reps in range(0, 5000):
        for fname, cksum, tsize, ftype in files.NO_SURPRISES:
            abs_fname = os.path.join(DATA_DIR, fname)
            rel_fname = os.path.join('tests/data/fixity/files', fname)
            fidx = FixityIndexer(abs_filename=os.path.abspath(abs_fname), name=rel_fname, cache_stat=use_cache)
            fidx.sync()
            assert fidx.type == ftype, 'wrong type for {}'.format(fname)
    elapsed.append(time.time() - start_time)

raise SystemError('Elapsed {} usec'.format(elapsed))
