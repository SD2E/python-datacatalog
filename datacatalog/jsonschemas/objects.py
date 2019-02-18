import python_jsonschema_objects as pjs

def get_class_object(schema, classname=None):
    """Instantiate and return a Python class from a JSON schema

    Args:
        schema (dict): A dict containing a JSON schema
        classname (str, optional): Name of the instantiated class to return. Optional if only one class is present.

    Returns:
        class: A Python class corresponding to the schema
    """
    builder = pjs.ObjectBuilder(schema)
    ns = builder.build_classes(named_only=True)
    if classname is None:
        if len(dir(ns)) == 1:
            clsobj = getattr(ns, dir(ns)[0])
            return clsobj
        else:
            raise ValueError(
                'Multiple classes were defined by the JSON schema, ' +
                'so the "classname" parameter may not be empty.')
    try:
        clsobj = getattr(ns, classname)
        return clsobj
    except AttributeError:
        raise ValueError(
            'No class was named {}. Currently known options are {}'.format(
                classname,
                ', '.join(dir(ns))))
