import sys
from ..converter import Converter, ConversionError, ValidationError
from ...tenancy import Projects

class Duke_Haase(Converter):

    """Convert Duke run CSV to sample-set schema"""

    def convert(self, input_fp, output_fp=None, verbose=True, config={}, enforce_validation=True):
        """Do the conversion by running a method in runner.py"""
        from .runner import convert_duke_haase
        passed_config = config if config != {} else self.options
        return convert_duke_haase(self.targetschema, self.encoding, input_fp,
                              verbose=verbose,
                              config=passed_config,
                              output_file=output_fp,
                              enforce_validation=enforce_validation)
