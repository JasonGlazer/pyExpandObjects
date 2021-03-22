import copy
import yaml
import re
from pathlib import Path

from custom_exceptions import PyExpandObjectsTypeError, InvalidTemplateException, \
    PyExpandObjectsYamlError, PyExpandObjectsFileNotFoundError, PyExpandObjectsYamlStructureException
from epjson_handler import EPJSON

source_dir = Path(__file__).parent


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
                    raise PyExpandObjectsTypeError('File extension does not match yaml type: {}'.format(value))
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
                        raise PyExpandObjectsFileNotFoundError('File does not exist: {}'.format(value))
                except yaml.YAMLError as exc:
                    if hasattr(exc, 'problem_mark'):
                        mark = exc.problem_mark
                        raise PyExpandObjectsYamlError("problem loading yaml at ({}, {})".format(
                            mark.line + 1, mark.column + 1))
                    else:
                        raise PyExpandObjectsYamlError()
        else:
            raise PyExpandObjectsTypeError(
                'template expansion structure reference is not a file path or dictionary: {}'.format(value))
        self.expansion_structure = parsed_value
        return


class VerifyTemplate:
    """
    Verify if template dictionary is a valid type and structure
    """
    def __init__(self):
        super().__init__()

    def __get__(self, obj, owner):
        return self.template

    def __set__(self, obj, value):
        if not isinstance(value, dict):
            raise PyExpandObjectsTypeError('Template must be a dictionary: {}'.format(value))
        try:
            # template dictionary should have one template_ype, one key (unique name)
            # and one object as a value (field/value dict)
            # this assignment below will fail if that is not the case.
            (template_type, template_structure), = value.items()
            (_, object_structure), = template_structure.items()
            # ensure object is dictionary
            if not isinstance(object_structure, dict):
                raise InvalidTemplateException(
                    'An Invalid object {} was passed as an {} object'.format(value, self.template_type))
            self.template = template_structure
        except ValueError:
            raise InvalidTemplateException(
                'An Invalid object {} failed verification'.format(value))
        return


