
import os, sys, json
import jsonschema as jschema
from expand_objects.logger import Logger

class EPJSON(Logger):
    """
    Handle epjson (and json) specific tasks

    Parameters
    ------
    Validator : schema validator from jsonschema
    schema_validated : validated schema
    schema : loaded schema.  This can be a failed or unvalidated schema.
        However, it requires a valid json object
    *_is_valid : initialized as None.  False if failed, True if passed.
    """
    def __init__(self, logger_name = None):
        super().__init__(logger_name = logger_name or 'epjson_logger')
        self.Validator = jschema.Draft4Validator
        self.schema = None
        self.schema_is_valid = None
        self.schema_validated = None
        self.input_epjson = None
        self.input_epjson_is_valid = None
        return

    def _get_json_file(self, json_location = None):
        """
        Load json file and return an error and None if fails
        """
        json_obj = None
        try:
            with open(json_location) as f:
                json_obj = json.load(f)
        except FileNotFoundError:
            self.exception("file does not exist: %s", json_location)
        except:
            self.exception("file is not a valid json: %s", json_location)
        return json_obj

    def _validate_schema(self, schema):
        """
        Validate schema based on the loaded
        jsonschema pre-built validator (self.Validator)

        Returns line by line values of errors if not valid.
        """
        schema_validated = False
        try:
            self.Validator.check_schema(schema)
            schema_validated = self.Validator(schema)
            self.logger.info('schema version: %s', self.schema['epJSON_schema_version'])
            self.logger.info('schema build: %s', self.schema['epJSON_schema_build'])
        except jsonschema.exceptions.SchemaError:
            self.logger.exception('Failed to validate schema')
        except:
            self.logger.exception('Schema validator failed')
        finally:
            return schema_validated

    def load_schema(self, schema_location = None):
        """
        Load schema to class object.

        Arguments
        -----
        schema_location (optional) : location of json schema.  If not provided
            then the default environment variable path (ENERGYPLUS_ROOT_DIR) and
            file (Energy+.schema.epJSON) will be used.

        A valid schema is required to load the file.

        Return
        -----
        class attribute 'schema' which contains the validated epjson schema
        """
        self.schema = False
        self.schema_is_valid = False
        self.schema_validated = False
        if not schema_location:
            schema_location = os.path.join(
                os.environ.get('ENERGYPLUS_ROOT_DIR'),
                'Energy+.schema.epJSON'
            )
        self.schema_location = schema_location
        self.schema = self._get_json_file(schema_location)
        if self.schema:
            self.logger.info('Schema loaded: %s', schema_location)
            self.schema_validated = self._validate_schema(self.schema)
            if self.schema_validated:
                self.schema_is_valid = True
        return

    def _validate_epjson(self, input_epjson):
        """
        Validate json file based on loaded schema.

        If input epjson is not valid, line by line errors will be returned.
        """
        epjson_is_valid = False
        if not self.schema or\
        not self.schema_is_valid or\
        not self.schema_validated:
            self.logger.error("Schema has either not been loaded or not validated.  "
                "File can't be processed")
            return epjson_is_valid
        try:
            file_validation = self.schema_validated.is_valid(input_epjson)
            if not file_validation:
                self.logger.error("Input file does not meet schema format")
                for err in self.schema_validated.iter_errors(input_epjson):
                    self.logger.error(err.message)
                return epjson_is_valid
            epjson_is_valid = True
        except:
            self.logger.exception('epJSON validation failed')
        finally:
            return epjson_is_valid

    def load_epjson(self, file_location, validate = True):
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
        self.input_epjson = False
        self.input_epjson_is_valid = False
        self.input_epjson = self._get_json_file(file_location)
        if self.input_epjson:
            self.logger.info(
                'input EPJSON file loaded, %s top level objects',
                len(self.input_epjson.keys())
            )
            if validate:
                self.epjson_is_valid = self._validate_epjson(self.input_epjson)
        return
