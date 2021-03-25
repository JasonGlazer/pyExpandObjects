import yaml
from jsonschema.exceptions import SchemaError
from logger import Logger


class CustomException(Logger, Exception):
    """
    Custom Exceptions used to write outputs to logger and
    indicate program-specific issues
    """
    def __init__(self, msg=''):
        super().__init__()
        self.msg = msg
        self.logger.error(msg)
        return

    def __str__(self):
        return self.msg


class InvalidEpJSONException(CustomException):
    """
    epJSON errors
    """
    pass


class InvalidTemplateException(CustomException):
    """
    Incorrect template usage and references
    """
    pass


class UniqueNameException(CustomException):
    """
    Unintentional key-overriding in dictionary/JSON objects
    """
    pass


class PyExpandObjectsYamlStructureException(CustomException):
    """
    Hierarchy and organizational YAML file exceptions
    """
    pass


class PyExpandObjectsSchemaError(CustomException, SchemaError):
    pass


class PyExpandObjectsFileNotFoundError(CustomException, FileNotFoundError):
    pass


class PyExpandObjectsTypeError(CustomException, TypeError):
    pass


class PyExpandObjectsYamlError(CustomException, yaml.YAMLError):
    pass
