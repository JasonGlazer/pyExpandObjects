import yaml
import re
import copy
import argparse
import numbers
import sys
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


def flatten_build_path(build_path, flat_list=[]):
    """
    Flattens list of lists to one list of items.
    Due to way the BuildPath is structured, sub-lists
    are inserted from re-used objects, which makes this code
    necessary.
    This is a simple recursion function that iterates a list
    and if the element it grabs is a list, then iterates through
    that list.  Whenever a non-list element is found, it is appended
    to a flattened list object that is eventually returned.
    """
    for i in build_path:
        if isinstance(i, list):
            flatten_build_path(i, flat_list)
        else:
            flat_list.append(i)
    return flat_list


def replace_values(super_object, text_replacement):
    """
    Replace the pre-set string values in an object
    to avoid duplications
    """
    if text_replacement:
        (energyplus_object_type, energyplus_object_constructors), = super_object.items()
        for field_name, field_value in energyplus_object_constructors['Fields'].items():
            super_object[energyplus_object_type]['Fields'][field_name] = field_value.replace(
                '{}',
                text_replacement
            )
    return super_object


def build_energyplus_object_from_complex_inputs(yaml_object, energyplus_object_dictionary, unique_name_input):
    """
    Builds an energyplus object from a yaml object which uses complex inputs.

    Parameters:
    yaml_object: template yaml object
    energyplus_object_dictionary: epJSON formatted dictionary containing reference objects
    unique_name_input: string to convert text to unique name
    using an existing epJSON dictionary for a HVAC System

    Returns:
    returns valid epJSON format for an EnergyPlus Object - {EnergyPlus Object: {field_names: field_values}}
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
            print(object_node_reference)
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
            (system_name, system_template_dictionary), = hvac_system_template_obj.items()
            print('System Name')
            print(system_name)
            # whenever getting values that you might edit later, use copy.deepcopy()
            # so a new dictionary is created; otherwise, every time you call that
            # value again the updated will be returned... even if you use .copy()
            option_tree = copy.deepcopy(data[':'.join(['OptionTree', st])])
            print("This is the tree that holds the alternative build information - option_tree")
            print(option_tree)
            selected_template = option_tree['Base']
            print('selected_template')
            print(selected_template)
            # get replacement values.  The yaml is structured so that each
            # the template object key value (e.g. heating_coil_type) triggers
            # this action.  The sub-objects in ReplaceElement
            # have keys that matches the options
            replace_keys = [
                field_name for field_name in system_template_dictionary.keys()
                if field_name in option_tree['ReplaceElements'].keys()
            ]
            # get insert values.  The yaml is structured similar to the
            # replace values except object modification instructions are
            # passed.  Additionally, the location is reference with
            # Before or After an object in the path to place the element.
            insert_keys = [
                field_name for field_name in system_template_dictionary.keys()
                if field_name in
                option_tree['InsertElements'].keys() and system_template_dictionary[field_name] != "None"
            ]
            # a side effect of the yaml structure is that nested lists are produced
            # so we need to flatten them.
            flattened_path = flatten_build_path(selected_template['BuildPath'])
            print('pre-replaced element path')
            for idx, energyplus_super_object in enumerate(flattened_path):
                print('object {} - {}'.format(idx, energyplus_super_object))
            # replace example
            # At the moment, replace happens even if correct equipment in place.
            # I'm sure there is a work-around to this but for now it doesn't break anything.
            if replace_keys:
                for field_name in replace_keys:
                    # get the replacement subtree
                    replace_objects_reference = \
                        option_tree['ReplaceElements'][field_name][system_template_dictionary[field_name]]
                    # for each subtree reference (more than one can be done)
                    for replace_object_reference, replace_option_structure in replace_objects_reference.items():
                        count_matches = 0
                        for idx, energyplus_super_object in enumerate(flattened_path):
                            (energyplus_object_type, _), = energyplus_super_object.items()
                            if re.match(replace_object_reference, energyplus_object_type):
                                count_matches += 1
                                if count_matches == replace_option_structure.get('Occurrence', 1):
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
                                    flattened_path[idx] = new_object
                                else:
                                    flattened_path.pop(idx)
                        # check if the number of matches actually met the occurrence threshold
                        if not count_matches >= replace_option_structure.get('Occurrence', 1):
                            print('error')
                            print('replace error')
                            sys.exit()
            print('post-replaced path')
            for idx, energyplus_super_object in enumerate(flattened_path):
                print('object {} - {}'.format(idx, energyplus_super_object))
            # apply base transitions.  This needs to be done before inserting optional elements.
            # If an element is inserted that is the same object type, then the transition mapping
            # would output to both objects.
            transition_object = selected_template['Transitions']
            for transition_field_name, value_reference in transition_object.items():
                for reference_energyplus_object_type, field_name in value_reference.items():
                    for energyplus_super_object in flattened_path:
                        # there should only be one key, so this method is used to unpack.
                        (energyplus_object_type, _), = energyplus_super_object.items()
                        if re.match(reference_energyplus_object_type, energyplus_object_type):
                            energyplus_super_object[energyplus_object_type]['Fields'][field_name] = (
                                system_template_dictionary[transition_field_name]
                            )
            print('post-transition path')
            for idx, energyplus_super_object in enumerate(flattened_path):
                print('object {} - {}'.format(idx, energyplus_super_object))
            # insert example
            if insert_keys:
                for field_name in insert_keys:
                    # get the replacement subtree
                    insert_objects_reference = \
                        option_tree['InsertElements'][field_name][system_template_dictionary[field_name]]
                    # for each subtree reference (more than one can be done)
                    for insert_object_reference, insert_option_structure in insert_objects_reference.items():
                        # iterate over regex matches and do operations when the right occurrence happens
                        count_matches = 0
                        for idx, energyplus_super_object in enumerate(flattened_path):
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
                                    for template_name, object_field_name in (
                                        insert_option_structure['Transitions'].items()
                                    ):
                                        (energyplus_object_type, _), = new_object.items()
                                        new_object[energyplus_object_type]['Fields'][object_field_name] = \
                                            system_template_dictionary[template_name]
                                    flattened_path.insert(
                                        insert_location,
                                        new_object
                                    )
                        # check if the number of matches actually met the occurrence threshold
                        if not count_matches >= replace_option_structure.get('Occurrence', 1):
                            print('error')
                            print('insert error')
                            sys.exit()
            print('post-insert element path')
            for idx, energyplus_super_object in enumerate(flattened_path):
                print('object {} - {}'.format(idx, energyplus_super_object))
            # insert system name
            for energyplus_super_object in flattened_path:
                (energyplus_object_type, energyplus_object_constructors), = energyplus_super_object.items()
                for field_name, field_value in energyplus_object_constructors['Fields'].items():
                    if isinstance(field_value, str):
                        energyplus_super_object[energyplus_object_type]['Fields'][field_name] = \
                            field_value.format(system_name)
            print('post-variable rename path')
            for idx, energyplus_super_object in enumerate(flattened_path):
                print('object {} - {}'.format(idx, energyplus_super_object))
            # Build a dictionary of valid epJSON objects from constructors
            # need to check for unique names within objects when in production
            energyplus_epjson_object = {}
            for idx, energyplus_super_object in enumerate(flattened_path):
                (energyplus_object_type, energyplus_object_constructors), = energyplus_super_object.items()
                # use copy so that the original structure is preserved for future queries
                tmp_d = copy.deepcopy(energyplus_object_constructors['Fields'])
                object_key = tmp_d.pop('name')
                # not necessary but it's a good reminder that this object is the target value
                object_values = tmp_d
                # create the object type if it doesn't exist
                if not energyplus_epjson_object.get(energyplus_object_type):
                    energyplus_epjson_object[energyplus_object_type] = {}
                # for the first object, do not alter the input node name.
                # for subsequent objects, set the input node name value to the
                # output node name value of the previous object.
                if idx == 0:
                    energyplus_epjson_object[energyplus_object_type][object_key] = object_values
                    out_node_name = (
                        energyplus_object_constructors['Fields']
                        [energyplus_object_constructors['Connectors']['Air']['Outlet']]
                    )
                else:
                    object_values[
                        energyplus_object_constructors['Connectors']['Air']['Inlet']
                    ] = out_node_name
                    energyplus_epjson_object[energyplus_object_type][object_key] = object_values
                    out_node_name = (
                        energyplus_object_constructors['Fields']
                        [energyplus_object_constructors['Connectors']['Air']['Outlet']]
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
                energyplus_object_constructors['Fields']['name']
            ]['air_inlet_node_name'] = '{} Outside Air Inlet'.format(system_name)
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
            (zone_name, zone_template_dictionary), = hvac_zone_template_obj.items()
            print('Zone Name')
            print(zone_name)
    return


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    main(args)

##########################
# todo_eo: Remaining example buildout
##########################
# System ideas and cleanup
##########################
# Try to make regex for when equipment is specified as key.  E.g. instead of this:
# reference_setpoint_node_name:
#           Fan:VariableVolume: air_outlet_node_name
#
# do this
# reference_setpoint_node_name:
#           Fan:.*: air_outlet_node_name
#
# Maybe make a sub function to find the equipment b/c it's likely to get reused often.
# This function could also hold the logic to just return a string if the value from
# reference_setpoint_node_name is a string.
# For really complex operations, you could add a parameter to match the nth occurrence
# reference_setpoint_node_name:
#           Fan:.*: air_outlet_node_name
#           Occurrence: 1
#
# Replace Regex should be changed to a dictionary where the key is the regex and the
# value is the occurrence, or the format above with just no value output for the regex
# Can we do this for FieldNameReplacement too?  It seems like it would be better if all
# key/value fields had the same options
#
# Possible text to replace code structure overview
# Some values can be expressed as one of two types:
#
# 1. static value - Number or string which does not contain '{}' for further formatting
#     2. Dictionary mapping :
#
# * Required Sub-dictionary
# * Key - EnergyPlus Object.  This can be a regular expression
# * Value - the reference node of the object
#
# * Optional Sub-dictionary
# * Key - 'Occurrence'
# * Value - The number occurrence from a match in the required sub-dictionary key.
# This is in case multiple matches are possible.
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
