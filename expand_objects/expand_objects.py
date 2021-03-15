import os
import yaml

import expand_objects.exceptions as eoe
from expand_objects.logger import Logger

this_script_path = os.path.dirname(
    os.path.abspath(__file__)
)


class ExpansionStructureLocation:
    """
    Verify expansion structure file location or object
    """
    def __get__(self, obj, owner):
        return self.expansion_structure

    def __set__(self, obj, value):
        if isinstance(value, dict):
            parsed_value = value
        elif isinstance(value, str):
            if not os.path.isfile(value):
                raise eoe.FileNotFoundError('template expansion structure file not found: {}'.format(value))
            if not value.endswith(('.yaml', '.yml')):
                raise eoe.TypeError('File extension does not match yaml type: {}'.format(value))
            parsed_value = yaml.safe_load(value)
        else:
            raise eoe.TypeError(
                'template expansion structure reference is not a file path or dictionary: {}'.format(value))
        self.expansion_structure = parsed_value
        return


class VerifyTemplate:
    """
    Verify if template dictionary is a valid type and structure
    """
    def __init__(self, template_type):
        super().__init__()
        self.template_type = template_type

    def __get__(self, obj, owner):
        return self.template

    def __set__(self, obj, value):
        if not isinstance(value, dict):
            raise eoe.TypeError('Template must be a dictionary: {}'.format(value))
        try:
            # template dictionary should have one key (unique name) and one object as a value (field/value dict)
            # this assignment below will fail if that is not the case.
            (_, _), = value.items()
            template = value
        except ValueError:
            raise eoe.InvalidTemplateException(
                'An Invalid object {} was passed as an {} object'.format(value, self.template_type))
        self.template = template
        return


class ExpandObjects(Logger):
    """
    General class for expanding template objects.

    Attributes:
    template: epJSON dictionary containing HVACTemplate to expand
    expansion_structure: file or dictionary of expansion structure details
    """

    template = VerifyTemplate(template_type='General Template')
    expansion_structure = ExpansionStructureLocation()

    def __init__(
            self,
            template,
            expansion_structure=os.path.join(
                this_script_path,
                'resources',
                'template_expansion_structures.yaml')):
        super().__init__()
        self.expansion_structure = expansion_structure
        self.template = template
        # apply template name and fields as class attributes
        (template_name, template_structure), = template.items()
        self.template_name = template_name
        for template_field in template_structure.keys():
            setattr(self, template_field, template_structure[template_field])
        return


class ExpandThermostat(ExpandObjects):
    """
    Thermostat expansion operations
    """

    def __init__(self, template):
        super().__init__(template=template)
        return
