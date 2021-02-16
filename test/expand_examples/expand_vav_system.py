import yaml
import re
import copy
import argparse
import numbers
import sys
import typing
from pprint import pprint

test_epjson = {
    "HVACTemplate:System:VAV": {
        "VAV Sys 1": {
            "cooling_coil_design_setpoint": 12.8,
            "cooling_coil_setpoint_reset_type": "None",
            "cooling_coil_type": "ChilledWater",
            "dehumidification_control_type": "None",
            "dehumidification_setpoint": 60.0,
            "economizer_lockout": "NoLockout",
            "economizer_lower_temperature_limit": 4,
            "economizer_type": "DifferentialDryBulb",
            "economizer_upper_temperature_limit": 19,
            "gas_heating_coil_efficiency": 0.8,
            "gas_heating_coil_parasitic_electric_load": 0.0,
            "gas_preheat_coil_efficiency": 0.8,
            "gas_preheat_coil_parasitic_electric_load": 0.0,
            "heat_recovery_type": "None",
            "heating_coil_design_setpoint": 10.0,
            "heating_coil_setpoint_reset_type": "None",
            "heating_coil_type": "Electric",
            "humidifier_rated_capacity": 1e-06,
            "humidifier_rated_electric_power": 2690.0,
            "humidifier_setpoint": 30.0,
            "humidifier_type": "None",
            "latent_heat_recovery_effectiveness": 0.65,
            "maximum_outdoor_air_flow_rate": "Autosize",
            "minimum_outdoor_air_control_type": "FixedMinimum",
            "minimum_outdoor_air_flow_rate": "Autosize",
            "minimum_outdoor_air_schedule_name": "Min OA Sched",
            "night_cycle_control": "CycleOnAny",
            "preheat_coil_type": "Electric",
            "preheat_efficiency": 1,
            "return_plenum_name": "PLENUM-1",
            "sensible_heat_recovery_effectiveness": 0.7,
            "sizing_option": "NonCoincident",
            "supply_fan_delta_pressure": 600,
            "supply_fan_maximum_flow_rate": "Autosize",
            "supply_fan_minimum_flow_rate": "Autosize",
            "supply_fan_motor_efficiency": 0.9,
            "supply_fan_motor_in_air_stream_fraction": 1,
            "supply_fan_part_load_power_coefficients": "InletVaneDampers",
            "supply_fan_placement": "DrawThrough",
            "supply_fan_total_efficiency": 0.7,
            "system_availability_schedule_name": "FanAvailSched"
        }
    },
    "HVACTemplate:Zone:VAV": {
        "HVACTemplate:Zone:VAV 1": {
            "baseboard_heating_capacity": "Autosize",
            "baseboard_heating_type": "None",
            "constant_minimum_air_flow_fraction": 0.3,
            "damper_heating_action": "Reverse",
            "outdoor_air_flow_rate_per_person": 0.00944,
            "outdoor_air_flow_rate_per_zone": 0.0,
            "outdoor_air_flow_rate_per_zone_floor_area": 0.0,
            "outdoor_air_method": "Flow/Person",
            "reheat_coil_type": "HotWater",
            "supply_air_maximum_flow_rate": "Autosize",
            "template_thermostat_name": "All Zones",
            "template_vav_system_name": "VAV Sys 1",
            "zone_cooling_design_supply_air_temperature_input_method": "SystemSupplyAirTemperature",
            "zone_heating_design_supply_air_temperature": 50.0,
            "zone_heating_design_supply_air_temperature_input_method": "SupplyAirTemperature",
            "zone_minimum_air_flow_input_method": "Constant",
            "zone_name": "SPACE1-1"
        },
        "HVACTemplate:Zone:VAV 2": {
            "baseboard_heating_capacity": "Autosize",
            "baseboard_heating_type": "None",
            "constant_minimum_air_flow_fraction": 0.3,
            "damper_heating_action": "Reverse",
            "outdoor_air_flow_rate_per_person": 0.00944,
            "outdoor_air_flow_rate_per_zone": 0.0,
            "outdoor_air_flow_rate_per_zone_floor_area": 0.0,
            "outdoor_air_method": "Flow/Person",
            "reheat_coil_type": "None",
            "supply_air_maximum_flow_rate": "Autosize",
            "template_thermostat_name": "All Zones",
            "template_vav_system_name": "VAV Sys 1",
            "zone_cooling_design_supply_air_temperature_input_method": "SystemSupplyAirTemperature",
            "zone_heating_design_supply_air_temperature": 50.0,
            "zone_heating_design_supply_air_temperature_input_method": "SupplyAirTemperature",
            "zone_minimum_air_flow_input_method": "Constant",
            "zone_name": "SPACE1-2"
        }
    }
}