class ExpandObjects(EPJSON):
    """
    Class to contain general expansion functions as well as methods to connect template outputs.

    Attributes:
        expansion_structure: file or dictionary of expansion structure details (from YAML)
        template: epJSON dictionary containing HVACTemplate to expand
        template_type: HVACTemplate object type
        template_name: HVACTemplate unique name
        epjson: dictionary of epSJON objects to write to file
        HVACTemplate fields are stored as class attributes
    """

    template = VerifyTemplate()
    expansion_structure = ExpansionStructureLocation()

    def __init__(
            self,
            template,
            expansion_structure=str(source_dir / 'resources' / 'template_expansion_structures.yaml')):
        super().__init__()
        self.expansion_structure = expansion_structure
        self.template = template
        try:
            (hvac_template_type, hvac_template_structure), = template.items()
            (template_name, template_structure), = hvac_template_structure.items()
        except ValueError:
            raise InvalidTemplateException(
                'An Invalid object {} failed verification'.format(template))
        self.template_type = hvac_template_type
        self.template_name = template_name
        # apply template name and fields as class attributes
        for template_field in template_structure.keys():
            setattr(self, template_field, template_structure[template_field])
        self.epjson = {}
        return

    def get_structure(
            self,
            structure_hierarchy: list,
            structure=None) -> dict:
        """
        Retrieve structure from YAML loaded object

        :param structure_hierarchy: list representing structure hierarchy
        :param structure: YAML loaded dictionary, default is loaded yaml loaded object
        :return: structured object as dictionary
        """
        try:
            structure = copy.deepcopy(structure or self.expansion_structure)
            if not isinstance(structure_hierarchy, list):
                raise PyExpandObjectsTypeError("Input must be a list of structure keys: {}".format(structure_hierarchy))
            for key in structure_hierarchy:
                structure = structure[key]
        except KeyError:
            raise PyExpandObjectsTypeError('YAML structure does not exist for hierarchy: {}'.format(
                structure_hierarchy))
        return structure

    def get_option_tree(
            self,
            structure_hierarchy: list) -> dict:
        """
        Retrieve structure from YAML loaded object and verify it is correctly formatted for an option tree
        :param structure_hierarchy: list representing structure hierarchy
        :return: structured object as dictionary
        """
        try:
            if not isinstance(structure_hierarchy, list):
                raise PyExpandObjectsTypeError("Input must be a list of structure keys: {}".format(structure_hierarchy))
            if structure_hierarchy[0] != 'OptionTree':
                structure_hierarchy.insert(0, 'OptionTree')
        except TypeError:
            raise PyExpandObjectsTypeError(
                "Call to YAML object was not a list of structure keys: {}".format(structure_hierarchy))
        structure = self.get_structure(structure_hierarchy=structure_hierarchy)
        # Check structure keys.  Return error if there is an unexpected value
        for key in structure:
            if key not in ['Template', 'InsertElement', 'ReplaceElement', 'RemoveElement',
                           'AdditionalObjects', 'AdditionalTemplateObjects']:
                raise PyExpandObjectsYamlStructureException(
                    "YAML object is incorrectly formatted: {}, bad key: {}".format(structure, key))
        return structure

    def _get_option_tree_leaf(self, option_tree, leaf_path):
        """
        Return Build path from OptionTree

        :param option_tree: Yaml object holding HVACTemplate option tree
        :param leaf_path: path to leaf node of option tree
        :return: Verified BuildPath and Transition dictionary as keys in an object
        """
        option_leaf = self.get_structure(structure_hierarchy=leaf_path, structure=option_tree)
        transitions = option_leaf.pop('Transitions', None)
        if len(option_leaf.keys()) != 1:
            raise PyExpandObjectsTypeError('OptionTree leaf is empty does not contain only '
                                           'one key (plus transition): {}'.format(option_tree))
        try:
            (_, objects), = option_leaf.items()
        except TypeError:
            raise PyExpandObjectsTypeError("Invalid or missing BuildPath location: {}".format(option_tree))
        return {
            'objects': objects,
            'transitions': transitions
        }

    def _apply_transitions(self, option_tree_leaf):
        """
        Set object field values in an OptionTree branch (BuildPath, InsertElements, etc.)
        from Template inputs using Transitions dictionary

        :param option_tree_leaf: YAML loaded option tree end node with two keys: objects and transitions
        :return: dictionary of objects with transitions applied
        """
        option_tree_transitions = option_tree_leaf.pop('transitions', None)
        if option_tree_transitions:
            for template_field, transition_structure in option_tree_transitions.items():
                (object_type, object_field), = transition_structure.items()
                (leaf_option, super_objects), = option_tree_leaf.items()
                for super_object in super_objects:
                    (super_object_type, super_object_name), = super_object.items()
                    if re.match(object_type, super_object_type):
                        if 'Fields' in super_object[super_object_type].keys():
                            super_object[super_object_type]['Fields'][object_field] = \
                                self.template[self.template_name][template_field]
                        else:
                            super_object[super_object_type][object_field] = \
                                self.template[self.template_name][template_field]
        return option_tree_leaf

    def create_build_path(self):
        """
        Create a build path of EnergyPlus super objects for a given template

        :return:
        """
        # Get Base BuildPath and specific transitions (make generalized functions for other actions)
        # apply transition names and return the action or build path
        # Get each Remove/Insert/Etc actions
        # apply transition names to each
        # Perform insert/edit of build path for each action
        # Connect nodes on systems only (first object in list is connected for multi-object build path locations)
        return

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
        structure_object = self.get_structure(structure_hierarchy=structure_hierarchy)
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
        # todo_eo: pre-set template inputs with None?  Discuss advantages of pre-definition.
        # fill/create class attributes values with template inputs
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
            raise InvalidTemplateException(
                'No setpoints or schedules provided to HVACTemplate:Thermostat object: {}'.format(self.template_name))
        self.epjson = self.merge_epjson(
            super_dictionary=self.epjson,
            object_dictionary=thermostat_setpoint_object,
            unique_name_override=False
        )
        return

    def run(self):
        """
        Perform all template expansion operations and return the class to the parent calling function.
        :return: ExpandThermostat class with necessary attributes filled for output
        """
        self.create_and_set_schedules()
        self.create_thermostat_setpoints()
        return self


class ExpandSystem(ExpandObjects):
    """
    System expansion operations
    """
    def __init__(self, template):
        # fill/create class attributes values with template inputs
        super().__init__(template=template)
        return


class ExpandZone(ExpandObjects):
    """
    Zone expansion operations
    """
    def __init__(self, template):
        # fill/create class attributes values with template inputs
        super().__init__(template=template)
        return
