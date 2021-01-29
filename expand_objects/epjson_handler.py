
import os, sys, json
import jsonschema as jschema
from expand_objects.logger import Logger

class EPJSON:
    """
    Handle epjson (and json) specific tasks
    """
    def __init__(self, logger_class = None):
        self.Logger = logger_class
        self.Validator = jschema.Draft4Validator
        self.schema_is_valid = None
        self.input_file_is_valid = None
        if isinstance(self.Logger, Logger):
            self.logger = self.Logger.logger
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

        epJSON_schema_build and epJSON_schema_version are required keys to pass
        the schema to the class variable.

        Return
        -----
        class attribute 'schema' which contains the epjson schema
        """
        self.schema_is_valid = False
        if not schema_location:
            schema_location = os.path.join(
                os.environ.get('ENERGYPLUS_ROOT_DIR'),
                'Energy+.schema.epJSON'
            )
        try:
            with open(schema_location) as f:
                self.schema = json.load(f)
            assert self.Validator(self.schema).check_schema(self.schema) is None
            self.Validator_schema = self.Validator(self.schema)
            self.schema_is_valid = True
            self.logger.info('schema validated and loaded: %s', schema_location)
            self.logger.info('schema version: %s', self.schema['epJSON_schema_version'])
            self.logger.info('schema build: %s', self.schema['epJSON_schema_build'])
        except AssertionError:
            self.logger.exception("Schema did not pass validation check")
            self.schema = None
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
            self.logger.info(
                'input EPJSON file loaded, %s top level objects',
                len(self.input_file.keys())
            )
        except:
            self.logger.exception("input file not found or failed to load")
            self.input_file = None
            sys.exit(1)
        return

    def validate_epjson(self):
        """
        Validate json file based on loaded schema
        """
        self.input_file_is_valid = False
        if not self.schema or\
        not self.schema_is_valid:
            self.logger.error("Schema has not be loaded or validated.  "
                "File can't be processed")
            return
        file_validation = self.Validator_schema.is_valid(self.input_file)
        if not file_validation:
            self.logger.error("Input file does not meet schema format")
            for err in self.Validator_schema.iter_errors(self.input_file):
                self.logger.error(err.message)
            return
        self.input_file_is_valid = True
        self.logger.info("Input file validated")
        return
