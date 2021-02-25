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
            # "zone_cooling_design_supply_air_temperature": 22,
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
    },
    "HVACTemplate:Plant:ChilledWaterLoop": {
        "Chilled Water Loop": {
            "chilled_water_design_setpoint": 7.22,
            "chilled_water_pump_configuration": "ConstantPrimaryNoSecondary",
            "chilled_water_reset_outdoor_dry_bulb_high": 26.7,
            "chilled_water_reset_outdoor_dry_bulb_low": 15.6,
            "chilled_water_setpoint_at_outdoor_dry_bulb_high": 6.7,
            "chilled_water_setpoint_at_outdoor_dry_bulb_low": 12.2,
            "chilled_water_setpoint_reset_type": "None",
            "chiller_plant_operation_scheme_type": "Default",
            "condenser_plant_operation_scheme_type": "Default",
            "condenser_water_design_setpoint": 29.4,
            "condenser_water_pump_rated_head": 179352,
            "minimum_outdoor_dry_bulb_temperature": 7.22,
            "primary_chilled_water_pump_rated_head": 179352,
            "pump_control_type": "Intermittent",
            "secondary_chilled_water_pump_rated_head": 179352
        }
    },
    "HVACTemplate:Plant:Chiller": {
        "Main Chiller": {
            "capacity": "Autosize",
            "chiller_type": "ElectricReciprocatingChiller",
            "condenser_type": "WaterCooled",
            "nominal_cop": 3.2,
            "priority": "1"
        }
    },
    "HVACTemplate:Plant:Tower": {
        "Main Tower": {
            "free_convection_capacity": "Autosize",
            "high_speed_fan_power": "Autosize",
            "high_speed_nominal_capacity": "Autosize",
            "low_speed_fan_power": "Autosize",
            "low_speed_nominal_capacity": "Autosize",
            "priority": "1",
            "tower_type": "SingleSpeed"
        }
    },
    "HVACTemplate:Thermostat": {
        "All Zones": {
            "constant_heating_setpoint": 12,
            # "cooling_setpoint_schedule_name": "Clg-SetP-Sch",
            # "heating_setpoint_schedule_name": "Htg-SetP-Sch"
        }
    },
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


def flatten_build_path(
        build_path: list,
        flat_list: list = [],
        clear: bool = True) -> list:
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

    :param build_path: list of nested dictionary objects
    :param flat_list: list used to store recursive addition of objects
    :param clear: Option to empty the recursive list
    :return: flattened list of objects in the build_path
    """
    if clear:
        flat_list = []
    for i in build_path:
        if isinstance(i, list):
            flatten_build_path(i, flat_list, clear=False)
        else:
            flat_list.append(i)
    return flat_list


def replace_values(
        super_object: dict,
        text_replacement: dict) -> dict:
    """
    Replace the pre-set string values in an object to avoid duplications.
    For example, '{}' can be replaced with '{} New Text'.  These fields will still contain
    the string formatting brackets for further manipulation.

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


def process_complex_inputs(
        energyplus_object_dictionary,
        object_node_reference,
        unique_name_input,
        reference_field_name):
    # if the value is a string or numeric, then it's a direct input.  If it is a dictionary
    # then the key-value pair is the object type and reference node holding the value to be input.
    # If it is a list, then the object will be iterated for each and the same process applied recursively
    # Anything else should return an error.
    if isinstance(object_node_reference, str):
        yield {"field": reference_field_name, "value": object_node_reference.format(unique_name_input)}
    elif isinstance(object_node_reference, numbers.Number):
        yield {"field": reference_field_name, "value": object_node_reference}
    elif isinstance(object_node_reference, dict):
        # Optional key 'Occurrence' can be used with the value being an integer.
        # {'Occurrence': N} is used to get nth match of the object_type search.
        object_occurrence = object_node_reference.pop('Occurrence', 1)
        (reference_object_type, reference_node), = object_node_reference.items()
        # Regular expression match the object type and the reference object type
        count_matches = 0
        for object_type in energyplus_object_dictionary.keys():
            if re.match(reference_object_type, object_type, re.IGNORECASE):
                count_matches += 1
                if count_matches == object_occurrence:
                    (energyplus_object_name, _), = energyplus_object_dictionary[object_type].items()
                    # if 'self' is used as the reference node, just return the energyplus object type
                    # if 'key' is used as the reference node, just get the unique object name
                    if reference_node.lower() == 'self':
                        yield {"field": reference_field_name, "value": object_type}
                    elif reference_node.lower() == 'key':
                        yield {"field": reference_field_name, "value": energyplus_object_name}
                    else:
                        yield {"field": reference_field_name,
                               "value": energyplus_object_dictionary[object_type]
                               [energyplus_object_name][reference_node]}
    # if a list is provided, then recursively apply the function
    elif isinstance(object_node_reference, list):
        onr_list = []
        for onr in object_node_reference:
            (onr_field_name, onr_sub_object_structure), = onr.items()
            onr_generator = process_complex_inputs(
                energyplus_object_dictionary,
                onr_sub_object_structure,
                unique_name_input,
                onr_field_name)
            for onr_yield_val in onr_generator:
                onr_list.append({onr_yield_val["field"]: onr_yield_val["value"]})
        yield {"field": reference_field_name, "value": onr_list}
    else:
        print('error')
    return


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
    for reference_field_name, object_node_reference in energyplus_object_constructors.items():
        processed_inputs = process_complex_inputs(
            energyplus_object_dictionary,
            object_node_reference,
            unique_name_input,
            reference_field_name)
        for pd in processed_inputs:
            tmp_d[pd["field"]] = pd["value"]
    # Make a check that every reference node was applied
    key_val = tmp_d.pop('name')
    return energyplus_object_type, {key_val: tmp_d}


