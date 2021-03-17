import os
import yaml
import copy
import re
from pathlib import Path

import custom_exceptions as eoe
from epjson_handler import EPJSON

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
            value_is_path = Path(value)
            if value_is_path.is_file():
                if not value.endswith(('.yaml', '.yml')):
                    raise eoe.TypeError('File extension does not match yaml type: {}'.format(value))
                else:
                    with open(value, 'r') as f:
                        # todo_eo: discuss safety issue if loader.
                        # With FullLoader there would be more functionality but might not be necessary.
                        parsed_value = yaml.load(f, Loader=yaml.SafeLoader)
            else:
                try:
                    # if the string is not a file, then try to load it directly with SafeLoader.
                    parsed_value = yaml.load(value, Loader=yaml.SafeLoader)
                    # if the parsed value is the same as the input value, it's probably a bad file path
                    if parsed_value == value:
                        raise eoe.FileNotFoundError('File does not exist: {}'.format(value))
                except yaml.YAMLError as exc:
                    if hasattr(exc, 'problem_mark'):
                        mark = exc.problem_mark
                        raise eoe.YamlError("problem loading yaml at ({}, {})".format(mark.line + 1, mark.column + 1))
                    else:
                        raise eoe.YamlError()
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
            (_, object_structure), = value.items()
            # ensure object is dictionary
            if not isinstance(object_structure, dict):
                raise eoe.InvalidTemplateException(
                    'An Invalid object {} was passed as an {} object'.format(value, self.template_type))
            template = value
        except ValueError:
            raise eoe.InvalidTemplateException(
                'An Invalid object {} was passed as an {} object'.format(value, self.template_type))
        self.template = template
        return


class ExpandObjects(EPJSON):
    """
    General class for expanding template objects.

    Attributes:
    template: epJSON dictionary containing HVACTemplate to expand
    expansion_structure: file or dictionary of expansion structure details
    epjson: dictionary of epSJON objects to write to file
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
        self.epjson = {}
        return

    def get_structure(
            self,
            structure_hierarchy: list) -> dict:
        """
        Retrieve structure from dict created by yaml object

        :param structure_hierarchy: list representing structure hierarchy
        :return: structured object as dictionary
        """
        try:
            structure = copy.deepcopy(self.expansion_structure)
            for key in structure_hierarchy:
                structure = structure[key]
        except KeyError:
            raise eoe.TypeError('YAML structure does not exist for hierarchy: {}'.format(structure_hierarchy))
        return structure

    def build_compact_schedule(
            self,
            structure_hierarchy: list,
            insert_values: list,
            name: str = None) -> dict:
        """
        Build a compact schedule from inputs.  Save epjJSON object to class dictionary and return to calling function.

        :param structure_hierarchy: list indicating YAML structure hierarchy
        :param insert_values: list of values to insert into object
        :param name: (optional) name of object.
        :return: epJSON object of compact schedule
        """
        structure_object = self.get_structure(structure_hierarchy)
        if not isinstance(insert_values, list):
            insert_values = [insert_values, ]
        if not name:
            name = structure_object.pop('name')
        if '{}' in name:
            name = name.format(insert_values[0])
        if not structure_object.get('schedule_type_limits_name', None):
            structure_object['schedule_type_limits_name'] = 'Any Number'
        # for each element in the schedule, convert to numeric if value replacement occurs
        if insert_values:
            formatted_data_lines = [
                {j: float(k.format(*insert_values))}
                if re.match(r'.*{.*f}', k, re.IGNORECASE) else {j: k}
                for i in structure_object['data'] for j, k in i.items()]
        else:
            formatted_data_lines = [{j: k} for i in structure_object for j, k in i.items()]
        schedule_object = {
            'Schedule:Compact': {
                name: {
                    'schedule_type_limits_name': structure_object['schedule_type_limits_name'],
                    'data': formatted_data_lines
                }
            }
        }
        # add objects to class epjson dictionary
        self.epjson = self.merge_epjson(
            super_dictionary=self.epjson,
            object_dictionary=schedule_object,
            unique_name_override=True
        )
        return schedule_object


class ExpandThermostat(ExpandObjects):
    """
    Thermostat expansion operations
    """

    def __init__(self, template):
        # pre-set template inputs with None.  Is this better to have them pre-defined?
        # todo_eo: discuss whether attribute validation should occur such that unknown field names raise exceptions
        self.heating_setpoint_schedule_name = None
        self.constant_heating_setpoint = None
        self.cooling_setpoint_schedule_name = None
        self.constant_cooling_setpoint = None
        # fill values with template inputs
        super().__init__(template=template)
        return

    def create_and_set_schedules(self):
        """
        Create, or use existing, schedules.  Assign schedule names to class variable

        :return: Cooling and/or Heating schedule variables as class attributes
        """
        for thermostat_type in ['heating', 'cooling']:
            if not getattr(self, '{}_setpoint_schedule_name'.format(thermostat_type), None) \
                    and getattr(self, 'constant_{}_setpoint'.format(thermostat_type), None):
                thermostat_schedule = self.build_compact_schedule(
                    structure_hierarchy=['Schedule', 'Compact', 'ALWAYS_VAL'],
                    insert_values=getattr(self, 'constant_{}_setpoint'.format(thermostat_type)),
                )
                (thermostat_schedule_type, thermostat_schedule_structure), = thermostat_schedule.items()
                (thermostat_schedule_name, _), = thermostat_schedule_structure.items()
                setattr(self, '{}_setpoint_schedule_name'.format(thermostat_type), thermostat_schedule_name)
        return

    def create_thermostat_setpoints(self):
        """
        Create ThermostatSetpoint objects based on class setpoint_schedule_name attributes
        :return: Updated class epJSON dictionary with ThermostatSetpoint objects added.
        """
        if getattr(self, 'heating_setpoint_schedule_name', None) \
                and getattr(self, 'cooling_setpoint_schedule_name', None):
            thermostat_setpoint_object = {
                "ThermostatSetpoint:DualSetpoint": {
                    '{} SP Control'.format(self.template_name): {
                        'heating_setpoint_temperature_schedule_name': self.heating_setpoint_schedule_name,
                        'cooling_setpoint_temperature_schedule_name': self.cooling_setpoint_schedule_name
                    }
                }
            }
        elif getattr(self, 'heating_setpoint_schedule_name', None):
            thermostat_setpoint_object = {
                "ThermostatSetpoint:SingleHeating": {
                    '{} SP Control'.format(self.template_name): {
                        'setpoint_temperature_schedule_name': self.heating_setpoint_schedule_name
                    }
                }
            }
        elif getattr(self, 'cooling_setpoint_schedule_name', None):
            thermostat_setpoint_object = {
                "ThermostatSetpoint:SingleCooling": {
                    '{} SP Control'.format(self.template_name): {
                        'setpoint_temperature_schedule_name': self.cooling_setpoint_schedule_name
                    }
                }
            }
        else:
            raise eoe.InvalidTemplateException(
                'No setpoints or schedules provided to HVACTemplate:Thermostat object: {}'.format(self.template_name))
        self.epjson = self.merge_epjson(
            super_dictionary=self.epjson,
            object_dictionary=thermostat_setpoint_object,
            unique_name_override=False
        )
        # todo_eo make single setpoint schedules
        return

    def run(self):
        """
        Perform all template expansion operations and return the class to the parent calling function.
        :return: ExpandThermostat class with necessary attributes filled for output
        """
        self.create_and_set_schedules()
        self.create_thermostat_setpoints()
        return self
