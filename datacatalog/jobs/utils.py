from .. import catalog_uuid
from uuid import UUID
import petname
import os

HASH_SALT = '97JFXMGWBDaFWt8a4d9NJR7z3erNcAve'
PATH_VERSION = 'v1'
PATH_BASE = 'products'

def validate_uuid5(uuid_string):
    """
    Validate that a UUID string is in
    fact a valid uuid5.
    """
    # Ref: https://gist.github.com/ShawnMilo/7777304

    try:
        UUID(uuid_string, version=5)
    except ValueError:
        # If it's a value error, then the string
        # is not a valid hex code for a UUID.
        raise ValueError('{} is not a valid catalog_uuid'.format(uuid_string))

def get_job_instance_directory():
    return petname.Generate(3, '-')

def get_archive_path(pipeline_id, lab, experiment_reference, measurement_id=None, session=None, version=PATH_VERSION):
    # FIXME Actually validate against known pipeline UUID
    # FIXME Validate lab, etc. against known metadata records
    validate_uuid5(pipeline_id)
    path_els = [PATH_BASE, version, pipeline_id]

    path_els.append(catalog_uuid(lab, binary=False))
    path_els.append(catalog_uuid(experiment_reference, binary=False))
    if measurement_id is not None:
        path_els.append(catalog_uuid(measurement_id, binary=False))
    if measurement_id is not None:
        path_els.append(catalog_uuid(measurement_id, binary=False))
    if session is None:
        path_els.append(get_job_instance_directory())
    else:
        path_els.append(session)

    return '/'.join(path_els)