def get_option_tree(template_name: str, data: dict) -> dict:
    """
    Retrieve dictionary of alternate build instructions from yaml object 'OptionTree'

    :param template_name: string value of HVACTemplate object
    :param data: yaml data in dictionary form
    :return: Dictionary of alternate build instructions
    """
    template_parse_regex = re.compile(r'HVACTemplate:(.*):(.*)', re.IGNORECASE)
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
    Some HVACTemplate field selections require alternative build operations to be performed from the
    base path.  This function creates a list of the field names that cause an alternative build for
    a specified action.

    :param action: 'Replace', 'Remove', or 'Insert' actions
    :param option_tree: Dictionary containing build path variations
    :param template_dictionary: Object containing the user-provided template inputs
    :return: list of field names that trigger the specified action
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
        'insert': insert_field_names}


def get_action_structure(
        action: str,
        action_list: typing.List[str],
        option_tree: dict,
        template_dictionary: dict) -> typing.Generator[int, str, dict]:
    """
    Create a generator that yields an object reference and structure for actions to be performed.
    The object reference may either be a string value of an object type or regular expression.  The
    option structure is the object containing the details for the action to be performed.

    :param action: action to be performed
    :param action_list: list of field_names triggering actions
    :param option_tree: Dictionary containing build path variations
    :param template_dictionary: user-inputs in HVACTemplate object
    :return: Iterator of [EnergyPlus object reference, action_structure]
    """
    # capitalize action
    action = action[0].upper() + action[1:]
    for field_name in action_list:
        # get the replacement subtree
        if option_tree[''.join([action, 'Elements'])].get(field_name) and \
                option_tree[''.join([action, 'Elements'])][field_name] \
                .get(template_dictionary[field_name]):
            objects_reference = \
                option_tree[''.join([action, 'Elements'])][field_name][template_dictionary[field_name]]
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
            for energyplus_object_type in energyplus_super_object.keys():
                if re.match(remove_object_reference, energyplus_object_type, re.IGNORECASE):
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
            for energyplus_object_type in energyplus_super_object.keys():
                if re.match(replace_object_reference, energyplus_object_type, re.IGNORECASE):
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


def perform_build_path(
        connector_path: str,
        option_tree: dict,
        template_dictionary: dict,
        super_dictionary: dict,
        unique_name: str,
        **kwargs) -> typing.List[dict]:
    """
    Perform operations to create a build_path, which is a list of EnergyPlus
    super objects.  These super objects are dictionaries that contain two sub-keys:
      - Fields: The key-value pairs for field names and their values
      - Connectors: Information regarding the input and output nodes for each ConnectorPath,
        which is the fluid flow loop (Air, ChilledWaterLoop, HotWaterLoop).

    :param connector_path: fluid flow loop to follow.  Necessary for recursive call to perform_build_operations
    :param option_tree: yaml OptionTree
    :param template_dictionary: template field names and values
    :param super_dictionary: High level dictionary used for writing output. The instantiation of this objects needs
      to be outside the scope of the function due to recursive operations.
    :param unique_name: unique value to be applied to fields
    :param kwargs:
    :return: build_path for a chosen fluid flow loop, which is a list of super objects
    """
    # capitalize connector path
    connector_path = connector_path[0].upper() + connector_path[1:]
    selected_template = option_tree['Base']
    print('### selected template ###')
    print(selected_template)
    # a side effect of the yaml structure is that nested lists are produced
    # so we need to flatten them.
    build_path = flatten_build_path(selected_template['BuildPath'])
    # check for nested HVACTemplate objects.  They will appear as string objects with the
    # template name (e.g. HVACTemplate:Plant:Chiller).
    # if so do a recursive build on that object, insert it into the original position, and then flatten the
    # build path again.
    for idx, energyplus_super_object in enumerate(build_path):
        if isinstance(energyplus_super_object, str) and \
                re.match('^HVACTemplate:.*', energyplus_super_object, re.IGNORECASE):
            # in this test program, we have to grab global objects, which are the yaml data and the
            # epjson object.  In production, these should be stored class attributes.
            sub_data = kwargs['data']
            sub_template_object = test_epjson[energyplus_super_object]
            sub_build_path = None
            for sub_object_name, sub_object_dictionary in sub_template_object.items():
                sub_option_tree = get_option_tree(energyplus_super_object, sub_data)
                _, sub_build_path = perform_build_operations(
                    connector_path=connector_path,
                    option_tree=sub_option_tree,
                    template_dictionary=sub_object_dictionary,
                    super_dictionary=super_dictionary,
                    unique_name=sub_object_name,
                    **kwargs)
            build_path[idx] = sub_build_path
            build_path = flatten_build_path(build_path)
    actions = get_all_action_field_names(
        option_tree=option_tree,
        template_dictionary=template_dictionary
    )
    print('pre-replaced element path')
    for idx, energyplus_super_object in enumerate(build_path):
        print('object {} - {}'.format(idx, energyplus_super_object))
    # remove example
    if actions.get('remove'):
        build_path = remove_objects(
            action='remove',
            action_list=actions['remove'],
            option_tree=option_tree,
            template_dictionary=template_dictionary,
            build_path=build_path
        )
    print('post-removed path')
    for idx, energyplus_super_object in enumerate(build_path):
        print('object {} - {}'.format(idx, energyplus_super_object))
    # replace example
    # At the moment, replace happens even if correct equipment in place.
    # I'm sure there is a work-around to this but for now it doesn't break anything.
    if actions.get('replace'):
        build_path = replace_objects(
            action='replace',
            action_list=actions['replace'],
            option_tree=option_tree,
            template_dictionary=template_dictionary,
            build_path=build_path
        )
    print('post-replaced path')
    for idx, energyplus_super_object in enumerate(build_path):
        print('object {} - {}'.format(idx, energyplus_super_object))
    # apply base transitions.  This needs to be done before inserting optional elements.
    # If an element is inserted that is the same object type, then the transition mapping
    # would output to both objects.
    if selected_template.get('Transitions'):
        build_path = apply_transitions_to_objects(
            transition_structure=selected_template['Transitions'],
            template_dictionary=template_dictionary,
            build_path=build_path
        )
    print('post-transition path')
    for idx, energyplus_super_object in enumerate(build_path):
        print('object {} - {}'.format(idx, energyplus_super_object))
    # insert example
    if actions.get('insert'):
        build_path = insert_objects(
            action='insert',
            action_list=actions['insert'],
            option_tree=option_tree,
            template_dictionary=template_dictionary,
            build_path=build_path
        )
    print('post-insert element path')
    for idx, energyplus_super_object in enumerate(build_path):
        print('object {} - {}'.format(idx, energyplus_super_object))
    # insert system name
    build_path = insert_unique_name(
        unique_name=unique_name,
        build_path=build_path
    )
    return build_path


