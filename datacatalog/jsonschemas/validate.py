import jsonschema
from tenacity import retry, retry_if_exception_type, stop_after_delay, stop_after_attempt, wait_random
from .formatchecker import formatChecker

@retry(retry=retry_if_exception_type(jsonschema.exceptions.RefResolutionError), stop=(stop_after_delay(15) | stop_after_attempt(5)), wait=wait_random(min=1, max=3), reraise=True)
def validate(to_validate, schema, format_checker=None):
    """Validate a dict against a JSON schema.

    Includes retry in case the remote schema does not resolve
    """
    if format_checker is None:
        format_checker = formatChecker()
    return jsonschema.validate(to_validate, schema, format_checker=format_checker)
