import sys
from ..converter import Converter, ConversionError, ValidationError
# from .runner import convert_biofab

class Biofab(Converter):
    def convert(self, input_fp, output_fp=None, verbose=True, config={}, enforce_validation=True):
        # schema_file, input_file, verbose=True, output=True, output_file=None
        from .runner import convert_biofab
        passed_config = config if config != {} else self.get('options', {})
        return convert_biofab(self.targetschema, input_fp, verbose=verbose, config=passed_config, output_file=output_fp, enforce_validation=enforce_validation)