def merge_dictionaries(
        super_dictionary: dict,
        object_dictionary: dict,
        unique_name_override: bool = True) -> dict:
    """
    Merge a high level dictionary with a sub-dictionary

    :param super_dictionary: High level dictionary used as the base object
    :param object_dictionary: dictionary to merge into base object
    :param unique_name_override: allow a duplicate unique name to overwrite an existing object
    :return: merged output of the two input dictionaries
    """
    for energyplus_object_type, tmp_d in object_dictionary.items():
        if not super_dictionary.get(energyplus_object_type):
            super_dictionary[energyplus_object_type] = {}
        if isinstance(tmp_d, dict):
            for object_name, object_fields in tmp_d.items():
                if not unique_name_override and object_name in super_dictionary[energyplus_object_type].keys():
                    print('unique name error')
                    sys.exit()
            for tmp_d_name, tmp_d_structure in tmp_d.items():
                super_dictionary[energyplus_object_type][tmp_d_name] = tmp_d_structure
        elif isinstance(tmp_d, list):
            super_dictionary[energyplus_object_type] = tmp_d
    return super_dictionary


def perform_build_operations(
        connector_path: str,
        option_tree: dict,
        template_dictionary: dict,
        super_dictionary: dict,
        unique_name: str,
        **kwargs) -> typing.Tuple[dict, typing.List[dict]]:
    """
    Perform operations to create a build_path and create an epJSON object from that output.

    :param connector_path: fluid flow loop to follow.
    :param option_tree: Alternative build instruction object in yaml OptionTree
    :param template_dictionary:
    :param super_dictionary:
    :param unique_name:
    :param kwargs:
    :return:
    """
    build_path = perform_build_path(
        connector_path=connector_path,
        option_tree=option_tree,
        template_dictionary=template_dictionary,
        super_dictionary=super_dictionary,
        unique_name=unique_name,
        **kwargs
    )
    print('BuldPath complete')
    print(build_path)
    print('post-variable rename path')
    for idx, energyplus_super_object in enumerate(build_path):
        print('object {} - {}'.format(idx, energyplus_super_object))
    # Build a dictionary of valid epJSON objects from constructors
    # from build path
    object_from_path = build_epjson(
        connector_path=connector_path,
        unique_name=unique_name,
        build_path=build_path
    )
    super_dictionary = merge_dictionaries(
        super_dictionary=super_dictionary,
        object_dictionary=object_from_path,
        unique_name_override=True)
    # build additional objects (e.g. Controllers)
    # these are stored in the option tree under AdditionalObjects
    # for standard objects, and AdditionalTemplateObjects for
    # template triggered objects
    additional_objects = build_additional_objects(
        option_tree=option_tree,
        connector_path=connector_path,
        super_dictionary=super_dictionary,
        unique_name=unique_name,
        template_dictionary=template_dictionary,
        **kwargs
    )
    super_dictionary = merge_dictionaries(
        super_dictionary=super_dictionary,
        object_dictionary=additional_objects,
        unique_name_override=True)
    return super_dictionary, build_path


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
                for energyplus_object_type in energyplus_super_object:
                    if re.match(reference_energyplus_object_type, energyplus_object_type, re.IGNORECASE):
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
            for energyplus_object_type in energyplus_super_object.keys():
                if re.match(insert_object_reference, energyplus_object_type, re.IGNORECASE):
                    count_matches += 1
                    if count_matches == insert_option_structure.get('Occurrence', 1):
                        # Look for 'BeforeObject' the 'After'.  Prevent inserting twice with check
                        # on reference_object
                        object_location_offset = insert_option_structure['Location']
                        insert_offset = None
                        if object_location_offset.capitalize() == 'After"':
                            insert_offset = 1
                        elif not insert_offset and object_location_offset.capitalize() == 'Before':
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
                        transition_structure = insert_option_structure.pop('Transitions', None)
                        if transition_structure:
                            for sub_object_type, sub_object_structure in new_object.items():
                                for sub_object_name, sub_object_fields in sub_object_structure.items():
                                    # This is similar to the additional object method of inserting transitions
                                    # however, the object here is a super object, not an additional object, so it
                                    # has an extra level of Fields/Connectors.
                                    # it could be refactored with an optional flag
                                    if sub_object_name.capitalize() == 'Fields':
                                        for sub_template_field, object_field in transition_structure.items():
                                            new_object[sub_object_type][sub_object_name][object_field] = \
                                                template_dictionary[sub_template_field]
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
        for energyplus_object_type, energyplus_object_constructors in energyplus_super_object.items():
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
        unique_name: str,
        build_path: typing.Union[dict, typing.List[dict]]) -> dict:
    """
    Build epJSON formatted dictionary of EnergyPlus objects from super objects.

    :param connector_path: air, HotWater, ChilledWater, or MixedWater connectors to use
    :param unique_name: unique name string.
    :param build_path: list of EnergyPlus super objects in build order

    :return: epJSON formatted dictionary
    """
    # capitalize connector path
    connector_path = connector_path[0].upper() + connector_path[1:]
    if isinstance(build_path, dict):
        build_path = [build_path, ]
    out_node_name = None
    epjson_object = {}
    for idx, energyplus_super_object in enumerate(build_path):
        # store object key and make sure not in list as you iterate:
        unique_object_names = []
        for energyplus_object_type, energyplus_object_constructors in energyplus_super_object.items():
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
            # also check for duplicates
            if object_key in unique_object_names:
                print('non-unique object error')
                sys.exit()
            unique_object_names.append(object_key)
            if energyplus_object_constructors.get('Connectors'):
                # todo_eo need to work this over for bypass (and other parallel equipment) to not be included in
                # the node name handoff
                # the easiest thing to do is to probably rewrite the process to also take lists and get the first
                # object if that is the case.
                # If the constructor has a None value, then it is just there for branch build
                if energyplus_object_constructors['Connectors'][connector_path].get('UseInBuildPath', True):
                    if idx == 0:
                        epjson_object[energyplus_object_type][object_key] = object_values
                        out_node = energyplus_object_constructors['Connectors'][connector_path]['Outlet']
                        if isinstance(out_node, str) and '{}' in out_node:
                            out_node_name = out_node.format(unique_name)
                        else:
                            out_node_name = (
                                energyplus_object_constructors['Fields']
                                [energyplus_object_constructors['Connectors'][connector_path]['Outlet']]
                            )
                    else:
                        object_values[
                            energyplus_object_constructors['Connectors'][connector_path]['Inlet']
                        ] = out_node_name
                        epjson_object[energyplus_object_type][object_key] = object_values
                        out_node = energyplus_object_constructors['Connectors'][connector_path]['Outlet']
                        if isinstance(out_node, str) and '{}' in out_node:
                            out_node_name = out_node.format(unique_name)
                        else:
                            out_node_name = (
                                energyplus_object_constructors['Fields']
                                [energyplus_object_constructors['Connectors'][connector_path]['Outlet']]
                            )
                else:
                    epjson_object[energyplus_object_type][object_key] = object_values
            else:
                epjson_object[energyplus_object_type][object_key] = object_values
    return epjson_object


