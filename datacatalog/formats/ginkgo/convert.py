import sys
from ..converter import Converter, ConversionError, ValidationError
# from .runner import convert_ginkgo
class Ginkgo(Converter):
    VERSION = '0.0.2'
    FILENAME = 'ginkgo_samples'

    def convert(self, input_fp, output_fp=None, verbose=True, config={}, enforce_validation=True):
        # schema_file, input_file, verbose=True, output=True, output_file=None
        from .runner import convert_ginkgo
        passed_config = config if config != {} else self.options
        return convert_ginkgo(self.targetschema, input_fp, verbose=verbose, config=passed_config, output_file=output_fp, enforce_validation=enforce_validation)