def build_parser():  # pragma: no cover
    """
    Build argument parser.
    """
    parser_object = argparse.ArgumentParser(
        prog='pyExpandObjects',
        description='Automated process that expands HVACTemplate objects into regular EnergyPlus objects.')
    parser_object.add_argument(
        "yaml_file",
        nargs='?',
        help='Paths of epJSON files to convert'
    )
    return parser_object


def flatten_build_path(build_path, flat_list=[], clear=True):
    """
    Flattens list of lists to one list of items.
    Due to way the BuildPath is structured, sub-lists
    are inserted from re-used objects, which makes this code
    necessary.

    This is a simple recursion function that iterates a list
    and if the element it grabs is a list, then iterates through
    that list.  Whenever a non-list element is found, it is appended
    to a flattened list object that is eventually returned.

    Clear is the option to restart flat_list.  Due to its recursive
    nature, the flat_list will continually append to the list in memory
    unless told to reset.
    """
    if clear:
        flat_list = []
    for i in build_path:
        if isinstance(i, list):
            flatten_build_path(i, flat_list, clear=False)
        else:
            flat_list.append(i)
    return flat_list


def replace_values(super_object: dict, text_replacement: dict) -> dict:
    """
    Replace the pre-set string values in an object to avoid duplications

    :param super_object: EnergyPlus super object
    :param text_replacement: string to replace with format brackets in the super object
        field values
    :return: super_object similar to the input, but with renamed string fields
    """
    if text_replacement:
        (energyplus_object_type, energyplus_object_constructors), = super_object.items()
        for field_name, field_value in energyplus_object_constructors['Fields'].items():
            super_object[energyplus_object_type]['Fields'][field_name] = field_value.replace(
                '{}',
                text_replacement
            )
    return super_object


def build_energyplus_object_from_complex_inputs(
        yaml_object: dict,
        energyplus_object_dictionary: dict,
        unique_name_input: str) -> typing.Tuple[str, dict]:
    """
    Builds an energyplus object from a yaml object which uses complex inputs.

    :param yaml_object: template yaml object in dictionary format
    :param energyplus_object_dictionary: epJSON formatted dictionary containing reference objects
    :param unique_name_input: string to convert text to unique name using an existing epJSON dictionary
        for a HVAC System

    :return: Valid epJSON key-value pair for an EnergyPlus Object - EnergyPlus Object, {field_names: field_values}
    """
    (energyplus_object_type, energyplus_object_constructors), = yaml_object.items()
    tmp_d = {}
    # if the value is a string or numeric, then it's a direct input.  If it is a dictionary
    # then the key-value pair is the object type and reference node holding the value to be input.
    # Anything else should return an error.
    for reference_field_name, object_node_reference in energyplus_object_constructors.items():
        if isinstance(object_node_reference, str):
            tmp_d[reference_field_name] = object_node_reference.format(unique_name_input)
        elif isinstance(object_node_reference, numbers.Number):
            tmp_d[reference_field_name] = object_node_reference
        elif isinstance(object_node_reference, dict):
            # Optional key 'Occurrence' can be used with the value being an integer.
            # {'Occurrence': N} is used to get nth match of the object_type search.
            object_occurrence = object_node_reference.pop('Occurrence', 1)
            (reference_object_type, reference_node), = object_node_reference.items()
            # Regular expression match the object type and the reference object type
            count_matches = 0
            for object_type in energyplus_object_dictionary.keys():
                if re.match(reference_object_type, object_type):
                    count_matches += 1
                    if count_matches == object_occurrence:
                        (energyplus_object_name, _), = energyplus_object_dictionary[object_type].items()
                        tmp_d[reference_field_name] = \
                            energyplus_object_dictionary[object_type][energyplus_object_name][reference_node]
        else:
            print('error')
    # Make a check that every reference node was applied
    key_val = tmp_d.pop('name')
    return energyplus_object_type, {key_val: tmp_d}


