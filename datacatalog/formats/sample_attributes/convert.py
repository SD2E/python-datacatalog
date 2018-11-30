import sys
from ..converter import Converter, ConversionError, ValidationError

class SampleAttributes(Converter):
    """Convert generic samples attributes file to sample-set schema"""
    VERSION = '0.0.1'
    FILENAME = 'sample_attributes'

    def convert(self, input_fp, output_fp=None, verbose=True, config={}, enforce_validation=True):
        """Do the conversion by running a method in runner.py"""
        from .runner import convert_sample_attributes
        passed_config = config if config != {} else self.options
        return convert_sample_attributes(self.targetschema, input_fp,
                                         verbose=verbose,
                                         config=passed_config,
                                         output_file=output_fp,
                                         enforce_validation=enforce_validation)
