import sys
from ..converter import Converter, ConversionError, ValidationError

class Caltech(Converter):
    """Convert Caltech run.xlsx to sample-set schema"""
    VERSION = '0.0.1'
    FILENAME = 'caltech_samples'

    def convert(self, input_fp, output_fp=None, verbose=True, config={}, enforce_validation=True):
        """Do the conversion by running a method in runner.py"""
        from .runner import convert_caltech
        passed_config = config if config != {} else self.options
        return convert_caltech(self.targetschema, self.encoding, input_fp,
                              verbose=verbose,
                              config=passed_config,
                              output_file=output_fp,
                              enforce_validation=enforce_validation)
