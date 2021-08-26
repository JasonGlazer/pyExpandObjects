from pathlib import Path

from tests.simulations import BaseSimulationTest
from src.epjson_handler import EPJSON

test_dir = Path(__file__).parent.parent.parent

schedule_objects = {
    "Schedule:Compact": {
        "Always12.5": {
            "data": [
                {
                    "field": "Through: 12/31"
                },
                {
                    "field": "For: AllDays"
                },
                {
                    "field": "Until: 24:00"
                },
                {
                    "field": 12.5
                }
            ],
            "schedule_type_limits_name": "Any Number"
        }
    }
}


class TestSimulationsSystemDualDuct(BaseSimulationTest):
    def setUp(self):
        self.ej = EPJSON()
        base_idf_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles', 'HVACTemplate-5ZoneDualDuct.idf')
        base_copy_file_path = self._copy_to_test_directory(base_idf_file_path)
        # read in base file, then edit inputs for alternate tests
        self.base_epjson = self.get_epjson_object_from_idf_file(base_copy_file_path)
        self.base_epjson.pop('Output:Variable')
        return

    def teardown(self):
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:system_availability_schedule_name")
    def test_system_availability_schedule_name(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1'][
            'system_availability_schedule_name'] = 'OCCUPY-1'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1'][
            'night_cycle_control'] = 'CycleOnAny'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['Fan:ConstantVolume']['SYS 1 ColdDuct Supply Fan']['availability_schedule_name'])
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['Fan:ConstantVolume']['SYS 1 HotDuct Supply Fan']['availability_schedule_name'])
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['AvailabilityManager:NightCycle']['SYS 1 Availability'][
                'fan_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "system_configuration_type_dual_fan_constant_volume")
    def test_system_configuration_type_dual_fan_constant_volume(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = 'DualFanConstantVolume'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Fan:ConstantVolume'].get('SYS 1 ColdDuct Supply Fan'))
        self.assertIsNotNone(
            epjson_output['Fan:ConstantVolume'].get('SYS 1 HotDuct Supply Fan'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "system_configuration_type_single_fan_constant_volume")
    def test_system_configuration_type_single_fan_constant_volume(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'SingleFanConstantVolume'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Fan:ConstantVolume'].get('SYS 1 Supply Fan'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "system_configuration_type_dual_fan_variable_volume")
    def test_system_configuration_type_dual_fan_variable_volume(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = 'DualFanVariableVolume'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Fan:VariableVolume'].get('SYS 1 ColdDuct Supply Fan'))
        self.assertIsNotNone(
            epjson_output['Fan:VariableVolume'].get('SYS 1 HotDuct Supply Fan'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "system_configuration_type_single_fan_variable_volume")
    def test_system_configuration_type_single_fan_variable_volume(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'SingleFanVariableVolume'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Fan:VariableVolume'].get('SYS 1 Supply Fan'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "main_supply_fan_maximum_flow_rate_constant_volume")
    def test_main_supply_fan_maximum_flow_rate_constant_volume(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'SingleFanConstantVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['main_supply_fan_maximum_flow_rate'] = 1.2
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            1.2,
            epjson_output['Sizing:System']['SYS 1 Sizing System']['cooling_supply_air_flow_rate'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "main_supply_fan_maximum_flow_rate_variable_volume")
    def test_main_supply_fan_maximum_flow_rate_variable_volume(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'SingleFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['main_supply_fan_maximum_flow_rate'] = 1.2
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            1.2,
            epjson_output['Sizing:System']['SYS 1 Sizing System']['cooling_supply_air_flow_rate'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "main_supply_fan_minimum_flow_fraction_variable_volume")
    def test_main_supply_fan_minimum_flow_fraction_variable_volume(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'SingleFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['main_supply_fan_minimum_flow_fraction'] = 0.15
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.15,
            epjson_output['Fan:VariableVolume']['SYS 1 Supply Fan']['fan_power_minimum_flow_fraction'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "main_supply_fan_total_efficiency")
    def test_main_supply_fan_total_efficiency(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'SingleFanConstantVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['main_supply_fan_total_efficiency'] = 0.66
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.66,
            epjson_output['Fan:ConstantVolume']['SYS 1 Supply Fan']['fan_total_efficiency'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "main_supply_fan_delta_pressure")
    def test_main_supply_fan_delta_pressure(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'SingleFanConstantVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['main_supply_fan_delta_pressure'] = 750
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            750,
            epjson_output['Fan:ConstantVolume']['SYS 1 Supply Fan']['pressure_rise'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "main_supply_fan_delta_pressure")
    def test_main_supply_fan_motor_efficiency(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'SingleFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['main_supply_fan_motor_efficiency'] = 0.77
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.77,
            epjson_output['Fan:VariableVolume']['SYS 1 Supply Fan']['motor_efficiency'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "main_supply_fan_motor_in_air_stream_fraction")
    def test_main_supply_fan_motor_in_air_stream_fraction(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'SingleFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['main_supply_fan_motor_in_air_stream_fraction'] = \
            0.85
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.85,
            epjson_output['Fan:VariableVolume']['SYS 1 Supply Fan']['motor_in_airstream_fraction'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "main_supply_fan_part_load_power_coefficients_inlet_vane_dampers")
    def test_main_supply_fan_part_load_power_coefficients_inlet_vane_dampers(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'SingleFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['main_supply_fan_part_load_power_coefficients'] = \
            'InletVaneDampers'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.35071223,
            epjson_output['Fan:VariableVolume']['SYS 1 Supply Fan']['fan_power_coefficient_1'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "main_supply_fan_part_load_power_coefficients_outlet_dampers")
    def test_main_supply_fan_part_load_power_coefficients_outlet_dampers(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'SingleFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['main_supply_fan_part_load_power_coefficients'] = \
            'OutletDampers'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.37073425,
            epjson_output['Fan:VariableVolume']['SYS 1 Supply Fan']['fan_power_coefficient_1'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "main_supply_fan_part_load_power_coefficients_variable_speed_motor")
    def test_main_supply_fan_part_load_power_coefficients_variable_speed_motor(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'SingleFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['main_supply_fan_part_load_power_coefficients'] = \
            'VariableSpeedMotor'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.0015302446,
            epjson_output['Fan:VariableVolume']['SYS 1 Supply Fan']['fan_power_coefficient_1'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "main_supply_fan_part_load_power_coefficients_ashrae_appendix_g")
    def test_main_supply_fan_part_load_power_coefficients_ashrae_appendix_g(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'SingleFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['main_supply_fan_part_load_power_coefficients'] = \
            'ASHRAE90.1-2004AppendixG'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.0013,
            epjson_output['Fan:VariableVolume']['SYS 1 Supply Fan']['fan_power_coefficient_1'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "main_supply_fan_part_load_power_coefficients"
                                              "_variable_speed_motor_pressure_reset")
    def test_main_supply_fan_part_load_power_coefficients_variable_speed_motor_pressure_reset(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'SingleFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['main_supply_fan_part_load_power_coefficients'] = \
            'VariableSpeedMotorPressureReset'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.040759894,
            epjson_output['Fan:VariableVolume']['SYS 1 Supply Fan']['fan_power_coefficient_1'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cold_duct_supply_fan_maximum_flow_rate_constant_volume")
    def test_cold_duct_supply_fan_maximum_flow_rate_constant_volume(self):
        # todo_eo: does not appear this value maps to anything
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanConstantVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cold_duct_supply_fan_maximum_flow_rate'] = 1.2
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            1.2,
            epjson_output['Sizing:System']['SYS 1 Sizing System']['cooling_supply_air_flow_rate'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cold_duct_supply_fan_maximum_flow_rate_variable_volume")
    def test_cold_duct_supply_fan_maximum_flow_rate_variable_volume(self):
        # todo_eo: does not appear this value maps to anything
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cold_duct_supply_fan_maximum_flow_rate'] = 1.2
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            1.2,
            epjson_output['Sizing:System']['SYS 1 Sizing System']['cooling_supply_air_flow_rate'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cold_duct_supply_fan_minimum_flow_fraction_variable_volume")
    def test_cold_duct_supply_fan_minimum_flow_fraction_variable_volume(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cold_duct_supply_fan_minimum_flow_fraction'] = 0.15
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.15,
            epjson_output['Fan:VariableVolume']['SYS 1 ColdDuct Supply Fan']['fan_power_minimum_flow_fraction'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cold_duct_supply_fan_total_efficiency")
    def test_cold_duct_supply_fan_total_efficiency(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanConstantVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cold_duct_supply_fan_total_efficiency'] = 0.66
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.66,
            epjson_output['Fan:ConstantVolume']['SYS 1 ColdDuct Supply Fan']['fan_total_efficiency'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cold_duct_supply_fan_delta_pressure")
    def test_cold_duct_supply_fan_delta_pressure(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanConstantVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cold_duct_supply_fan_delta_pressure'] = 750
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            750,
            epjson_output['Fan:ConstantVolume']['SYS 1 ColdDuct Supply Fan']['pressure_rise'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cold_duct_supply_fan_motor_efficiency")
    def test_cold_duct_supply_fan_motor_efficiency(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cold_duct_supply_fan_motor_efficiency'] = 0.77
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.77,
            epjson_output['Fan:VariableVolume']['SYS 1 ColdDuct Supply Fan']['motor_efficiency'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cold_duct_supply_fan_motor_in_air_stream_fraction")
    def test_cold_duct_supply_fan_motor_in_air_stream_fraction(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1'][
            'cold_duct_supply_fan_motor_in_air_stream_fraction'] = 0.85
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.85,
            epjson_output['Fan:VariableVolume']['SYS 1 ColdDuct Supply Fan']['motor_in_airstream_fraction'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cold_duct_supply_fan_part_load_power_coefficients_inlet_vane_dampers")
    def test_cold_duct_supply_fan_part_load_power_coefficients_inlet_vane_dampers(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1'][
            'cold_duct_supply_fan_part_load_power_coefficients'] = 'InletVaneDampers'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.35071223,
            epjson_output['Fan:VariableVolume']['SYS 1 ColdDuct Supply Fan']['fan_power_coefficient_1'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cold_duct_supply_fan_part_load_power_coefficients_outlet_dampers")
    def test_cold_duct_supply_fan_part_load_power_coefficients_outlet_dampers(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1'][
            'cold_duct_supply_fan_part_load_power_coefficients'] = 'OutletDampers'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.37073425,
            epjson_output['Fan:VariableVolume']['SYS 1 ColdDuct Supply Fan']['fan_power_coefficient_1'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cold_duct_supply_fan_part_load_power_coefficients_variable_speed_motor")
    def test_cold_duct_supply_fan_part_load_power_coefficients_variable_speed_motor(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1'][
            'cold_duct_supply_fan_part_load_power_coefficients'] = 'VariableSpeedMotor'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.0015302446,
            epjson_output['Fan:VariableVolume']['SYS 1 ColdDuct Supply Fan']['fan_power_coefficient_1'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cold_duct_supply_fan_part_load_power_coefficients_ashrae_appendix_g")
    def test_cold_duct_supply_fan_part_load_power_coefficients_ashrae_appendix_g(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1'][
            'cold_duct_supply_fan_part_load_power_coefficients'] = 'ASHRAE90.1-2004AppendixG'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.0013,
            epjson_output['Fan:VariableVolume']['SYS 1 ColdDuct Supply Fan']['fan_power_coefficient_1'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cold_duct_supply_fan_part_load_power_coefficients"
                                              "_variable_speed_motor_pressure_reset")
    def test_cold_duct_supply_fan_part_load_power_coefficients_variable_speed_motor_pressure_reset(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1'][
            'cold_duct_supply_fan_part_load_power_coefficients'] = 'VariableSpeedMotorPressureReset'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.040759894,
            epjson_output['Fan:VariableVolume']['SYS 1 ColdDuct Supply Fan']['fan_power_coefficient_1'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cold_duct_supply_fan_placement_blow_through_constant")
    def test_cold_duct_supply_fan_placement_blow_through_constant(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanConstantVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1'][
            'cold_duct_supply_fan_placement'] = 'BlowThrough'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'SYS 1 ColdDuct Supply Fan Outlet',
            epjson_output['Coil:Cooling:Water']['SYS 1 ColdDuct Cooling Coil']['air_inlet_node_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cold_duct_supply_fan_placement_blow_through_variable")
    def test_cold_duct_supply_fan_placement_blow_through_variable(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1'][
            'cold_duct_supply_fan_placement'] = 'BlowThrough'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'SYS 1 ColdDuct Supply Fan Outlet',
            epjson_output['Coil:Cooling:Water']['SYS 1 ColdDuct Cooling Coil']['air_inlet_node_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cold_duct_supply_fan_placement_draw_through_constant")
    def test_cold_duct_supply_fan_placement_draw_through_constant(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanConstantVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1'][
            'cold_duct_supply_fan_placement'] = 'DrawThrough'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'SYS 1 ColdDuct Cooling Coil Outlet',
            epjson_output['Fan:ConstantVolume']['SYS 1 ColdDuct Supply Fan']['air_inlet_node_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cold_duct_supply_fan_placement_draw_through_variable")
    def test_cold_duct_supply_fan_placement_draw_through_variable(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1'][
            'cold_duct_supply_fan_placement'] = 'DrawThrough'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'SYS 1 ColdDuct Cooling Coil Outlet',
            epjson_output['Fan:VariableVolume']['SYS 1 ColdDuct Supply Fan']['air_inlet_node_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "hot_duct_supply_fan_maximum_flow_rate_constant_volume")
    def test_hot_duct_supply_fan_maximum_flow_rate_constant_volume(self):
        # todo_eo: does not appear this value maps to anything
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanConstantVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['hot_duct_supply_fan_maximum_flow_rate'] = 1.2
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            1.2,
            epjson_output['Sizing:System']['SYS 1 Sizing System']['heating_supply_air_flow_rate'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "hot_duct_supply_fan_maximum_flow_rate_variable_volume")
    def test_hot_duct_supply_fan_maximum_flow_rate_variable_volume(self):
        # todo_eo: does not appear this value maps to anything
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['hot_duct_supply_fan_maximum_flow_rate'] = 1.2
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            1.2,
            epjson_output['Sizing:System']['SYS 1 Sizing System']['heating_supply_air_flow_rate'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "hot_duct_supply_fan_minimum_flow_fraction_variable_volume")
    def test_hot_duct_supply_fan_minimum_flow_fraction_variable_volume(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['hot_duct_supply_fan_minimum_flow_fraction'] = 0.15
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.15,
            epjson_output['Fan:VariableVolume']['SYS 1 HotDuct Supply Fan']['fan_power_minimum_flow_fraction'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "hot_duct_supply_fan_total_efficiency")
    def test_hot_duct_supply_fan_total_efficiency(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanConstantVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['hot_duct_supply_fan_total_efficiency'] = 0.66
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.66,
            epjson_output['Fan:ConstantVolume']['SYS 1 HotDuct Supply Fan']['fan_total_efficiency'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "hot_duct_supply_fan_delta_pressure")
    def test_hot_duct_supply_fan_delta_pressure(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanConstantVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['hot_duct_supply_fan_delta_pressure'] = 750
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            750,
            epjson_output['Fan:ConstantVolume']['SYS 1 HotDuct Supply Fan']['pressure_rise'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "hot_duct_supply_fan_motor_efficiency")
    def test_hot_duct_supply_fan_motor_efficiency(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['hot_duct_supply_fan_motor_efficiency'] = 0.77
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.77,
            epjson_output['Fan:VariableVolume']['SYS 1 HotDuct Supply Fan']['motor_efficiency'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "hot_duct_supply_fan_motor_in_air_stream_fraction")
    def test_hot_duct_supply_fan_motor_in_air_stream_fraction(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1'][
            'hot_duct_supply_fan_motor_in_air_stream_fraction'] = 0.85
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.85,
            epjson_output['Fan:VariableVolume']['SYS 1 HotDuct Supply Fan']['motor_in_airstream_fraction'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "hot_duct_supply_fan_part_load_power_coefficients_inlet_vane_dampers")
    def test_hot_duct_supply_fan_part_load_power_coefficients_inlet_vane_dampers(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1'][
            'hot_duct_supply_fan_part_load_power_coefficients'] = 'InletVaneDampers'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.35071223,
            epjson_output['Fan:VariableVolume']['SYS 1 HotDuct Supply Fan']['fan_power_coefficient_1'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "hot_duct_supply_fan_part_load_power_coefficients_outlet_dampers")
    def test_hot_duct_supply_fan_part_load_power_coefficients_outlet_dampers(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1'][
            'hot_duct_supply_fan_part_load_power_coefficients'] = 'OutletDampers'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.37073425,
            epjson_output['Fan:VariableVolume']['SYS 1 HotDuct Supply Fan']['fan_power_coefficient_1'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "hot_duct_supply_fan_part_load_power_coefficients_variable_speed_motor")
    def test_hot_duct_supply_fan_part_load_power_coefficients_variable_speed_motor(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1'][
            'hot_duct_supply_fan_part_load_power_coefficients'] = 'VariableSpeedMotor'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.0015302446,
            epjson_output['Fan:VariableVolume']['SYS 1 HotDuct Supply Fan']['fan_power_coefficient_1'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "hot_duct_supply_fan_part_load_power_coefficients_ashrae_appendix_g")
    def test_hot_duct_supply_fan_part_load_power_coefficients_ashrae_appendix_g(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1'][
            'hot_duct_supply_fan_part_load_power_coefficients'] = 'ASHRAE90.1-2004AppendixG'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.0013,
            epjson_output['Fan:VariableVolume']['SYS 1 HotDuct Supply Fan']['fan_power_coefficient_1'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "hot_duct_supply_fan_part_load_power_coefficients"
                                              "_variable_speed_motor_pressure_reset")
    def test_hot_duct_supply_fan_part_load_power_coefficients_variable_speed_motor_pressure_reset(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1'][
            'hot_duct_supply_fan_part_load_power_coefficients'] = 'VariableSpeedMotorPressureReset'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.040759894,
            epjson_output['Fan:VariableVolume']['SYS 1 HotDuct Supply Fan']['fan_power_coefficient_1'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "hot_duct_supply_fan_placement_blow_through_constant")
    def test_hot_duct_supply_fan_placement_blow_through_constant(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanConstantVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1'][
            'hot_duct_supply_fan_placement'] = 'BlowThrough'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'SYS 1 HotDuct Supply Fan Outlet',
            epjson_output['Coil:Heating:Water']['SYS 1 HotDuct Heating Coil']['air_inlet_node_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "hot_duct_supply_fan_placement_blow_through_variable")
    def test_hot_duct_supply_fan_placement_blow_through_variable(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1'][
            'hot_duct_supply_fan_placement'] = 'BlowThrough'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'SYS 1 HotDuct Supply Fan Outlet',
            epjson_output['Coil:Heating:Water']['SYS 1 HotDuct Heating Coil']['air_inlet_node_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "hot_duct_supply_fan_placement_draw_through_constant")
    def test_hot_duct_supply_fan_placement_draw_through_constant(self):
        # todo_eo: EO fails with this option setup. It appears the hot branchlist is out of order
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanConstantVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1'][
            'hot_duct_supply_fan_placement'] = 'DrawThrough'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'SYS 1 HotDuct Cooling Coil Outlet',
            epjson_output['Fan:ConstantVolume']['SYS 1 HotDuct Supply Fan']['air_inlet_node_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "hot_duct_supply_fan_placement_draw_through_variable")
    def test_hot_duct_supply_fan_placement_draw_through_variable(self):
        # todo_eo: EO fails with this option setup.  It appears the hot branchlist is out of order
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1'][
            'hot_duct_supply_fan_placement'] = 'DrawThrough'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'SYS 1 HotDuct Cooling Coil Outlet',
            epjson_output['Fan:VariableVolume']['SYS 1 HotDuct Supply Fan']['air_inlet_node_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cooling_coil_type_chilled_water")
    def test_cooling_coil_type_chilled_water(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cooling_coil_type'] = 'ChilledWater'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Coil:Cooling:Water'].get('SYS 1 ColdDuct Cooling Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cooling_coil_type_chilled_water_detailed_flat_model")
    def test_cooling_coil_type_chilled_water_detailed_flat_model(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cooling_coil_type'] = 'ChilledWaterDetailedFlatModel'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Coil:Cooling:Water:DetailedGeometry'].get('SYS 1 ColdDuct Cooling Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cooling_coil_type_none")
    def test_cooling_coil_type_none(self):
        # todo_eo: EO fails with error message on conversion.  Similar error on simulation.
        #  Conversion message output: b"<root>[Branch][SYS 1 Cold Branch][components][1] - Missing required property
        #  'component_outlet_node_name'.\r\nErrors occurred when validating input file. Preceding condition(s) cause
        #  termination.\r\nInput file conversion failed:
        self.base_epjson.pop('HVACTemplate:Plant:Chiller')
        self.base_epjson.pop('HVACTemplate:Plant:ChilledWaterLoop')
        self.base_epjson.pop('HVACTemplate:Plant:Tower')
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cooling_coil_type'] = 'None'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Coil:Cooling:Water:DetailedGeometry'].get('SYS 1 ColdDuct Cooling Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cooling_coil_availability_schedule_name")
    def test_cooling_coil_availability_schedule_name(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cooling_coil_availability_schedule_name'] = \
            'OCCUPY-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['Coil:Cooling:Water']['SYS 1 ColdDuct Cooling Coil']['availability_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cooling_coil_setpoint_control_type_fixed_setpoint_"
                                              "dual_fan_draw_through")
    def test_cooling_coil_setpoint_control_type_fixed_setpoint_dual_draw_through(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cold_duct_supply_fan_placement'] = \
            'DrawThrough'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cooling_coil_setpoint_control_type'] = \
            'FixedSetpoint'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'SYS 1 ColdDuct Supply Fan Outlet',
            epjson_output['SetpointManager:Scheduled']['SYS 1 ColdDuct Cooling Supply Air Temp Manager'][
                'setpoint_node_or_nodelist_name'])
        self.assertEqual(
            'SYS 1 ColdDuct Cooling Setpoint Nodes',
            epjson_output['SetpointManager:MixedAir']['SYS 1 ColdDuct Cooling Air Temp Manager'][
                'setpoint_node_or_nodelist_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cooling_coil_setpoint_control_type_fixed_setpoint_"
                                              "dual_fan_draw_through")
    def test_cooling_coil_setpoint_control_type_fixed_setpoint_dual_blow_through(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cold_duct_supply_fan_placement'] = \
            'BlowThrough'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cooling_coil_setpoint_control_type'] = \
            'FixedSetpoint'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'SYS 1 ColdDuct Cooling Setpoint Nodes',
            epjson_output['SetpointManager:Scheduled']['SYS 1 ColdDuct Cooling Supply Air Temp Manager'][
                'setpoint_node_or_nodelist_name'])
        return

    def test_cooling_coil_setpoint_control_type_fixed_setpoint_single(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'SingleFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cooling_coil_setpoint_control_type'] = \
            'FixedSetpoint'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'SYS 1 ColdDuct Cooling Setpoint Nodes',
            epjson_output['SetpointManager:Scheduled']['SYS 1 ColdDuct Cooling Supply Air Temp Manager'][
                'setpoint_node_or_nodelist_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cooling_coil_setpoint_control_type_scheduled_"
                                              "dual_fan_draw_through")
    def test_cooling_coil_setpoint_control_type_scheduled_dual_draw_through(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cold_duct_supply_fan_placement'] = \
            'DrawThrough'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cooling_coil_setpoint_control_type'] = \
            'Scheduled'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'SYS 1 ColdDuct Supply Fan Outlet',
            epjson_output['SetpointManager:Scheduled']['SYS 1 ColdDuct Cooling Supply Air Temp Manager'][
                'setpoint_node_or_nodelist_name'])
        self.assertEqual(
            'SYS 1 ColdDuct Cooling Setpoint Nodes',
            epjson_output['SetpointManager:MixedAir']['SYS 1 ColdDuct Cooling Air Temp Manager'][
                'setpoint_node_or_nodelist_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cooling_coil_setpoint_control_type_scheduled_"
                                              "dual_fan_blow_through")
    def test_cooling_coil_setpoint_control_type_scheduled_dual_blow_through(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cold_duct_supply_fan_placement'] = \
            'BlowThrough'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cooling_coil_setpoint_control_type'] = \
            'Scheduled'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'SYS 1 ColdDuct Cooling Setpoint Nodes',
            epjson_output['SetpointManager:Scheduled']['SYS 1 ColdDuct Cooling Supply Air Temp Manager'][
                'setpoint_node_or_nodelist_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cooling_coil_setpoint_control_type_scheduled_"
                                              "single")
    def test_cooling_coil_setpoint_control_type_scheduled_single(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'SingleFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cooling_coil_setpoint_control_type'] = \
            'Scheduled'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'SYS 1 ColdDuct Cooling Setpoint Nodes',
            epjson_output['SetpointManager:Scheduled']['SYS 1 ColdDuct Cooling Supply Air Temp Manager'][
                'setpoint_node_or_nodelist_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cooling_coil_setpoint_control_type_outdoor_air_temperature_reset_"
                                              "dual_fan_draw_through")
    def test_cooling_coil_setpoint_control_type_outdoor_air_temperature_reset_dual_draw_through(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cold_duct_supply_fan_placement'] = \
            'DrawThrough'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cooling_coil_setpoint_control_type'] = \
            'OutdoorAirTemperatureReset'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'SYS 1 ColdDuct Supply Fan Outlet',
            epjson_output['SetpointManager:OutdoorAirReset']['SYS 1 ColdDuct Cooling Supply Air Temp Manager'][
                'setpoint_node_or_nodelist_name'])
        self.assertEqual(
            'SYS 1 ColdDuct Cooling Setpoint Nodes',
            epjson_output['SetpointManager:MixedAir']['SYS 1 ColdDuct Cooling Air Temp Manager'][
                'setpoint_node_or_nodelist_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cooling_coil_setpoint_control_type_outdoor_air_temperature_reset_"
                                              "dual_fan_blow_through")
    def test_cooling_coil_setpoint_control_type_outdoor_air_temperature_reset_dual_blow_through(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cold_duct_supply_fan_placement'] = \
            'BlowThrough'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cooling_coil_setpoint_control_type'] = \
            'OutdoorAirTemperatureReset'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'SYS 1 ColdDuct Cooling Setpoint Nodes',
            epjson_output['SetpointManager:OutdoorAirReset']['SYS 1 ColdDuct Cooling Supply Air Temp Manager'][
                'setpoint_node_or_nodelist_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cooling_coil_setpoint_control_type_outdoor_air_temperature_reset_"
                                              "dual_fan_blow_through")
    def test_cooling_coil_setpoint_control_type_outdoor_air_temperature_reset_single(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'SingleFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cooling_coil_setpoint_control_type'] = \
            'OutdoorAirTemperatureReset'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'SYS 1 ColdDuct Cooling Setpoint Nodes',
            epjson_output['SetpointManager:OutdoorAirReset']['SYS 1 ColdDuct Cooling Supply Air Temp Manager'][
                'setpoint_node_or_nodelist_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cooling_coil_setpoint_control_type_warmest_"
                                              "dual_fan_draw_through")
    def test_cooling_coil_setpoint_control_type_warmest_dual_draw_through(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cold_duct_supply_fan_placement'] = \
            'DrawThrough'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cooling_coil_setpoint_control_type'] = \
            'Warmest'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'SYS 1 ColdDuct Supply Fan Outlet',
            epjson_output['SetpointManager:Warmest']['SYS 1 ColdDuct Cooling Supply Air Temp Manager'][
                'setpoint_node_or_nodelist_name'])
        self.assertEqual(
            'SYS 1 ColdDuct Cooling Setpoint Nodes',
            epjson_output['SetpointManager:MixedAir']['SYS 1 ColdDuct Cooling Air Temp Manager'][
                'setpoint_node_or_nodelist_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cooling_coil_setpoint_control_type_warmest_"
                                              "dual_fan_draw_through")
    def test_cooling_coil_setpoint_control_type_warmest_dual_blow_through(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cold_duct_supply_fan_placement'] = \
            'BlowThrough'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cooling_coil_setpoint_control_type'] = \
            'Warmest'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'SYS 1 ColdDuct Cooling Setpoint Nodes',
            epjson_output['SetpointManager:Warmest']['SYS 1 ColdDuct Cooling Supply Air Temp Manager'][
                'setpoint_node_or_nodelist_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cooling_coil_setpoint_control_type_warmest_"
                                              "single")
    def test_cooling_coil_setpoint_control_type_warmest_single(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'SingleFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cooling_coil_setpoint_control_type'] = \
            'Warmest'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'SYS 1 ColdDuct Cooling Setpoint Nodes',
            epjson_output['SetpointManager:Warmest']['SYS 1 ColdDuct Cooling Supply Air Temp Manager'][
                'setpoint_node_or_nodelist_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cooling_coil_warmest_temperature")
    def test_cooling_coil_warmest_temperature(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cooling_coil_setpoint_control_type'] = \
            'Warmest'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cooling_coil_design_setpoint_temperature'] = 13
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            18.2,
            epjson_output['SetpointManager:Warmest']['SYS 1 ColdDuct Cooling Supply Air Temp Manager'][
                'maximum_setpoint_temperature'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cooling_coil_design_setpoint_temperature")
    def test_cooling_coil_design_setpoint_temperature(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cooling_coil_design_setpoint_temperature'] = 13
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            13,
            epjson_output['Sizing:System']['SYS 1 Sizing System']['central_cooling_design_supply_air_temperature'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:"
                                              "cooling_coil_setpoint_schedule_name")
    def test_cooling_coil_setpoint_schedule_name(self):
        self.ej.merge_epjson(
            super_dictionary=self.base_epjson,
            object_dictionary=schedule_objects)
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cooling_coil_setpoint_control_type'] = \
            'Scheduled'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cooling_coil_setpoint_schedule_name'] = 'Always12.5'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'Always12.5',
            epjson_output['SetpointManager:Scheduled']['SYS 1 ColdDuct Cooling Supply Air Temp Manager'][
                'schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DualDuct:cooling_coil_outdoor_reset_inputs")
    def test_cooling_coil_outdoor_reset_inputs(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['system_configuration_type'] = \
            'DualFanVariableVolume'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1']['cooling_coil_setpoint_control_type'] = \
            'OutdoorAirTemperatureReset'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1'][
            'cooling_coil_setpoint_control_type'] = 'OutdoorAirTemperatureReset'
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1'][
            'cooling_coil_setpoint_at_outdoor_dry_bulb_low'] = 15.5
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1'][
            'cooling_coil_reset_outdoor_dry_bulb_low'] = 15.4
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1'][
            'cooling_coil_setpoint_at_outdoor_dry_bulb_high'] = 12.5
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1'][
            'cooling_coil_reset_outdoor_dry_bulb_high'] = 23.2
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            23.2,
            epjson_output['SetpointManager:OutdoorAirReset']['SYS 1 ColdDuct Cooling Supply Air Temp Manager'][
                'outdoor_high_temperature'])
        self.assertEqual(
            12.5,
            epjson_output['SetpointManager:OutdoorAirReset']['SYS 1 ColdDuct Cooling Supply Air Temp Manager'][
                'setpoint_at_outdoor_high_temperature'])
        self.assertEqual(
            15.4,
            epjson_output['SetpointManager:OutdoorAirReset']['SYS 1 ColdDuct Cooling Supply Air Temp Manager'][
                'outdoor_low_temperature'])
        self.assertEqual(
            15.5,
            epjson_output['SetpointManager:OutdoorAirReset']['SYS 1 ColdDuct Cooling Supply Air Temp Manager'][
                'setpoint_at_outdoor_low_temperature'])
        return