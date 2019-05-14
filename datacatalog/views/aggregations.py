import json
import os
from datacatalog import settings
from datacatalog import logger
from ..utils import import_submodules

logger = logger.get_logger(__name__, verbose=settings.LOG_VERBOSE)

class Aggregation(dict):
    author = None
    description = None
    view_name = None
    view_on = None

def get_aggregations(exclude=[]):
    """Discover and return view definitions

    Returns:
        dict: MongoDB view definitions keyed on view name
    """
    mods = import_submodules('datacatalog.views')
    aggs = dict()

    if isinstance(exclude, str):
        exclude = [exclude]
    elif exclude is None:
        exclude = []

    for m in mods:
        try:
            module_name = None
            try:
                module_name = m.__name__.split('.')[-1]
            except Exception:
                pass
            if module_name in exclude:
                continue
            logger.debug('Module: {}'.format(m))
            view_name = getattr(m, 'MONGODB_VIEW_NAME', module_name)
            if view_name is not None:
                logger.debug('View: {}'.format(view_name))
                mod_path = os.path.dirname(m.__file__)
                agg_file = getattr(m, 'AGGREGATION_FILE', 'aggregation.json')
                with (open(os.path.join(mod_path, agg_file), 'rb')) as af:
                    pkg_agg = Aggregation(json.load(af))
                    setattr(pkg_agg, 'view_name', view_name)
                    setattr(pkg_agg, 'view_on', pkg_agg.get('view_on'))
                    setattr(pkg_agg, 'description',
                            getattr(m, 'DESCRIPTION', 'View on ' + pkg_agg.view_on ))
                    setattr(pkg_agg, 'author',
                            getattr(m, 'AUTHOR', settings.TACC_TENANT_POC_EMAIL))
                    if view_name not in aggs:
                        aggs[view_name] = pkg_agg
                    else:
                        raise ValueError(
                            'Duplicate view name {} found'.format(view_name))
        except Exception:
            raise
    return aggs
