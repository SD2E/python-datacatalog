import arrow
from .. import identifiers
from .. import pathmappings

MANAGED_LEVELS = ('1', '2')
ARCHIVE_PATH_VERSION = 'v1'
ARCHIVE_PATH_PREFIX = pathmappings.prefix_for_level()

def get_instance_directory(session=None):
    if session is None or len(session) < 4:
        return identifiers.interesting_animal.generate()
    if not session.endswith('-'):
        session = session + '-'
    return session + arrow.utcnow().format('YYYYMMDDTHHmmss') + 'Z'

def get_archive_path(pipeline_uuid, **kwargs):
    """Construct an archivePath for a pipeline job
    Arguments:
    Parameters:
    Returns:
    String representation of a job archiving path
    """

    # FIXME Actually validate against known pipeline UUIDs
    identifiers.datacatalog_uuid.validate(pipeline_uuid)

    version = ARCHIVE_PATH_VERSION
    path_els = [ARCHIVE_PATH_PREFIX, version]

    # FIXME Validate lab, etc. against known metadata entries

    # Mandatory arguments
    for el in ['lab_name', 'experiment_reference']:
        if kwargs.get(el, None) is not None:
            path_els.append(identifiers.datacatalog_uuid.generate(
                kwargs.get(el), binary=False))
        else:
            raise KeyError('{} must be specified'.format(el))

    # Optional arguments
    for el in ['measurement_id']:
        if kwargs.get(el, None) is not None:
            path_els.append(identifiers.datacatalog_uuid.generate(
                kwargs.get(el), binary=False))
        else:
            pass

    # Not allowed to be empty so we can safely append it without further checks
    path_els.append(pipeline_uuid)

    # Session
    path_els.append(get_instance_directory(kwargs.get('session', None)))

    # NOTE /products/v1/<lab.uuid>/<experiment.uuid>/<measurement.uuid>/<pipeline.uuid/<session|petname>-MMMMDDYYHHmmss
    return '/'.join(path_els)
