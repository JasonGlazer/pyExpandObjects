import yaml
import sys
import re
import copy
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
    }
}


def flatten_build_path(build_path, flat_list=[]):
    """
    Flattens list of lists to one list of items.
    Due to way the buildPath is structured, sub-lists
    are inserted of re-used objects, which makes this code
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


def replace_values(ep_object, text_replacement):
    """
    Replace the pre-set strting values in an object
    to avoid duplications
    """
    if text_replacement:
        for ep_object_type, object_arguments in ep_object.items():
            for field_name2, field_value in object_arguments['Fields'].items():
                ep_object[ep_object_type]['Fields'][field_name2] = field_value.replace(
                    '{}',
                    text_replacement
                )
    return ep_object

def build_controller_manager(yaml_object, ep_d):
    """
    Builds a setpoint manager or controller using an existing epJSON dictionary for a HVAC System

    returns key and value to be inserted into epJSON
    """
    for energyplus_object, energyplus_arguments in yaml_object.items():
        tmp_d = {}
        # if the value is a string, then it's a direct input.  if it's not, then it's a dictionary
        # where the key-value pair is the
        for controller_manager_field_name, value_reference in energyplus_arguments.items():
            if isinstance(value_reference, str):
                tmp_d[controller_manager_field_name] = value_reference.format(system_name)
            else:
                for object_type, reference_node in value_reference.items():
                    print(object_type)
                    print(reference_node)
                    print(ep_d[object_type])
                    for k, v in ep_d[object_type].items():
                        print(ep_d[object_type][k])
                    for k in ep_d[object_type].keys():
                        print(ep_d[object_type][k])
                        print(ep_d[object_type][k][reference_node])
                        tmp_d[controller_manager_field_name] = ep_d[object_type][k][reference_node]
    return energyplus_object, tmp_d

# In this process note one import aspect. Actual structure/object names are 
# # not used.  The path is built
# entirely from yaml structures, which means that very little (comparatively)
# python code will need to be rewritten, i.e. this chunk should work for 
# (hopefully) all HVACTemplate:System objects.
with open(sys.argv[1], 'r') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)
    templates = [i for i in test_epjson if i.startswith('HVACTemplate:System')]
    for t in templates:
        hvac_template_obj = test_epjson[t]
        for system_name, template_dictionary in hvac_template_obj.items():
            print('System Name')
            print(system_name)
            option_tree = copy.deepcopy(data[':'.join(['OptionTree', t])])
            print("option_tree")
            print(option_tree)
            selected_template = option_tree['Base']
            print('selected_template')
            print(selected_template)
            replace_keys = [
                field_name for field_name in template_dictionary.keys()
                if field_name in option_tree['ReplaceElements'].keys()
                and template_dictionary[field_name] != "None"
            ]
            insert_keys = [
                field_name for field_name in template_dictionary.keys()
                if field_name in option_tree['InsertElements'].keys()
                and template_dictionary[field_name] != "None"
            ]
            flattened_path = flatten_build_path(selected_template['buildPath'])
            print('pre-replaced element path')
            for idx, i in enumerate(flattened_path):
                print('object {} - {}'.format(idx, i))
            # replace example
            # replace happens even if correct equipment in place.
            if replace_keys:
                for field_name in replace_keys:
                    for idx, obj in enumerate(flattened_path):
                        replace_regex = option_tree['ReplaceElements'][field_name]['ReplaceRegex']
                        object_type = list(obj.keys())[0]
                        if re.match(replace_regex, object_type):
                            new_object = copy.deepcopy(
                                option_tree['ReplaceElements'][field_name]['ReplaceElement'][template_dictionary[field_name]]['Object']
                            )
                            replacement = option_tree['ReplaceElements'][field_name]['ReplaceElement'][template_dictionary[field_name]]\
                            .get('FieldNameReplacement')
                            # rename if applicable
                            new_object = replace_values(
                                new_object,
                                replacement
                            )
                            flattened_path[idx] = new_object
                            test = option_tree['ReplaceElements'][field_name]['ReplaceElement'][template_dictionary[field_name]]
            print('post-replaced path')
            for idx, i in enumerate(flattened_path):
                print('object {} - {}'.format(idx, i))
            # insert example
            if insert_keys:
                for field_name in insert_keys:
                    # try the 'before' option first, then 'after'
                    reference_object = None
                    if option_tree['InsertElements'][field_name]['Location'].get('BeforeObject'):
                        reference_object = option_tree['InsertElements'][field_name]['Location'].get('BeforeObject')
                        insert_offset = 0
                    elif not reference_object and option_tree['InsertElements'][field_name]['Location'].get('AfterObject'):
                        reference_object = option_tree['InsertElements'][field_name]['Location'].get('AfterObject')
                        insert_offset = 1
                    else:
                        print('error')
                    if reference_object:
                        for idx, obj in enumerate(flattened_path):
                            object_type = list(obj.keys())[0]
                            if reference_object == object_type:
                                insert_location = idx + insert_offset
                        if insert_location >= 0:
                            new_object = copy.deepcopy(
                                option_tree['InsertElements'][field_name]['ObjectType'][template_dictionary[field_name]]['Object']
                            )
                            replacement = option_tree['InsertElements'][field_name]['ObjectType'][template_dictionary[field_name]]\
                                .get('FieldNameReplacement')
                            new_object = replace_values(
                                new_object,
                                replacement
                            )
                            flattened_path.insert(
                                insert_location,
                                new_object
                            )
                        else:
                            print('error')
            print('post-insert elemet path')
            for idx, i in enumerate(flattened_path):
                print('object {} - {}'.format(idx, i))
            # insert system name
            for build_object in flattened_path:
                for energyplus_object, energyplus_arguments in build_object.items():
                    for field_name, field_value in energyplus_arguments['Fields'].items():
                        build_object[energyplus_object]['Fields'][field_name] = field_value.format(system_name)
            print('post-variable rename path')
            for idx, i in enumerate(flattened_path):
                print('object {} - {}'.format(idx, i))
            ep_object_d = {}
            # create airflow system epJSON dictionary
            # need to check for unique names within objects
            for idx, build_object in enumerate(flattened_path):
                for energyplus_object, energyplus_arguments in build_object.items():
                    object_key = energyplus_arguments['Fields'].pop('name')
                    object_values = energyplus_arguments['Fields']
                    if not ep_object_d.get(energyplus_object):
                        ep_object_d[energyplus_object] = {}
                    if idx == 0:
                        ep_object_d[energyplus_object][object_key] = object_values
                        out_node_name = energyplus_arguments['Fields']\
                            [energyplus_arguments['Connectors']['Air']['Outlet']]
                    else:
                        energyplus_arguments['Fields']\
                            [energyplus_arguments['Connectors']['Air']['Inlet']] = out_node_name
                        ep_object_d[energyplus_object][object_key] = object_values
                        out_node_name = energyplus_arguments['Fields']\
                            [energyplus_arguments['Connectors']['Air']['Outlet']]
            # assign Template value inputs
            transition_object = selected_template['Transitions']
            for transition_field_name, value_reference in transition_object.items():
                for ep_object, node_name in value_reference.items():
                    #should only be one key
                    for k in ep_object_d[ep_object].keys():
                        ep_object_d[ep_object][k][node_name] = template_dictionary[transition_field_name]
            # build Controllers (if/else statements can be copied from Fortran code)
            # however, note that we can also call the build_path or the epJSON dictionary
            # now to make decisions as well
            # Mixed Air setpoint Manager

            # These objects need to be fixed 'name' needs to be a key with the rest as values.
            # fix the calling function and both will be fixed.


            pprint(ep_object_d)
            setpoint_managers = copy.deepcopy(data['SetpointManagers'])
            energyplus_object, tmp_d = build_controller_manager(
                copy.deepcopy(setpoint_managers['MixedAir']['Base']),
                ep_object_d
            )
            ep_object_d[energyplus_object] = tmp_d
            # build Controllers (if/else statements can be copied from Fortran code)
            # however, note that we can also call the build_path or the epJSON dictionary
            # now to make decisions as well
            controllers = copy.deepcopy(data['Controllers'])
            energyplus_object, tmp_d = build_controller_manager(
                copy.deepcopy(controllers['OutdoorAir']['Base']),
                ep_object_d
            )
            ep_object_d[energyplus_object] = tmp_d
            print('Energyplus epJSON objects')
            pprint(ep_object_d, width=150)
            print('Supply Path outlet')
            for energyplus_arguments in flattened_path[-1].values():
                last_node = energyplus_arguments['Fields'][energyplus_arguments['Connectors']['Air']['Outlet']]
            print(last_node)
            print('Supply Path inlet')
            # loops like these need to be removed.
            for k, v in selected_template['Connectors']['Supply']['Inlet'].items():
                for object_name, object_values in ep_object_d[k].items():
                    print(ep_object_d[k][object_name][v])
            print('Demand Path inlet')
            print(selected_template['Connectors']['Demand']['Inlet'].format(system_name))
            print('Demand Path outlet')
            print(selected_template['Connectors']['Demand']['Outlet'].format(system_name))

            # three lists: branch, setpointManagers, and Controllers
            # maybe search by object name 'preheat' for preheat setpoint managers? same for other objects?