def get_option_tree(template_name: str, data: dict) -> dict:
    """
    Retrieve dictionary of alternate build instructions from yaml dictionary

    :param template_name: string value of HVACTemplate object
    :param data: yaml data in dictionary form
    :return: Dictionary of alternate build instructions
    """
    template_parse_regex = re.compile(r'HVACTemplate:(.*):(.*)')
    template_classes = re.match(template_parse_regex, template_name)
    # whenever getting values that you might edit later, use copy.deepcopy()
    # so a new dictionary is created; otherwise, every time you call that
    # value again the updated will be returned... even if you use .copy()
    yaml_option_tree = copy.deepcopy(data[':'.join(['OptionTree'])])
    option_tree = yaml_option_tree['HVACTemplate'][template_classes[1]][template_classes[2]]
    return option_tree


def get_action_field_names(action: str, option_tree: dict, template_dictionary: dict) -> typing.List[str]:
    # field names that cause a specified set of actions to be performed.
    # The yaml is structured so that each
    # the template object key value (e.g. heating_coil_type) triggers
    # an action.  The sub-objects in [Remove,Replace,Insert]Element
    # have keys that matches the options
    """
    Compare option_tree alternate build actions against the template inputs
    and return the field names when matched.

    :param action: 'Replace', 'Remove', or 'Insert' actions
    :param option_tree: Dictionary containing build path variations
    :param template_dictionary: Object containing the user-provided template inputs
    :return:
    """
    if option_tree.get(action):
        action_field_names = [
            field_name for field_name in template_dictionary.keys()
            if field_name in option_tree[action].keys()
        ]
    else:
        action_field_names = []
    return action_field_names


def get_all_action_field_names(option_tree: dict, template_dictionary: dict) -> dict:
    """
    Create dictionary of all actions to be performed, based on the template dictionary
    inputs and the given option_tree.

    :param option_tree: Dictionary containing build path variations
    :param template_dictionary: Object containing the user-provided template inputs
    :return: Dictionary containing remove, replace, and insert actions
    """
    remove_field_names = get_action_field_names(
        action='RemoveElements',
        option_tree=option_tree,
        template_dictionary=template_dictionary
    )
    replace_field_names = get_action_field_names(
        action='ReplaceElements',
        option_tree=option_tree,
        template_dictionary=template_dictionary
    )
    insert_field_names = get_action_field_names(
        action='InsertElements',
        option_tree=option_tree,
        template_dictionary=template_dictionary
    )
    return {
        'remove': remove_field_names,
        'replace': replace_field_names,
        'insert': insert_field_names
    }


def get_action_structure(
        action: str,
        action_list: typing.List[str],
        option_tree: dict,
        template_dictionary: dict) -> typing.Generator[int, str, dict]:
    """

    :param action: action to be performed
    :param action_list: list of field_names triggering actions
    :param option_tree: Dictionary containing build path variations
    :param template_dictionary: user-inputs in HVACTemplate object

    :return: Iterator of [EnergyPlus object reference, action_structure]
    """
    for field_name in action_list:
        # get the replacement subtree
        if option_tree[''.join([action.capitalize(), 'Elements'])].get(field_name) and \
                option_tree[''.join([action.capitalize(), 'Elements'])][field_name] \
                .get(template_dictionary[field_name]):
            objects_reference = \
                option_tree[''.join([action.capitalize(), 'Elements'])][field_name][template_dictionary[field_name]]
            # for each subtree reference (more than one can be done)
            for object_reference, option_structure in objects_reference.items():
                yield object_reference, option_structure


def remove_objects(
        action: str,
        action_list: typing.List[str],
        option_tree: dict,
        template_dictionary: dict,
        build_path: typing.List[dict]) -> typing.List[dict]:
    """
    Remove object in a flattened path using alternate build instructions

    :param action: action to be performed
    :param action_list: list of field_names triggering actions
    :param option_tree: Dictionary containing build path variations
    :param template_dictionary: user-inputs in HVACTemplate object
    :param build_path: list of EnergyPlus super objects in build order

    :return: build_path with replaced objects
    """
    object_references = get_action_structure(
        action=action,
        action_list=action_list,
        option_tree=option_tree,
        template_dictionary=template_dictionary)
    for remove_object_reference, remove_option_structure in object_references:
        count_matches = 0
        # If 'Occurrence' is specified, then only replace when that occurrence happens.
        remove_at_occurrence = remove_option_structure.get('Occurrence', 1)
        for idx, energyplus_super_object in enumerate(build_path):
            ############333
            # todo_eo: work from here
            # this zone type has two dictionary objects b/c heating coil is combined,
            # need to rewrite all insert, replace, remove code to account for this.
            (energyplus_object_type, _), = energyplus_super_object.items()
            if re.match(remove_object_reference, energyplus_object_type):
                count_matches += 1
                if count_matches == remove_at_occurrence:
                    build_path.pop(idx)
        # check if the number of matches actually met the occurrence threshold
        if not count_matches >= remove_at_occurrence:
            print('error')
            print('replace error')
            sys.exit()
    return build_path


