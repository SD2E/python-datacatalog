import sys
from ..converter import Converter, ConversionError, ValidationError
class SampleAttributes(Converter):
    def convert(self, input_fp, output_fp=None, verbose=True, config={}, enforce_validation=True):
        # schema_file, input_file, verbose=True, output=True, output_file=None
        from .runner import convert_sample_attributes
        passed_config = config if config != {} else self.options
        return convert_sample_attributes(self.targetschema, self.encoding, input_fp, verbose=verbose, config=passed_config, output_file=output_fp, enforce_validation=enforce_validation)
