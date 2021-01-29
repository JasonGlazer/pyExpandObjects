import os

__version__ = "0.0"
__author__ = "John Grando"

from expand_objects.epjson_handler import EPJSON
from expand_objects.logger import Logger

class ExpandObjects:
    """
    Base class for expand-objects
    """
    def __init__(self, logger_class = None):
        self.Logger = logger_class
        if isinstance(self.Logger, Logger):
            self.logger = self.Logger.logger
        else:
            self.logger = Logger().logger
        return

    def run(self, file_location, **kwargs):
        """
        Run expand-objects

        Paramters
        -----
        file_location : epJSON file location
        logger (optional) : logger object passed from parent function.
        schema_location (optional) : schema file location.  If not
            provided then an attempt to load the schema file in the energyplus
            root directory will be made
        use_validator (optional) : boolean value to indicate whether schema
            validation should be used.  This will run by default.
        """
        tst = EPJSON(logger_class = kwargs.get('logger', self.Logger))
        tst.load_schema(schema_location = kwargs.get('schema_location'))
        tst.load_epjson(file_location = file_location)
        if kwargs.get('use_validator', True):
            tst.validate_epjson()
        return

if __name__ == "__main__":
    #Temp code while tests are not set up
    eo = ExpandObjects(logger_class = Logger(logger_name = 'base_logger'))
    eo.run(
        file_location = os.path.join(
            os.environ.get('ENERGYPLUS_EXPANDOBJECTS_ROOT_DIR'),
            'test',
            'example_files',
            'RefBldgMediumOfficeNew2004_Chicago_epJSON.epJSON'
        )
    )