def replace_objects(
        action: str,
        action_list: typing.List[str],
        option_tree: dict,
        template_dictionary: dict,
        build_path: typing.List[dict]) -> typing.List[dict]:
    """
    Replace object in a flattened path using alternate build instructions

    :param action: action to be performed
    :param action_list: list of field_names triggering actions
    :param option_tree: Dictionary containing build path variations
    :param template_dictionary: user-inputs in HVACTemplate object
    :param build_path: list of EnergyPlus super objects in build order

    :return: build_path with replaced objects
    """
    object_references = get_action_structure(
        action=action,
        action_list=action_list,
        option_tree=option_tree,
        template_dictionary=template_dictionary)
    for replace_object_reference, replace_option_structure in object_references:
        count_matches = 0
        # If 'Occurrence' is specified, then only replace when that occurrence happens.
        replace_at_occurrence = replace_option_structure.get('Occurrence', 1)
        for idx, energyplus_super_object in enumerate(build_path):
            (energyplus_object_type, _), = energyplus_super_object.items()
            if re.match(replace_object_reference, energyplus_object_type):
                count_matches += 1
                if count_matches == replace_at_occurrence:
                    # get object from template
                    new_object = copy.deepcopy(
                        replace_option_structure['Object']
                    )
                    # rename fields
                    replacement = (
                        replace_option_structure.get('FieldNameReplacement')
                    )
                    # rename if applicable
                    new_object = replace_values(
                        new_object,
                        replacement
                    )
                    # replace old object with new
                    build_path[idx] = new_object
        # check if the number of matches actually met the occurrence threshold
        if not count_matches >= replace_at_occurrence:
            print('error')
            print('replace error')
            sys.exit()
    return build_path


def apply_transitions_to_objects(
        transition_structure: dict,
        template_dictionary: dict,
        build_path: typing.Union[dict, typing.List[dict]]) -> typing.Union[dict, typing.List[dict]]:
    """
    Transfer user input data from HVACTemplate object to the objects in the build path.
    If a dictionary is passed, return a dictionary.  Otherwise return a list.

    :param transition_structure: transition key-value pairs for passing user input data
    :param template_dictionary: user-inputs in HVACTemplate object
    :param build_path: list of EnergyPlus super objects in build order

    :return: build_path with template input data transferred to objects
    """
    if isinstance(build_path, dict):
        as_object = True
        build_path = [build_path, ]
    else:
        as_object = False
    for transition_field_name, value_reference in transition_structure.items():
        for reference_energyplus_object_type, field_name in value_reference.items():
            for energyplus_super_object in build_path:
                # there should only be one key, so this method is used to unpack.
                (energyplus_object_type, _), = energyplus_super_object.items()
                if re.match(reference_energyplus_object_type, energyplus_object_type):
                    if not energyplus_super_object[energyplus_object_type]['Fields'].get(field_name):
                        energyplus_super_object[energyplus_object_type]['Fields'][field_name] = None
                    energyplus_super_object[energyplus_object_type]['Fields'][field_name] = (
                        template_dictionary[transition_field_name]
                    )
    if as_object:
        return build_path[0]
    else:
        return build_path


