import copy
import yaml
import re
from pathlib import Path
import numbers
import typing

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

    def flatten_list(
            self,
            nested_list: list,
            flat_list: list = [],
            clear: bool = True) -> list:
        """
        Flattens list of lists to one list of items.

        :param nested_list: list of nested dictionary objects
        :param flat_list: list used to store recursive addition of objects
        :param clear: Option to empty the recursive list
        :return: flattened list of objects
        """
        if clear:
            flat_list = []
        for i in nested_list:
            if isinstance(i, list):
                self.flatten_list(i, flat_list, clear=False)
            else:
                flat_list.append(i)
        return flat_list

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
            if key not in ['BuildPath', 'InsertObject', 'ReplaceObject', 'RemoveObject',
                           'BaseObjects', 'TemplateObjects']:
                raise PyExpandObjectsYamlStructureException(
                    "YAML object is incorrectly formatted: {}, bad key: {}".format(structure, key))
        return structure

    def _get_option_tree_objects(
            self,
            structure_hierarchy: list) -> dict:
        """
        Return objects from option tree leaf.

        :return: epJSON dictionary with unresolved complex inputs
        """
        option_tree = self.get_option_tree(structure_hierarchy=structure_hierarchy)
        options = option_tree.keys()
        option_tree_dictionary = {}
        if not set(list(options)).issubset({'BaseObjects', 'TemplateObjects', 'BuildPath'}):
            raise PyExpandObjectsYamlError("Invalid OptionTree leaf type provided in YAML: {}"
                                           .format(options))
        if 'BaseObjects' in options:
            option_tree_leaf = self._get_option_tree_leaf(
                option_tree=option_tree,
                leaf_path=['BaseObjects', ])
            object_list = self._apply_transitions(option_tree_leaf=option_tree_leaf)
            option_tree_dictionary = self.merge_epjson(
                super_dictionary=option_tree_dictionary,
                object_dictionary=self._yaml_list_to_epjson_dictionaries(object_list))
        if 'TemplateObjects' in options:
            for template_field, template_tree in option_tree['TemplateObjects'].items():
                (field_option, objects), = template_tree.items()
                if re.match(field_option, getattr(self, template_field)):
                    option_tree_leaf = self._get_option_tree_leaf(
                        option_tree=option_tree,
                        leaf_path=['TemplateObjects', template_field, getattr(self, template_field)])
                    object_list = self._apply_transitions(option_tree_leaf=option_tree_leaf)
                    option_tree_dictionary = self.merge_epjson(
                        super_dictionary=option_tree_dictionary,
                        object_dictionary=self._yaml_list_to_epjson_dictionaries(object_list))
        if "BuildPath" in options:
            # todo_eo: this location is the final output of BuildPath steps which return a list of yaml objects
            pass
        return option_tree_dictionary

    def _get_option_tree_leaf(
            self,
            option_tree: dict,
            leaf_path: list) -> dict:
        """
        Return leaf from OptionTree that has no template options (e.g. alternative options)

        :param option_tree: Yaml object holding HVACTemplate option tree
        :param leaf_path: path to leaf node of option tree
        :return: Verified BuildPath and Transition dictionary as keys in an object
        """
        option_leaf = self.get_structure(structure_hierarchy=leaf_path, structure=option_tree)
        transitions = option_leaf.pop('Transitions', None)
        try:
            objects = self.flatten_list(option_leaf['Objects'])
        except KeyError:
            raise PyExpandObjectsTypeError("Invalid or missing Objects location: {}".format(option_tree))
        return {
            'Objects': objects,
            'Transitions': transitions
        }

    def _apply_transitions(
            self,
            option_tree_leaf: dict) -> list:
        """
        Set object field values in an OptionTree leaf, which consist of an 'Objects' and 'Transitions' key
        using a supplied Transitions dictionary.

        :param option_tree_leaf: YAML loaded option tree end node with two keys: objects and transitions
        :return: list of dictionary objects with transitions applied
        """
        option_tree_transitions = option_tree_leaf.pop('Transitions', None)
        if option_tree_transitions:
            # iterate over the transitions instructions
            for template_field, transition_structure in option_tree_transitions.items():
                for object_type_reference, object_field in transition_structure.items():
                    # for each transition instruction, iterate over the objects and apply if the
                    # object_type matches
                    # Ensure there is only one object_key and it is 'Objects'
                    (object_key, tree_objects), = option_tree_leaf.items()
                    if not object_key == 'Objects':
                        raise PyExpandObjectsYamlError(
                            "Objects key missing from OptionTree leaf: {}".format(option_tree_leaf))
                    for tree_object in tree_objects:
                        for object_type, object_name in tree_object.items():
                            if re.match(object_type_reference, object_type):
                                # On a match, apply the field.  If the object is a 'super' object used in a
                                # BuildPath, then insert it in the 'Fields' dictionary.  Otherwise, insert it
                                # into the base level of the object.  The template field was loaded as a class
                                # attribute on initialization.
                                try:
                                    if 'Fields' in tree_object[object_type].keys():
                                        tree_object[object_type]['Fields'][object_field] = \
                                            getattr(self, template_field)
                                    else:
                                        tree_object[object_type][object_field] = \
                                            getattr(self, template_field)
                                except AttributeError:
                                    self.logger.warning("Template field ({}) was attempted to be applied "
                                                        "to object ({}) but was not present in template inputs"
                                                        .format(template_field, object_type))
        # merge list of objects with transitions applied into a single epJSON dictionary and return
        return option_tree_leaf['Objects']

    def _yaml_list_to_epjson_dictionaries(self, yaml_list):
        """
        Convert input YAML dictionaries into epJSON formatted dictionaries.

        YAML dictionaries can either be regular or 'super' objects which contain 'Fields' and 'Connectors'
        yaml_list: list of yaml objects to be formatted.
        :return: epJSON formatted dictionary
        """
        output_dictionary = {}
        for transitioned_object in yaml_list:
            try:
                (transitioned_object_type, transitioned_object_structure), = transitioned_object.items()
                # get the dictionary nested in 'Fields' for super objects
                if {"Connectors", "Fields"} == set(transitioned_object_structure.keys()):
                    object_name = transitioned_object_structure['Fields'].pop('name').format(self.template_name)
                    transitioned_object_structure = transitioned_object_structure['Fields']
                else:
                    object_name = transitioned_object_structure.pop('name').format(self.template_name)
                output_dictionary = self.merge_epjson(
                    super_dictionary=output_dictionary,
                    object_dictionary={transitioned_object_type: {object_name: transitioned_object_structure}}
                )
            except (TypeError, KeyError, ValueError):
                raise PyExpandObjectsYamlStructureException(
                    "YAML object is incorrectly formatted: {}".format(transitioned_object))
        return output_dictionary

    def _resolve_complex_input(
            self,
            epjson: dict,
            field_name: str,
            input_value: typing.Union[str, int, float, dict, list]) -> \
            typing.Generator[str, typing.Dict[str, str], None]:
        """
        Resolve a complex input into a field value

        :param epjson: epJSON dictionary of objects
        :param input_value: field value input
        :return: resolved field value
        """
        if isinstance(input_value, numbers.Number):
            yield {"field": field_name, "value": input_value}
        elif isinstance(input_value, str):
            yield {"field": field_name, "value": input_value.format(self.template_name)}
        elif isinstance(input_value, dict):
            # unpack the referenced object type and the lookup instructions
            (reference_object_type, lookup_instructions), = input_value.items()
            # try to match the reference object with EnergyPlus objects in the super_dictionary
            for object_type in epjson.keys():
                if re.match(reference_object_type, object_type):
                    # retrieve value
                    # if 'self' is used as the reference node, return the energyplus object type
                    # if 'key' is used as the reference node, return the unique object name
                    # After those checks, the lookup_instructions is the field name of the object.
                    (object_name, _), = epjson[object_type].items()
                    if lookup_instructions.lower() == 'self':
                        yield {"field": field_name, "value": object_type}
                    elif lookup_instructions.lower() == 'key':
                        yield {"field": field_name, "value": object_name}
                    elif isinstance(epjson[object_type][object_name][lookup_instructions], dict):
                        try:
                            complex_generator = self._resolve_complex_input(
                                epjson=epjson,
                                field_name=field_name,
                                input_value=epjson[object_type][object_name][lookup_instructions])
                            for cg in complex_generator:
                                yield cg
                        except RecursionError:
                            raise PyExpandObjectsYamlStructureException(
                                "Maximum Recursion limit exceeded when resolving {} for {}"
                                .format(input_value, field_name))
                    else:
                        yield {"field": field_name,
                               "value": epjson[object_type]
                               [object_name][lookup_instructions]}
        elif isinstance(input_value, list):
            try:
                tmp_list = []
                for input_list_item in input_value:
                    tmp_d = {}
                    for input_list_field, input_list_value in input_list_item.items():
                        complex_generator = self._resolve_complex_input(
                            epjson=epjson,
                            field_name=input_list_field,
                            input_value=input_list_value)
                        for cg in complex_generator:
                            tmp_d[cg["field"]] = cg["value"]
                        tmp_list.append(tmp_d)
                yield {"field": field_name, "value": tmp_list}
            except RecursionError:
                raise PyExpandObjectsYamlStructureException(
                    "Maximum Recursion limit exceeded when resolving {} for {}"
                    .format(input_value, field_name))
        return

    def _resolve_objects(self, epjson, reference_epjson=None):
        """
        Resolve complex inputs in epJSON formatted dictionary

        :param epjson: epJSON dictionary with complex inputs
        :param reference_epjson: (optional) epJSON dictionary to be used as reference objects for complex lookups.  If
            None, then the input epjson will be used
        :return: epJSON dictionary with values replacing complex inputs
        """
        if not reference_epjson:
            reference_epjson = copy.deepcopy(epjson)
        for object_type, object_structure in epjson.items():
            for object_name, object_fields in object_structure.items():
                for field_name, field_value in object_fields.items():
                    input_generator = self._resolve_complex_input(
                        epjson=reference_epjson,
                        field_name=field_name,
                        input_value=field_value)
                    for ig in input_generator:
                        object_fields[ig['field']] = ig['value']
        return epjson

    def _create_objects(self):
        """
        Create a set of EnergyPlus objects for a given template

        :return: epJSON dictionary and BuildPath (if applicable) as class attributes
        """
        # For systems, perform buildpath operations
        # BuildPath stored as a list of objects and dictionary in class attributes. List is necessary for future lookups
        # systems - get BuildPath
        # systems - perform insert/remove/etc. operations
        # systems - connect nodes and convert field values using name formatting and complex input operations
        # systems - return list of objects created from BuildPath saved separately for future reference
        # Get BaseObjects and Template objects, applying transitions from template before returning YAML objects
        structure_hierarchy = self.template_type.split(':')
        epjson = self._get_option_tree_objects(structure_hierarchy=structure_hierarchy)
        # Convert field values using name formatting and complex input operations
        self.epjson = self._resolve_objects(epjson)
        # store final values in self.epjson
        # Perform connections, put functions in child classes
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

    def run(self):
        """
        Process zone template
        :return: epJSON dictionary as class attribute
        """
        self._create_objects()
        return
