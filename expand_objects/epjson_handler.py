import json
import jsonschema
from pathlib import Path
from expand_objects.logger import Logger

this_script_path = Path(__file__).resolve()


class UniqueNameException(Exception):
    pass


class EPJSON(Logger):
    """
    Handle epjson (and json) specific tasks

    Inheritance:
    Logger

    Attributes:
    Validator: schema validator from jsonschema
    schema_validator: validated schema
    schema: loaded schema.  This can be a failed or unvalidated schema.
        However, it requires a valid json object
    schema_location: file path for schema
    input_epjson: input epjson file
    schema_is_valid: initialized as None.  False if failed, True if passed.
    input_epjson_is_valid: initialized as None.  False if failed, True if passed.
    """

    def __init__(self, no_schema=True):
        super().__init__()
        self.no_schema = no_schema
        self.Validator = jsonschema.Draft4Validator
        self.schema = None
        self.schema_is_valid = None
        self.schema_validator = None
        self.input_epjson = None
        self.input_epjson_is_valid = None
        self.schema_location = None

    @staticmethod
    def merge_epjson(
            super_dictionary: dict,
            object_dictionary: dict,
            unique_name_override: bool = True,
            unique_name_fail: bool = True) -> dict:
        """
        Merge a high level formatted dictionary with a sub-dictionary, both in epJSON format

        :param super_dictionary: high level dictionary used as the base object
        :param object_dictionary: dictionary to merge into base object
        :param unique_name_override: allow a duplicate unique name to overwrite an existing object
        :param unique_name_fail: if override is set to False, choose whether to skip object or fail
        :return: merged output of the two input dictionaries
        """
        for object_type, object_structure in object_dictionary.items():
            if not super_dictionary.get(object_type):
                super_dictionary[object_type] = {}
            if isinstance(object_structure, dict):
                for object_name, object_fields in object_structure.items():
                    if not unique_name_override and object_name in super_dictionary[object_type].keys():
                        if unique_name_fail:
                            raise UniqueNameException("Unique name {} already exists in object {}".format(
                                object_name,
                                object_type
                            ))
                        else:
                            continue
                    super_dictionary[object_type][object_name] = object_fields
            elif isinstance(object_structure, list):
                super_dictionary[object_type] = object_structure
        return super_dictionary

    def _get_json_file(self, json_location=None):
        """
        Load json file and return an error and None if fails

        :param json_location: file location for json object
        :return: loaded json object
        """
        json_obj = None
        try:
            with open(json_location) as f:
                json_obj = json.load(f)
        except FileNotFoundError:
            self.logger.exception("file does not exist: %s", json_location)
        except Exception as e:
            self.logger.exception("file is not a valid json: %s\n%s", json_location, str(e))
        return json_obj

    def _validate_schema(self, schema):
        """
        Validate schema based on the loaded
        jsonschema pre-built validator (self.Validator)

        :param schema: loaded schema object
        :return: validated schema object or False value if failed
        """
        schema_validator = False
        try:
            self.Validator.check_schema(schema)
            schema_validator = self.Validator(schema)
            self.logger.info('schema version: %s', self.schema['epJSON_schema_version'])
            self.logger.info('schema build: %s', self.schema['epJSON_schema_build'])
        except jsonschema.exceptions.SchemaError:
            self.logger.exception('Failed to validate schema')
        except Exception as e:
            self.logger.exception('Schema validator failed:\n%s', str(e))
        finally:
            return schema_validator

    def load_schema(self, schema_location=None):
        """
        Load schema to class object.

        :param schema_location: (Optional) location of json schema.  If not provided
            then the default environment variable path (ENERGYPLUS_ROOT_DIR) and
            file (Energy+.schema.epJSON) will be used.

        :return: Validated schema as a class attribute
        """
        if self.no_schema:
            self.schema = False
            self.schema_is_valid = False
            self.schema_validator = False
            if not schema_location:
                try:
                    schema_location = str(this_script_path.parent / 'resources' / 'Energy+.schema.epJSON')
                except Exception as e:
                    self.logger.exception('Schema file path is not valid; \n%s', str(e))
                    return
            self.schema_location = schema_location
            self.schema = self._get_json_file(schema_location)
            if self.schema:
                self.logger.info('Schema loaded: %s', schema_location)
                self.schema_validator = self._validate_schema(self.schema)
                if self.schema_validator:
                    self.schema_is_valid = True
        return

    def _validate_epjson(self, input_epjson):
        """
        Validate json file based on loaded schema.

        :param input_epjson: epJSON object
        :return: boolean indicating whether object is valid
        """
        epjson_is_valid = False
        if not self.schema or \
                not self.schema_is_valid or \
                not self.schema_validator:
            self.logger.error("Schema has either not been loaded or not validated.  "
                              "File can't be processed")
            return epjson_is_valid
        try:
            file_validation = self.schema_validator.is_valid(input_epjson)
            if not file_validation:
                self.logger.error("Input file does not meet schema format")
                for err in self.schema_validator.iter_errors(input_epjson):
                    self.logger.error(err.message)
                return epjson_is_valid
            epjson_is_valid = True
        except Exception as e:
            self.logger.exception('epJSON validation failed; \n%s', str(e))
        finally:
            return epjson_is_valid

    def load_epjson(self, epjson_ref, validate=True):
        """
        Load schema to class object.

        :param epjson_ref: Location of epJSON file to read or object itself
        :param validate: Whether or not to perform schema validation

        :return: boolean flag for valid epJSON and epJSON object as class attributes
        """
        try:
            if isinstance(epjson_ref, dict):
                self.input_epjson = epjson_ref
            else:
                self.input_epjson = self._get_json_file(epjson_ref)
        except FileNotFoundError:
            self.logger.error('epJSON file not found')
            self.input_epjson = False
        if self.input_epjson:
            self.logger.info(
                'input EPJSON file loaded, %s top level objects',
                len(self.input_epjson.keys())
            )
            if validate and self.schema_is_valid:
                self.input_epjson_is_valid = self._validate_epjson(self.input_epjson)
        return