def insert_objects(
        action: str,
        action_list: typing.List[str],
        option_tree: dict,
        template_dictionary: dict,
        build_path: typing.List[dict]) -> typing.List[dict]:
    """
    Insert object in a flattened path using alternate build instructions

    :param action: action to be performed
    :param action_list: list of field_names triggering actions
    :param option_tree: Dictionary containing build path variations
    :param template_dictionary: user-inputs in HVACTemplate object
    :param build_path: list of EnergyPlus super objects in build order

    :return: build_path with replaced objects
    """
    object_references = get_action_structure(
        action=action,
        action_list=action_list,
        option_tree=option_tree,
        template_dictionary=template_dictionary)
    for insert_object_reference, insert_option_structure in object_references:
        # iterate over regex matches and do operations when the right occurrence happens
        count_matches = 0
        for idx, energyplus_super_object in enumerate(build_path):
            (energyplus_object_type, _), = energyplus_super_object.items()
            if re.match(insert_object_reference, energyplus_object_type):
                count_matches += 1
                if count_matches == insert_option_structure.get('Occurrence', 1):
                    # Look for 'BeforeObject' the 'After'.  Prevent inserting twice with check
                    # on reference_object
                    object_location_offset = insert_option_structure['Location']
                    insert_offset = None
                    if object_location_offset == 'After"':
                        insert_offset = 1
                    elif not insert_offset and object_location_offset == 'Before':
                        insert_offset = 0
                    else:
                        print("error")
                        print("insert location error")
                        sys.exit()
                    insert_location = idx + insert_offset
                    # get object to be inserted from yaml option tree
                    new_object = copy.deepcopy(
                        insert_option_structure['Object']
                    )
                    # get rename format
                    replacement = (
                        insert_option_structure.get('FieldNameReplacement')
                    )
                    # rename if possible
                    new_object = replace_values(
                        new_object,
                        replacement
                    )
                    # apply specific transitions
                    new_object = apply_transitions_to_objects(
                        transition_structure=insert_option_structure['Transitions'],
                        template_dictionary=template_dictionary,
                        build_path=new_object
                    )
                    build_path.insert(
                        insert_location,
                        new_object
                    )
        # check if the number of matches actually met the occurrence threshold
        if not count_matches >= insert_option_structure.get('Occurrence', 1):
            print('error')
            print('insert error')
            sys.exit()
    return build_path


def insert_unique_name(
        unique_name: str,
        build_path: typing.Union[dict, typing.List[dict]]) -> typing.Union[dict, typing.List[dict]]:
    """
    Insert a unique names string into field values where the format symbol '{}' is present.
    If a dictionary is passed, return a dictionary.  Otherwise return a list.

    :param unique_name: Unique name to be applied to string fields
    :param build_path: list of EnergyPlus super objects in build order

    :return: build_path of same structure with string fields formatted to have unqiue names
    """
    if isinstance(build_path, dict):
        as_object = True
        build_path = [build_path, ]
    else:
        as_object = False
    for energyplus_super_object in build_path:
        (energyplus_object_type, energyplus_object_constructors), = energyplus_super_object.items()
        for field_name, field_value in energyplus_object_constructors['Fields'].items():
            if isinstance(field_value, str):
                energyplus_super_object[energyplus_object_type]['Fields'][field_name] = \
                    field_value.format(unique_name)
    if as_object:
        return build_path[0]
    else:
        return build_path


def build_epjson(
        connector_path: str,
        build_path: typing.Union[dict, typing.List[dict]],
        epjson_object: dict = {}) -> dict:
    """
    Build epJSON formatted dictionary of EnergyPlus objects from super objects.

    :param epjson_object: epjson dictionary to pass for build.  Empty (new) if not specified
    :param connector_path: air, HotWater, ChilledWater, or MixedWater connectors to use
    :param build_path: list of EnergyPlus super objects in build order

    :return: epJSON formatted dictionary
    """
    if isinstance(build_path, dict):
        build_path = [build_path, ]
    out_node_name = None
    for idx, energyplus_super_object in enumerate(build_path):
        (energyplus_object_type, energyplus_object_constructors), = energyplus_super_object.items()
        # use copy so that the original structure is preserved for future queries
        tmp_d = copy.deepcopy(energyplus_object_constructors['Fields'])
        object_key = tmp_d.pop('name')
        # not necessary but it's a good reminder that this object is the target value
        object_values = tmp_d
        # create the object type if it doesn't exist
        if not epjson_object.get(energyplus_object_type):
            epjson_object[energyplus_object_type] = {}
        # for the first object, do not alter the input node name.
        # for subsequent objects, set the input node name value to the
        # output node name value of the previous object.
        if idx == 0:
            epjson_object[energyplus_object_type][object_key] = object_values
            out_node_name = (
                energyplus_object_constructors['Fields']
                [energyplus_object_constructors['Connectors'][connector_path.capitalize()]['Outlet']]
            )
        else:
            object_values[
                energyplus_object_constructors['Connectors'][connector_path.capitalize()]['Inlet']
            ] = out_node_name
            epjson_object[energyplus_object_type][object_key] = object_values
            out_node_name = (
                energyplus_object_constructors['Fields']
                [energyplus_object_constructors['Connectors'][connector_path.capitalize()]['Outlet']]
            )
    return epjson_object

