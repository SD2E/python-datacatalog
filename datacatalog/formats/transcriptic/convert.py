import sys
from ..converter import Converter, ConversionError, ValidationError
# from .runner import convert_transcriptic

class Transcriptic(Converter):
    def convert(self, input_fp, output_fp=None, verbose=True, config={}, enforce_validation=True):
        from .runner import convert_transcriptic
        passed_config = config if config != {} else self.options
        return convert_transcriptic(self.targetschema, self.encoding, input_fp, verbose=verbose, config=passed_config, output_file=output_fp, enforce_validation=enforce_validation)