def process_additional_object_input(
        object_or_template,
        object_structure,
        connector_path,
        super_dictionary,
        unique_name,
        **kwargs):
    object_dictionary = {}
    if not object_or_template.startswith('HVACTemplate'):
        additional_object = {object_or_template: object_structure}
        for additional_sub_object, additional_sub_object_fields in additional_object.items():
            energyplus_object, tmp_d = build_energyplus_object_from_complex_inputs(
                yaml_object={additional_sub_object: copy.deepcopy(additional_sub_object_fields)},
                energyplus_object_dictionary=super_dictionary,
                unique_name_input=unique_name
            )
            if not object_dictionary.get(energyplus_object):
                object_dictionary[energyplus_object] = {}
            for object_name, object_fields in tmp_d.items():
                if object_name in object_dictionary[energyplus_object].keys():
                    print('unique name error')
                    sys.exit()
            object_dictionary[energyplus_object] = tmp_d
    # if the object is just a string, it should be for an HVACTemplate OptionTree build.
    # The key is the unique name modifier
    elif object_or_template.startswith('HVACTemplate'):
        # in this test program, we have to grab global objects, which are the yaml data and the
        # epjson object.  In production, these should be stored class attributes.
        sub_data = kwargs['data']
        sub_template_object = test_epjson.get(object_or_template)
        # some internal yaml templates are not accessible via EnergyPlus, so they will not have
        # a json input
        sub_option_tree = get_option_tree(object_or_template, sub_data)
        if isinstance(sub_template_object, dict):
            for sub_object_name, sub_object_dictionary in sub_template_object.items():
                energyplus_epjson_objects, _ = perform_build_operations(
                    connector_path=object_structure.get('ConnectorPath', connector_path),
                    option_tree=sub_option_tree,
                    template_dictionary=sub_object_dictionary,
                    super_dictionary=super_dictionary,
                    unique_name=object_structure['UniqueName'],
                    data=sub_data
                )
                for energyplus_object, tmp_d in energyplus_epjson_objects.items():
                    if not object_dictionary.get(energyplus_object):
                        object_dictionary[energyplus_object] = {}
                    for object_name, object_fields in tmp_d.items():
                        if object_name in object_dictionary[energyplus_object].keys():
                            print('unique name error')
                            sys.exit()
                    object_dictionary[energyplus_object] = tmp_d
        else:
            # for now, just specify the connector_path.  Will have to make a mapping dictionary later
            energyplus_epjson_objects, _ = perform_build_operations(
                connector_path=object_structure.get('ConnectorPath', connector_path),
                option_tree=sub_option_tree,
                template_dictionary={},
                super_dictionary=super_dictionary,
                unique_name=object_structure['UniqueName'],
                data=sub_data
            )
            object_dictionary = merge_dictionaries(
                super_dictionary=object_dictionary,
                object_dictionary=energyplus_epjson_objects,
                unique_name_override=False)
    else:
        print('value was not additional object key nor an HVACTemplate string')
        sys.exit()
    return object_dictionary


