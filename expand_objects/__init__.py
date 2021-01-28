import os

__version__ = "0.0"
__author__ = "John Grando"

from expand_objects.epjson_handler import EPJSON
from expand_objects.logger import Logger

class ExpandObjects:
    def __init__(self, logger = None):
        if isinstance(logger, Logger):
            self.logger = logger
        else:
            self.logger = Logger().logger
        return

    def run(self, file_location, **kwargs):
        tst = EPJSON(logger = self.logger)
        tst.load_schema(schema_location = kwargs.get('schema_location'))
        tst.load_epjson(file_location = file_location)
        return

if __name__ == "__main__":
    eo = ExpandObjects(logger = Logger().logger)
    eo.run(
        file_location = os.path.join(
            os.environ.get('ENERGYPLUS_EXPANDOBJECTS_ROOT_DIR'),
            'example_files',
            'RefBldgMediumOfficeNew2004_Chicago_epJSON.epJSON'
        )
    )
