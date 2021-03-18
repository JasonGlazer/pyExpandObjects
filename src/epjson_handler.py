import sys
import re
import json
import jsonschema
import copy
from pathlib import Path
from custom_exceptions import PyExpandObjectsFileNotFoundError, PyExpandObjectsSchemaError, \
    PyExpandObjectsTypeError, UniqueNameException
from logger import Logger

this_script_path = Path(__file__).resolve()


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

    def __init__(self, no_schema=False):
        super().__init__()
        self.no_schema = no_schema
        self.schema = None
        self.Validator = jsonschema.Draft4Validator
        self.schema_is_valid = None
        self.schema_validator = None
        self.input_epjson = None
        self.input_epjson_is_valid = None
        self.schema_location = None
        return

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

    @staticmethod
    def summarize_epjson(epjson):
        """
        Retrieve file, simulate, and compare it to a created epJSON object
        :param epjson:
        :return: dictionary of count summaries
        """
        output = {}
        for object_type, epjson_objects in epjson.items():
            for _, _ in epjson_objects.items():
                if not output.get(object_type):
                    output[object_type] = 1
                else:
                    output[object_type] = output[object_type] + 1
        return output

    @staticmethod
    def purge_epjson(epjson, purge_dictionary=None):
        """
        Remove objects in an input epJSON object.
        :param epjson: input epJSON
        :param purge_dictionary: key-value pair of object_type and list of regular expressions to remove items
            (.* removes all objects)
        :return: epJSON
        """
        tmp_d = copy.deepcopy(epjson)
        if purge_dictionary:
            for object_type, object_structure in epjson.items():
                if object_type in purge_dictionary.keys():
                    for object_name, object_fields in object_structure.items():
                        if isinstance(purge_dictionary[object_type], str):
                            purge_dictionary[object_type] = [purge_dictionary[object_type], ]
                        for rgx_match in purge_dictionary[object_type]:
                            if re.match(rgx_match, object_name):
                                tmp_d[object_type].pop(object_name)
                            if not tmp_d[object_type].keys():
                                tmp_d.pop(object_type)
        return tmp_d

    @staticmethod
    def unpack_epjson(epjson):
        """
        Create generator of epJSON objects

        :param epjson: epJSON object
        :return: generator which returns the subdictionaries of an epJSON object
        """
        for _, epjson_objects in epjson.items():
            for object_name, object_structure in epjson_objects.items():
                yield {object_name: object_structure}
        return None

    @staticmethod
    def _get_json_file(json_location=None):
        """
        Load json file and return an error and None if fails

        :param json_location: file location for json object
        :return: loaded json object
        """
        try:
            with open(json_location) as f:
                json_obj = json.load(f)
        except FileNotFoundError:
            raise PyExpandObjectsFileNotFoundError("file does not exist: {}", json_location)
        except Exception as e:
            raise PyExpandObjectsTypeError("file is not a valid json: %s\n%s", json_location, str(e))
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
        except jsonschema.exceptions.SchemaError as e:
            raise PyExpandObjectsSchemaError(e)
        except Exception as e:
            self.logger.exception('Schema validator failed:\n%s', str(e))
            sys.exit(1)
        finally:
            return schema_validator

    def load_schema(self, schema_location=None):
        """
        Load schema to class object.

        :param schema_location: (Optional) location of json schema.  If not provided
            then the default environment variable path (ENERGYPLUS_ROOT_DIR) and
            file (Energy+.schema.epJSON) will be used.

        :return: Validated schema, validator, and boolean flag as class attributes
        """
        if self.no_schema:
            self.schema = False
            self.schema_is_valid = False
            self.schema_validator = False
        else:
            if not schema_location:
                try:
                    schema_location = str(this_script_path.parent / 'resources' / 'Energy+.schema.epJSON')
                except FileNotFoundError:
                    raise PyExpandObjectsFileNotFoundError('Schema file path is not valid; \n%s')
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
        if not self.schema or \
                not self.schema_is_valid or \
                not self.schema_validator:
            self.logger.error("Schema has either not been loaded or not validated.  "
                              "File can't be processed")
            return False
        try:
            file_validation = self.schema_validator.is_valid(input_epjson)
            if not file_validation:
                self.logger.error("Input file does not meet schema format")
                for err in self.schema_validator.iter_errors(input_epjson):
                    self.logger.error(err.message)
                sys.exit(1)
            else:
                return True
        except Exception as e:
            self.logger.exception('epJSON validation failed; \n%s', str(e))
            sys.exit(1)

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
            raise PyExpandObjectsFileNotFoundError('epJSON file not found')
        if self.input_epjson:
            self.logger.info(
                'input EPJSON file loaded, %s top level objects',
                len(self.input_epjson.keys())
            )
            if validate and self.schema_is_valid:
                self.input_epjson_is_valid = self._validate_epjson(self.input_epjson)
        return

    def epjson_process(self, epjson_ref):
        self.logger.info('##### epJSON Setup #####')
        self.load_schema()
        self.load_epjson(epjson_ref=epjson_ref)
        return