def build_additional_objects(
        option_tree: dict,
        super_dictionary: dict,
        connector_path: str,
        unique_name: str,
        template_dictionary: dict,
        **kwargs) -> dict:
    """
    Build additional objects in option tree

    :param option_tree: Dictionary containing build path variations
    :param super_dictionary: epjson dictionary of EnergyPlus objects
    :param connector_path: connector path name to use
    :param unique_name: unique name string
    :param template_dictionary: input HVACTemplate object
    :return:
    """
    object_dictionary = {}
    if option_tree.get('AdditionalObjects'):
        # check if additional object iterator is a energyplus object key or an HVACTemplate object key.
        for new_object_structure in option_tree['AdditionalObjects']:
            for object_or_template, object_structure in new_object_structure.items():
                # check for transitions and pop them if present
                transition_structure = object_structure.pop('Transitions', None)
                sub_object_dictionary = process_additional_object_input(
                    object_or_template=object_or_template,
                    object_structure=object_structure,
                    option_tree=option_tree,
                    connector_path=connector_path,
                    super_dictionary=super_dictionary,
                    # energyplus_object_dictionary=energyplus_object_dictionary,
                    unique_name=unique_name,
                    **kwargs
                )
                # apply transition fields
                if transition_structure:
                    for sub_object_type, sub_object_structure in sub_object_dictionary.items():
                        tmp_d = {}
                        for sub_object_name, sub_object_fields in sub_object_structure.items():
                            # apply all base fields and values to object before transition
                            for field, value in sub_object_fields.items():
                                tmp_d[field] = value
                            # overwrite, or add, fields and values to object
                            for sub_template_field, object_field in transition_structure.items():
                                if template_dictionary.get(sub_template_field):
                                    tmp_d[object_field] = template_dictionary[sub_template_field]
                            sub_object_dictionary[sub_object_type][sub_object_name] = tmp_d
                object_dictionary = merge_dictionaries(
                    super_dictionary=object_dictionary,
                    object_dictionary=sub_object_dictionary,
                    unique_name_override=True)
    if option_tree.get('AdditionalTemplateObjects'):
        for template_field, template_structure in option_tree['AdditionalTemplateObjects'].items():
            for template_option, add_object_structure in template_structure.items():
                if template_dictionary.get(template_field):
                    if re.match(template_option, template_dictionary[template_field]):
                        for new_object_structure in add_object_structure:
                            for object_or_template, object_structure in new_object_structure.items():
                                # check for transitions and pop them if present
                                transition_structure = object_structure.pop('Transitions', None)
                                sub_object_dictionary = process_additional_object_input(
                                    object_or_template=object_or_template,
                                    object_structure=object_structure,
                                    option_tree=option_tree,
                                    connector_path=connector_path,
                                    super_dictionary=super_dictionary,
                                    # energyplus_object_dictionary=energyplus_object_dictionary,
                                    unique_name=unique_name,
                                    **kwargs
                                )
                                # apply transition fields
                                if transition_structure:
                                    for sub_object_type, sub_object_structure in sub_object_dictionary.items():
                                        tmp_d = {}
                                        for sub_object_name, sub_object_fields in sub_object_structure.items():
                                            # apply all base fields and values to object before transition
                                            for field, value in sub_object_fields.items():
                                                tmp_d[field] = value
                                            # overwrite, or add, fields and values to object
                                            for sub_template_field, object_field in transition_structure.items():
                                                if template_dictionary.get(sub_template_field):
                                                    tmp_d[object_field] = template_dictionary[sub_template_field]
                                            sub_object_dictionary[sub_object_type][sub_object_name] = tmp_d
                                object_dictionary = merge_dictionaries(
                                    super_dictionary=object_dictionary,
                                    object_dictionary=sub_object_dictionary,
                                    unique_name_override=True)
    return object_dictionary


def build_compact_schedule(data, schedule_type, insert_values: typing.Union[int, str, list]):
    """
    Create compact schedule from specified yaml object and value
    :return:
    """
    if not isinstance(insert_values, list):
        insert_values = [insert_values, ]
    schedule_object = {'Schedule:Compact': {}}
    always_temperature_object = copy.deepcopy(data['Schedule']['Compact'][schedule_type])
    formatted_data_lines = [
        float(i.format(*insert_values))
        if re.match(r'.*{.*}', i, re.IGNORECASE) else i
        for i in always_temperature_object['data']]
    schedule_object['Schedule:Compact'][always_temperature_object['name'].format(insert_values[0])] = \
        formatted_data_lines
    return schedule_object


def build_thermostats(
        super_dictionary,
        template_dictionary,
        thermostat_name,
        **kwargs):
    """
    Create thermostat objects and associated equipment

    :param super_dictionary: Dictionary of thermostat objects
    :param template_dictionary: Dictionary of template fields
    :param thermostat_name: unique name of thermostat object
    :return:
    """
    # Do simple if-else statements to find the right thermostat type, then write it to an object dictionary.
    # it's easier to just construct thermostats from if-else statements than to build an alternate
    # yaml hierarchy.
    thermostat_options_object = {
        'heating_schedule': template_dictionary.get('heating_setpoint_schedule_name'),
        'constant_heating_setpoint': template_dictionary.get('constant_heating_setpoint'),
        'cooling_schedule': template_dictionary.get('cooling_setpoint_schedule_name'),
        'constant_cooling_setpoint': template_dictionary.get('constant_cooling_setpoint')
    }
    schedule_objects = []
    for thermostat_type in ['heating', 'cooling']:
        # build constant setpoints into schedule.  make error if both type specified:
        if thermostat_options_object.get('constant_{}_setpoint'.format(thermostat_type)):
            if not thermostat_options_object.get('{}_schedule'.format(thermostat_type)):
                # create thermostat schedules and save them to temporary dictionaries
                schedule_object = build_compact_schedule(
                    data=kwargs['data'],
                    schedule_type='ALWAYS_VAL',
                    insert_values=template_dictionary['constant_{}_setpoint'.format(thermostat_type)]
                )
                schedule_objects.append(schedule_object)
                # apply new schedule to the thermostat object
                thermostat_options_object['{}_schedule'.format(thermostat_type)] = \
                    'ALWAYS_{}'.format(thermostat_options_object['constant_{}_setpoint'.format(thermostat_type)])
            else:
                print('schedule error')
                sys.exit()
    # create thermostat object type based on which inputs were provided.
    thermostat_object = {}
    if thermostat_options_object.get('heating_schedule') and \
            thermostat_options_object.get('cooling_schedule'):
        thermostat_object['ThermostatSetpoint:DualSetpoint'] = {}
        thermostat_object['ThermostatSetpoint:DualSetpoint'][thermostat_name] = {}
        thermostat_object['ThermostatSetpoint:DualSetpoint'][thermostat_name][
            'heating_setpoint_temperature_schedule_name'] = \
            thermostat_options_object['heating_schedule']
        thermostat_object['ThermostatSetpoint:DualSetpoint'][thermostat_name][
            'cooling_setpoint_temperature_schedule_name'] = \
            thermostat_options_object['cooling_schedule']
    elif thermostat_options_object.get('heating_schedule') and not \
            thermostat_options_object.get('cooling_schedule'):
        thermostat_object['ThermostatSetpoint:SingleHeating'] = {}
        thermostat_object['ThermostatSetpoint:SingleHeating'][thermostat_name] = {}
        thermostat_object['ThermostatSetpoint:SingleHeating'][thermostat_name][
            'setpoint_temperature_schedule_name'] = \
            thermostat_options_object['heating_schedule']
    elif not thermostat_options_object.get('heating_schedule') and \
            thermostat_options_object.get('cooling_schedule'):
        thermostat_object['ThermostatSetpoint:SingleCooling'] = {}
        thermostat_object['ThermostatSetpoint:SingleCooling'][thermostat_name] = {}
        thermostat_object['ThermostatSetpoint:SingleCooling'][thermostat_name][
            'setpoint_temperature_schedule_name'] = \
            thermostat_options_object['cooling_schedule']
    else:
        print('thermostat error')
        sys.exit()
    # update super dictionary with new objects
    for so in schedule_objects:
        super_dictionary = merge_dictionaries(
            super_dictionary=super_dictionary,
            object_dictionary=so
        )
    super_dictionary = merge_dictionaries(
        super_dictionary=super_dictionary,
        object_dictionary=thermostat_object)
    return super_dictionary


