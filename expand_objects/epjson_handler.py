
import os, sys, json, jsonschema

from expand_objects.logger import Logger

class EPJSON:
    """
    Handle epjson (and json) specific tasks
    """
    def __init__(self, logger = None):
        if isinstance(logger, Logger):
            self.logger = logger
        else:
            self.logger = Logger().logger
        return

    def load_schema(self, schema_location = None):
        """
        Load schema to class object.

        Arguments
        -----
        schema_location (optional) : location of json schema.  If not provided
            then the default environment variable path (ENERGYPLUS_ROOT_DIR) and
            file (Energy+.schema.epJSON) will be used.

        Return
        -----
        class attribute 'schema' which contains the epjson schema
        """
        if not schema_location:
            schema_location = os.path.join(
                os.environ.get('ENERGYPLUS_ROOT_DIR'),
                'Energy+.schema.epJSON'
            )
        try:
            with open(schema_location) as f:
                self.schema = json.load(f)
            self.logger.info('schema loaded from %s', schema_location)
            self.logger.info('schema version: %s', self.schema['epJSON_schema_version'])
            self.logger.info('schema build: %s', self.schema['epJSON_schema_build'])
        except:
            self.logger.exception('Failed to load schema from %s', schema_location)
            self.schema = None
        return

    def load_epjson(self, file_location):
        """
        Load schema to class object.

        Arguments
        -----
        file_location : location of epjson file to read
        schema_location (optional) : location of json schema.  If not provided
            then the default environment variable path (ENERGYPLUS_ROOT_DIR) and
            file (Energy+.schema.epJSON) will be used.

        Return
        -----
        class object (file_location, schema_location)
        """
        try:
            with open(file_location) as f:
                self.input_file = json.load(f)
            self.logger.info('input EPJSON file loaded, %s top level objects', len(self.input_file.keys()))
        except:
            self.logger.exception("input file not found or failed to load")
            self.input_file = None
            sys.exit(1)
        return
