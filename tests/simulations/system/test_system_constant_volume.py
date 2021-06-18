from pathlib import Path

from tests.simulations import BaseSimulationTest
from src.epjson_handler import EPJSON

test_dir = Path(__file__).parent.parent.parent


class TestSimulationsSystemConstantVolume(BaseSimulationTest):
    def setUp(self):
        self.ej = EPJSON()
        base_idf_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles', 'HVACTemplate-5ZoneConstantVolumeChillerBoiler.idf')
        base_copy_file_path = self._copy_to_test_directory(base_idf_file_path)
        # read in base file, then edit inputs for alternate tests
        self.base_epjson = self.get_epjson_object_from_idf_file(base_copy_file_path)
        return

    def teardown(self):
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:system_availability_schedule_name")
    def test_system_availability_schedule_name(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4']['system_availability_schedule_name'] = 'OCCUPY-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['Fan:ConstantVolume']['AHU 1 Spaces 1-4 Supply Fan']['availability_schedule_name'])
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['AvailabilityManager:NightCycle']['AHU 1 Spaces 1-4 Availability']['fan_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:supply_fan_maximum_flow_rate")
    def test_supply_fan_maximum_flow_rate(self):
        # todo_eo: legacy does not seem to updated Fan:ConstantVolume or AirLoopHVAC
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4']['supply_fan_maximum_flow_rate'] = 2.0
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            2.0,
            epjson_output['Fan:ConstantVolume']['AHU 1 Spaces 1-4 Supply Fan']['maximum_flow_rate'])
        self.assertEqual(
            2.0,
            epjson_output['AirLoopHVAC']['AHU 1 Spaces 1-4']['design_supply_air_flow_rate'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:supply_fan_total_efficiency")
    def test_supply_fan_total_efficiency(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4']['supply_fan_total_efficiency'] = 0.65
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.65,
            epjson_output['Fan:ConstantVolume']['AHU 1 Spaces 1-4 Supply Fan']['fan_total_efficiency'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:supply_fan_delta_pressure")
    def test_supply_fan_delta_pressure(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4']['supply_fan_delta_pressure'] = 500
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            500,
            epjson_output['Fan:ConstantVolume']['AHU 1 Spaces 1-4 Supply Fan']['pressure_rise'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:supply_fan_motor_efficiency")
    def test_supply_fan_motor_efficiency(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4']['supply_fan_motor_efficiency'] = 0.8
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.8,
            epjson_output['Fan:ConstantVolume']['AHU 1 Spaces 1-4 Supply Fan']['motor_efficiency'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:supply_fan_motor_in_air_stream_fraction")
    def test_supply_fan_motor_in_air_stream_fraction(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'supply_fan_motor_in_air_stream_fraction'] = 0.9
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.9,
            epjson_output['Fan:ConstantVolume']['AHU 1 Spaces 1-4 Supply Fan']['motor_in_airstream_fraction'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:supply_fan_placement_draw_through")
    def test_supply_fan_placement_draw_through(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'supply_fan_placement'] = 'DrawThrough'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'AHU 1 Spaces 1-4 Heating Coil Outlet',
            epjson_output['Fan:ConstantVolume']['AHU 1 Spaces 1-4 Supply Fan']['air_inlet_node_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:supply_fan_placement_blow_through")
    def test_supply_fan_placement_blow_through(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'supply_fan_placement'] = 'BlowThrough'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'AHU 1 Spaces 1-4 Heating Coil Outlet',
            epjson_output['Fan:ConstantVolume']['AHU 1 Spaces 1-4 Supply Fan']['air_inlet_node_name'])
        return