def modify_zone_control_thermostats(
        super_dictionary: dict,
        epjson_dictionary: dict,
        **kwargs):
    # find ZoneControlThermostats with each thermostat name and update fields
    # get thermostat name
    tmp_schedule_dictionary = {}
    tmp_modified_object_dictionary = {}
    for object_type, energyplus_object in epjson_dictionary.items():
        if object_type.lower() == 'zonecontrol:thermostat':
            for object_name, object_fields in energyplus_object.items():
                thermostat_name = energyplus_object[object_name]['control_1_name']
                # get thermostat type
                thermostats = {
                    i: j for i, j
                    in epjson_dictionary.items()
                    if re.match(r'^ThermostatSetpoint', i, re.IGNORECASE)}
                # iterate over thermostats looking for a name match
                for thermostat_type, thermostat_structure in thermostats.items():
                    for thermostat_search_name, thermostat_search_fields in thermostat_structure.items():
                        # after a match is found, create an always available schedule and update the object
                        # fields for the ZoneControl:Thermostat.  Save these as temp dictionaries to avoid
                        # updating a dictionary while iterating through itself.
                        if thermostat_search_name.lower() == thermostat_name.lower():
                            if re.match(r'.*SingleHeating$', thermostat_type, re.IGNORECASE):
                                control_schedule = build_compact_schedule(
                                    data=kwargs['data'],
                                    schedule_type='ALWAYS_VAL',
                                    insert_values=1
                                )
                            elif re.match(r'.*SingleCooling$', thermostat_type, re.IGNORECASE):
                                control_schedule = build_compact_schedule(
                                    data=kwargs['data'],
                                    schedule_type='ALWAYS_VAL',
                                    insert_values=2
                                )
                            elif re.match(r'.*DualSetpoint$', thermostat_type, re.IGNORECASE):
                                control_schedule = build_compact_schedule(
                                    data=kwargs['data'],
                                    schedule_type='ALWAYS_VAL',
                                    insert_values=4
                                )
                            else:
                                print('thermostat schedule error')
                                sys.exit()
                            # populate new object fields and add to temporary dictionaries
                            (control_schedule_type, control_schedule_structure), = control_schedule.items()
                            tmp_schedule_dictionary[control_schedule_type] = control_schedule_structure
                            (control_schedule_name, _), = control_schedule_structure.items()
                            # copy of super dictionary is necessary in case any transitions or other
                            # default values were applied to the objects before this process.
                            if not tmp_modified_object_dictionary.get(object_type):
                                tmp_modified_object_dictionary[object_type] = {object_name: {}}
                            if not tmp_modified_object_dictionary[object_type].get(object_name):
                                tmp_modified_object_dictionary[object_type][object_name] = {}
                            if epjson_dictionary.get(object_type):
                                if epjson_dictionary[object_type].get(object_name):
                                    tmp_modified_object_dictionary[object_type][object_name] = \
                                        copy.deepcopy(epjson_dictionary[object_type][object_name])
                            tmp_modified_object_dictionary[object_type][object_name]['control_1_object_type'] = \
                                thermostat_type
                            tmp_modified_object_dictionary[object_type][object_name]['control_type_schedule_name'] = \
                                control_schedule_name
    # update super dictionary with new objects
    super_dictionary = merge_dictionaries(
        super_dictionary=super_dictionary,
        object_dictionary=tmp_schedule_dictionary
    )
    super_dictionary = merge_dictionaries(
        super_dictionary=super_dictionary,
        object_dictionary=tmp_modified_object_dictionary
    )
    return super_dictionary


