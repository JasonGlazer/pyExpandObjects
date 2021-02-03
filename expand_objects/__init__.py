__version__ = "0.0"
__author__ = "John Grando"

from expand_objects.epjson_handler import EPJSON
from expand_objects.logger import Logger


class ExpandObjects(Logger):
    """
    Base class for expand-objects

    Inheritance
    -----
    EPJSON : Class for handling epJSON files
        Parameters
        -----
        logger_class : Logging class for output
    """

    def __init__(self):
        super().__init__()
        # The same logger can be specified via logger_name
        self.epjson_handler = EPJSON()
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
        self.logger.info('Expand Objects starting')
        self.epjson_handler.load_schema(
            schema_location=kwargs.get('schema_location')
        )
        self.epjson_handler.load_epjson(
            epjson_ref=file_location,
            validate=True)
        self.logger.info('Expand Objects finished')
        return