# In this process note one import aspect. Specific field names are
# rarely used, if at all.  Most of the structure comes from the yaml
# object, which means that very little (comparatively)
# python code will need to be rewritten, i.e. this chunk should work for
# (hopefully) all HVACTemplate:System objects.  Possibly, most of the code
# could be reused for zone and water loop templates as well.


def main(input_args):
    with open(input_args.yaml_file, 'r') as f:
        # get yaml data
        data = yaml.load(f, Loader=yaml.FullLoader)
        # extract system template objects from epJSON
        system_templates = [i for i in test_epjson if i.startswith('HVACTemplate:System')]
        # iterate over templates
        for st in system_templates:
            # get template object as dictionary
            hvac_system_template_obj = test_epjson[st]
            for system_name, system_template_dictionary in hvac_system_template_obj.items():
                print('System Name')
                print(system_name)
                option_tree = get_option_tree(st, data)
                selected_template = option_tree['Base']
                print('selected_template')
                print(selected_template)
                actions = get_all_action_field_names(
                    option_tree=option_tree,
                    template_dictionary=system_template_dictionary
                )
                # a side effect of the yaml structure is that nested lists are produced
                # so we need to flatten them.
                flattened_path = flatten_build_path(selected_template['BuildPath'])
                print('pre-replaced element path')
                for idx, energyplus_super_object in enumerate(flattened_path):
                    print('object {} - {}'.format(idx, energyplus_super_object))
                # replace example
                # At the moment, replace happens even if correct equipment in place.
                # I'm sure there is a work-around to this but for now it doesn't break anything.
                if actions.get('replace'):
                    flattened_path = replace_objects(
                        action='replace',
                        action_list=actions['replace'],
                        option_tree=option_tree,
                        template_dictionary=system_template_dictionary,
                        build_path=flattened_path
                    )
                print('post-replaced path')
                for idx, energyplus_super_object in enumerate(flattened_path):
                    print('object {} - {}'.format(idx, energyplus_super_object))
                # apply base transitions.  This needs to be done before inserting optional elements.
                # If an element is inserted that is the same object type, then the transition mapping
                # would output to both objects.
                if selected_template.get('Transitions'):
                    flattened_path = apply_transitions_to_objects(
                        transition_structure=selected_template['Transitions'],
                        template_dictionary=system_template_dictionary,
                        build_path=flattened_path
                    )
                print('post-transition path')
                for idx, energyplus_super_object in enumerate(flattened_path):
                    print('object {} - {}'.format(idx, energyplus_super_object))
                # insert example
                if actions.get('insert'):
                    flattened_path = insert_objects(
                        action='insert',
                        action_list=actions['insert'],
                        option_tree=option_tree,
                        template_dictionary=system_template_dictionary,
                        build_path=flattened_path
                    )
                print('post-insert element path')
                for idx, energyplus_super_object in enumerate(flattened_path):
                    print('object {} - {}'.format(idx, energyplus_super_object))
                # insert system name
                flattened_path = insert_unique_name(
                    unique_name=system_name,
                    build_path=flattened_path
                )
                print('post-variable rename path')
                for idx, energyplus_super_object in enumerate(flattened_path):
                    print('object {} - {}'.format(idx, energyplus_super_object))
                # Build a dictionary of valid epJSON objects from constructors
                # from build path
                # need to check for unique names within objects when in production
                energyplus_epjson_object = build_epjson(
                    connector_path='air',
                    build_path=flattened_path
                )
                # build Controllers (if/else statements can be copied from Fortran code)
                # however, note that we can also call the build_path or the epJSON dictionary
                # now to make decisions as well
                # Mixed Air setpoint Manager
                setpoint_managers = copy.deepcopy(data['SetpointManagers'])
                energyplus_object, tmp_d = build_energyplus_object_from_complex_inputs(
                    copy.deepcopy(setpoint_managers['MixedAir']['Base']),
                    energyplus_epjson_object,
                    system_name
                )
                energyplus_epjson_object[energyplus_object] = tmp_d
                # build Controllers (if/else statements can be copied from Fortran code)
                # however, note that we can also call the build_path or the epJSON dictionary
                # now to make decisions as well
                controllers = copy.deepcopy(data['Controllers'])
                energyplus_object, tmp_d = build_energyplus_object_from_complex_inputs(
                    copy.deepcopy(controllers['OutdoorAir']['Base']),
                    energyplus_epjson_object,
                    system_name
                )
                energyplus_epjson_object[energyplus_object] = tmp_d
                print('Energyplus epJSON objects')
                pprint(energyplus_epjson_object, width=150)
                print('Supply Path outlet')
                for energyplus_arguments in flattened_path[-1].values():
                    last_node = energyplus_arguments['Fields'][energyplus_arguments['Connectors']['Air']['Outlet']]
                print(last_node)
                print('Supply Path inlet')
                (controller_reference_object_type, controller_reference_field_name), = \
                    selected_template['Connectors']['Supply']['Inlet'].items()
                (energyplus_object_name, _), = energyplus_epjson_object[controller_reference_object_type].items()
                print(
                    energyplus_epjson_object[controller_reference_object_type]
                    [energyplus_object_name][controller_reference_field_name]
                )
                print('Demand Path inlet')
                print(selected_template['Connectors']['Demand']['Inlet'].format(system_name))
                print('Demand Path outlet')
                print(selected_template['Connectors']['Demand']['Outlet'].format(system_name))
                # NodeLists, other controllers, etc. can be created based on logically parsing the epJSON object,
                # the super object, the flattened path, or any combination of these objects
                # OutdoorAir:Nodelist Example:
                (energyplus_object_type, energyplus_object_constructors), = flattened_path[0].items()
                # rename the inlet node to current conventions
                energyplus_epjson_object[energyplus_object_type][
                    energyplus_object_constructors['Fields']['name']]['air_inlet_node_name'] = \
                    '{} Outside Air Inlet'.format(system_name)
                # get the yaml object to construct
                outdoor_air_node_list = copy.deepcopy(data['OutdoorAir:NodeList']['Base'])
                # build object and add to dictionary
                (outdoor_air_node_list_object_type, _), = outdoor_air_node_list.items()
                energyplus_epjson_object[outdoor_air_node_list_object_type] = \
                    ['{} Outside Air Inlet'.format(system_name), ]
                print('epJSON with Nodelist')
                pprint(energyplus_epjson_object, width=150)
        # do zone builds in scope of the system build.  In production, these will be separate or child classes that
        # get system information when necessary.
        zone_templates = [i for i in test_epjson if i.startswith('HVACTemplate:Zone')]
        # iterate over templates
        for zt in zone_templates:
            # get template object as dictionary
            hvac_zone_template_obj = test_epjson[zt]
            for template_zone_name, zone_template_dictionary in hvac_zone_template_obj.items():
                print('##### New Zone Template #####')
                print('Zone Name')
                print(template_zone_name)
                option_tree = get_option_tree(zt, data)
                selected_template = option_tree['Base']
                print('selected_template')
                print(selected_template)
                # in cases where the template needs a whole new object, like vav w reheat vs no reheat, then a remove
                # all extraneous equipment, and then replace the terminal unit.
                # perform remove elements
                actions = get_all_action_field_names(
                    option_tree=option_tree,
                    template_dictionary=zone_template_dictionary
                )
                flattened_path = flatten_build_path(selected_template['BuildPath'])
                if actions.get('remove'):
                    flattened_path = remove_objects(
                        action='remove',
                        action_list=actions['remove'],
                        option_tree=option_tree,
                        template_dictionary=zone_template_dictionary,
                        build_path=flattened_path
                    )
    return


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    main(args)

##########################
# todo_eo: Remaining example buildout
##########################
# System ideas and cleanup
# Need to try better alignment to zone flexibility if possible.
##########################

################
# Zone equipment
################
# build paths can happen the same way; however, the zone coils make a parallel branch from an internal
# AirTerminal:* node that is merged to the AirTerminal output.  The build path can create all elements
# and populate the heating_coil_type field.  The program can then iterate over the list looking for
# these types of objects, identify the heating/cooling coil types and then insert a coil
#
# Need to figure out how to handle recirculation systems (e.g. PIU).  Maybe same way, just build a path then
# iterate back over for recirculation loops to be applied.
#
# Dual duct systems and zones may need their own build logic, as they are parallel air flow loops.
#############
# Plant Loops
#############
# Supply side should be similar to the HVACTemplate system build
# Demand side, loop through all objects in all air loops and set in a list.  Then, build loop for each object like
# how zones are created.
#######################