def build_branches(
        super_dictionary,
        build_path,
        unique_name,
        connectors_to_build=('Air', 'ChilledWaterLoop', 'HotWaterLoop')):
    """
    Build branches from build_paths

    :param super_dictionary:
    :param build_path:
    :param unique_name:
    :param connectors_to_build:
    :return:
    """
    # collect all connector path keys to use as the key for each branch iteration
    if not super_dictionary.get('BranchList'):
        super_dictionary['BranchList'] = {}
    if not super_dictionary.get('Branch'):
        super_dictionary['Branch'] = {}
    demand_chilled_water_objects = []
    demand_hot_water_objects = []
    demand_mixed_water_objects = []
    connectors_list = []
    for build_object in build_path:
        for super_object in build_object.values():
            connector_object = super_object.get('Connectors')
            if connector_object:
                for connector_type in connector_object.keys():
                    connectors_list.append(connector_type)
    connectors_set = set(connectors_to_build).intersection(set(connectors_list))
    # iterate over build path for each connector type and build the branch
    for connector_type in connectors_set:
        if connector_type.capitalize() == 'Air':
            component_list = []
            for build_object in build_path:
                for object_type, super_object in build_object.items():
                    # do I need to run a check that consecutive objects have inlet/outlet nodes?
                    connector_object = super_object.get('Connectors')
                    if connector_object:
                        object_connector = connector_object.get(connector_type)
                        if object_connector:
                            component_dictionary = {
                                'component_object_type': object_type,
                                'component_object_name': super_object['Fields']['name'],
                                'component_inlet_node_name': super_object['Fields'][object_connector['Inlet']],
                                'component_outlet_node_name': super_object['Fields'][object_connector['Outlet']]}
                            component_list.append(component_dictionary)
            super_dictionary["Branch"][' '.join([unique_name, connector_type, 'Branch'])] = component_list
            super_dictionary["BranchList"][' '.join([unique_name, connector_type, 'Branches'])] =  \
                {"branches": [{"branch_name": ' '.join([unique_name, connector_type, 'Branch'])}]}
        else:
            for build_object in build_path:
                for object_type, super_object in build_object.items():
                    # only retrieve demand-side water coils or air loop objects.  Supply side water loopp
                    # branches are created in the additional objects fields of the templates
                    if re.match('^Coil.*', object_type, re.IGNORECASE):
                        # do I need to run a check that consecutive objects have inlet/outlet nodes?
                        connector_object = super_object.get('Connectors')
                        if connector_object:
                            object_connector = connector_object.get(connector_type)
                            if object_connector:
                                super_dictionary["Branch"][' '.join([super_object['Fields']['name'], 'Branch'])] = {
                                    'component_object_type': object_type,
                                    'component_object_name': super_object['Fields']['name'],
                                    'component_inlet_node_name': super_object['Fields'][object_connector['Inlet']],
                                    'component_outlet_node_name': super_object['Fields'][object_connector['Outlet']]}
                        # build demand branch list
                        if re.match('^Coil:Cooling:Water.*', object_type, re.IGNORECASE):
                            demand_chilled_water_objects.append(' '.join([super_object['Fields']['name'], 'Branch']))
                        elif re.match('^Coil:Heating:Water.*|^ZoneHVAC:Baseboard.*Water', object_type, re.IGNORECASE):
                            demand_hot_water_objects.append(' '.join([super_object['Fields']['name'], 'Branch']))
                        elif re.match('^Coil:.*HeatPump.*', object_type, re.IGNORECASE):
                            demand_mixed_water_objects.append(' '.join([super_object['Fields']['name'], 'Branch']))
    demand_dictionary = {
        "DemandChilledWater": demand_chilled_water_objects,
        "DemandHotWater": demand_hot_water_objects,
        "DemandMixedWater": demand_mixed_water_objects}
    return super_dictionary, demand_dictionary

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
        # save outputs to dictionary
        system_dictionary = {}
        # iterate over templates
        for st in system_templates:
            # continue
            # get template object as dictionary
            hvac_system_template_obj = test_epjson[st]
            energyplus_system_build_paths = []
            energyplus_system_unique_names = []
            for system_name, system_template_dictionary in hvac_system_template_obj.items():
                print('System Name')
                print(system_name)
                option_tree = get_option_tree(st, data)
                sub_system_dictionary, system_build_path = perform_build_operations(
                    connector_path='air',
                    option_tree=option_tree,
                    template_dictionary=system_template_dictionary,
                    super_dictionary={},
                    unique_name=system_name,
                    data=data
                )
                system_dictionary[system_name] = sub_system_dictionary
                energyplus_system_build_paths.append(system_build_path)
                energyplus_system_unique_names.append(system_name)
        print('Energyplus epJSON objects')
        pprint(system_dictionary, width=150)
        # do zone builds in scope of the system build.  In production, these will be separate or child classes that
        # get system information when necessary.
        zone_templates = [i for i in test_epjson if i.startswith('HVACTemplate:Zone')]
        # save outputs to dictionary
        zone_dictionary = {}
        # iterate over templates
        energyplus_zone_build_paths = []
        energyplus_zone_unique_names = []
        print('##### Zone Template Output #####')
        for zt in zone_templates:
            # get template object as dictionary
            hvac_zone_template_obj = test_epjson[zt]
            for template_zone_name, zone_template_dictionary in hvac_zone_template_obj.items():
                # continue
                print('##### New Zone Template #####')
                print('Zone Name')
                print(template_zone_name)
                option_tree = get_option_tree(zt, data)
                sub_zone_dictionary, zone_build_path = perform_build_operations(
                    connector_path='air',
                    option_tree=option_tree,
                    template_dictionary=zone_template_dictionary,
                    super_dictionary={},
                    unique_name=zone_template_dictionary["zone_name"]
                )
                zone_dictionary[template_zone_name] = sub_zone_dictionary
                energyplus_zone_build_paths.append(zone_build_path)
                energyplus_zone_unique_names.append(zone_template_dictionary["zone_name"])
        print('zone object list')
        pprint(zone_dictionary, width=150)
        # plant system loop build
        plant_templates = [i for i in test_epjson if re.match('HVACTemplate:Plant:.*Loop', i, re.IGNORECASE)]
        # save outputs to dictionary
        plant_dictionary = {}
        energyplus_plant_build_paths = []
        energyplus_plant_unique_names = []
        for pt in plant_templates:
            hvac_plant_template_obj = test_epjson[pt]
            for template_plant_name, plant_template_dictionary in hvac_plant_template_obj.items():
                print('##### New Plant Template #####')
                print('Plant Name')
                print(template_plant_name)
                connector_path_rgx = re.match(r'^HVACTemplate:Plant:(.*)', pt, re.IGNORECASE)
                option_tree = get_option_tree(pt, data)
                sub_plant_dictionary, plant_build_path = perform_build_operations(
                    connector_path=connector_path_rgx.group(1),
                    option_tree=option_tree,
                    template_dictionary=plant_template_dictionary,
                    super_dictionary={},
                    unique_name=connector_path_rgx.group(1),
                    data=data
                )
                plant_dictionary[template_plant_name] = sub_plant_dictionary
                energyplus_plant_build_paths.append(plant_build_path)
                energyplus_plant_unique_names.append(template_plant_name)
        pprint(plant_dictionary, width=150)
        # sys.exit()
        print('##### New Plant Template Output #####')
        pprint(plant_dictionary, width=150)
        # Collect all template objects to one epjson object for further processing
        epjson_dictionary = {}
        for template_dictionary in [system_dictionary, zone_dictionary, plant_dictionary]:
            for template_name, epjson_object in template_dictionary.items():
                epjson_dictionary = merge_dictionaries(
                    super_dictionary=epjson_dictionary,
                    object_dictionary=epjson_object,
                    unique_name_override=False
                )
        # build system branches
        print('##### Branch Build #####')
        system_branch_dictionary = {}
        zone_branch_dictionary = {}
        system_demand_branchlist = []
        zone_demand_branchlist = []
        for sbp, unique_name in zip(energyplus_system_build_paths, energyplus_system_unique_names):
            system_branch_dictionary, sub_system_demand_branchlist = build_branches(
                super_dictionary=system_branch_dictionary,
                build_path=sbp,
                unique_name=unique_name)
            system_demand_branchlist.append(sub_system_demand_branchlist)
        for zbp, unique_name in zip(energyplus_zone_build_paths, energyplus_zone_unique_names):
            zone_branch_dictionary, sub_zone_demand_branchlist = build_branches(
                super_dictionary=zone_branch_dictionary,
                build_path=zbp,
                unique_name=unique_name,
                connectors_to_build=['HotWaterLoop', 'ChilledWaterLoop', 'CondenserWaterLoop'])
            zone_demand_branchlist.append(sub_zone_demand_branchlist)
        branch_dictionary = {}
        for bd in [system_branch_dictionary, zone_branch_dictionary]:
            # returned value is an object with Branch and BranchList keys
            branch_dictionary = merge_dictionaries(
                super_dictionary=branch_dictionary,
                object_dictionary=bd,
                unique_name_override=False
            )
        print('##### New Branch Output #####')
        pprint(branch_dictionary, width=150)
        epjson_dictionary = merge_dictionaries(
            super_dictionary=epjson_dictionary,
            object_dictionary=branch_dictionary
        )
        # use the stored demand branch lists to create a BranchList
        # Add pumps and pipes.  This will require the use of the template input fields as well.
        print(system_demand_branchlist)
        print(zone_demand_branchlist)
        pprint(epjson_dictionary, width=150)
        sys.exit()
        # build thermostats
        # this should be one of the last steps as it scans the epjson_dictionary
        thermostat_templates = [i for i in test_epjson if re.match('HVACTemplate:Thermostat', i, re.IGNORECASE)]
        # save outputs to dictionary
        thermostat_dictionary = {}
        for tt in thermostat_templates:
            hvac_thermostat_template_obj = test_epjson[tt]
            for template_thermostat_name, thermostat_template_dictionary in hvac_thermostat_template_obj.items():
                print('##### New Thermostat Template #####')
                print('Thermostat Name')
                print(template_thermostat_name)
                thermostat_sub_dictionary = build_thermostats(
                    super_dictionary={},
                    template_dictionary=thermostat_template_dictionary,
                    thermostat_name=template_thermostat_name,
                    data=data
                )
                thermostat_dictionary[template_thermostat_name] = thermostat_sub_dictionary
        print('##### New Thermostat Output #####')
        pprint(thermostat_dictionary, width=150)
        for template_dictionary in thermostat_dictionary.values():
            epjson_dictionary = merge_dictionaries(
                super_dictionary=epjson_dictionary,
                object_dictionary=template_dictionary,
                unique_name_override=True
            )
        # Modify epjson object using its own sub-objects as references
        # This should serve as a last step for only objects that can't be
        # completed in above processes.
        modified_epjson_objects = modify_zone_control_thermostats(
            super_dictionary={},
            epjson_dictionary=epjson_dictionary,
            data=data)
        epjson_dictionary = merge_dictionaries(
            super_dictionary=epjson_dictionary,
            object_dictionary=modified_epjson_objects
        )
        print('##### Modified Objects Output #####')
        pprint(modified_epjson_objects, width=150)
        print('##### EPJSON Output #####')
        pprint(epjson_dictionary, width=150)
    return


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    main(args)

##########################
# todo_eo: Remaining example buildout
##########################
# General High Priority
# Remove use of kwargs
###########################

##########################
# System ideas and cleanup
##########################

################
# Zone equipment
################

#############
# Plant Loops
#############

#############
# Thermostats
#############

#################
# Cleanup
# Input all necessary fields into yaml for energyplus objects
# build out all necessary additional equipment
#################

################
# Additional
# set default schedules (e.g. always on) as default values
# make one of the last steps of the program to iterate over fields and add missing schedules.
# can be generalized to a function that just adds any missing default objects
#######
# Check references to non-standard inputs referenced in Input Output Reference
# e.g. HVACTemplate:Plant:Chiller:ObjectReference and make sure these are handled
# similarly.  If they need to differ, then include it in the NFP.
###############
