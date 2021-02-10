import yaml
import sys
import re
import copy

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
        for system_name, field_d in hvac_template_obj.items():
            print(system_name)
            option_tree = copy.deepcopy(data[':'.join(['OptionTree', t])])
            print("option_tree")
            print(option_tree)
            selected_template = option_tree['Base']
            print('selected_template')
            print(selected_template)
            print(field_d['humidifier_type'])
            replace_keys = [
                field_name for field_name in field_d.keys()
                if field_name in option_tree['ReplaceElements'].keys()
                and field_d[field_name] != "None"
            ]
            insert_keys = [
                field_name for field_name in field_d.keys()
                if field_name in option_tree['InsertElements'].keys()
                and field_d[field_name] != "None"
            ]
            print('replace keys')
            print(replace_keys)
            print('insert keys')
            print(insert_keys)
            flattened_path = flatten_build_path(selected_template['buildPath'])
            print('pre-replaced path')
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
                                option_tree['ReplaceElements'][field_name]['ReplaceElement'][field_d[field_name]]['Object']
                            )
                            replacement = option_tree['ReplaceElements'][field_name]['ReplaceElement'][field_d[field_name]]\
                            .get('FieldNameReplacement')
                            # rename if applicable
                            new_object = replace_values(
                                new_object,
                                replacement
                            )
                            flattened_path[idx] = new_object
                            test = option_tree['ReplaceElements'][field_name]['ReplaceElement'][field_d[field_name]]
            print('post-replaced path')
            for idx, i in enumerate(flattened_path):
                print('object {} - {}'.format(idx, i))
            # insert example
            if insert_keys:
                for field_name in insert_keys:
                    # try the 'before' option first, then 'after'
                    if option_tree['InsertElements'][field_name]['Location'].get('BeforeObject'):
                        reference_object = option_tree['InsertElements'][field_name]['Location'].get('BeforeObject')
                        insert_offset = 0
                    elif option_tree['InsertElements'][field_name]['Location'].get('AfterObject'):
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
                                option_tree['InsertElements'][field_name]['ObjectType'][field_d[field_name]]['Object']
                            )
                            replacement = option_tree['InsertElements'][field_name]['ObjectType'][field_d[field_name]]\
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
            print('post-insert path')
            for idx, i in enumerate(flattened_path):
                print('object {} - {}'.format(idx, i))
            # collapse objects to EP objects
            # make sure to save last output air node as branch output for building splitters/mixers
            # three lists: branch, setpointManagers, and Controllers
            # maybe search by object name 'preheat' for preheat setpoint managers? same for other objects?
