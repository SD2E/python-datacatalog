class UnsupportedMapping(NotImplementedError):
    pass

class ExperimentReferenceError(Exception):
    pass

class MappingNotFound(ExperimentReferenceError):
    pass

class IncorrectConfiguration(ExperimentReferenceError):
    pass

class LookupNotPopulated(ExperimentReferenceError):
    pass

class GoogleSheetsError(ExperimentReferenceError):
    pass
