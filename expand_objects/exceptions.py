import yaml
from jsonschema.exceptions import SchemaError
from expand_objects.logger import Logger


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


class SchemaError(CustomException, SchemaError):
    pass


class FileNotFoundError(CustomException, FileNotFoundError):
    pass


class TypeError(CustomException, TypeError):
    pass


class YamlError(CustomException, yaml.YAMLError):
    pass
