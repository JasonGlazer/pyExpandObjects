from pathlib import Path

from tests.simulations import BaseSimulationTest
from src.epjson_handler import EPJSON

test_dir = Path(__file__).parent.parent.parent


class TestSimulationsSystemUnitarySystem(BaseSimulationTest):
    def setUp(self):
        self.ej = EPJSON()
        base_idf_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles',
                                               'HVACTemplate-5ZoneUnitarySystem.idf')
        base_copy_file_path = self._copy_to_test_directory(base_idf_file_path)
        # read in base file, then edit inputs for alternate tests
        self.base_epjson = self.get_epjson_object_from_idf_file(base_copy_file_path)
        # todo_eo: errors output in legaacy unless non-default system is set to single speed dx
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 2 Furnace DX Cool MultiSpd'][
            'cooling_coil_type'] = 'SingleSpeedDX'
        self.base_epjson.pop('Output:Variable')
        return

    def teardown(self):
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:system_availability_schedule_name")
    def test_system_availability_schedule_name(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'system_availability_schedule_name'] = 'OCCUPY-1'
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'night_cycle_control'] = 'CycleOnAny'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['Fan:OnOff']['Sys 1 Furnace DX Cool SnglSpd Supply Fan']['availability_schedule_name'])
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['AvailabilityManager:NightCycle']['Sys 1 Furnace DX Cool SnglSpd Availability'][
                'fan_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "control_type_load")
    def test_control_type_load(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'control_type'] = 'Load'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'Load',
            epjson_output['AirLoopHVAC:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd Unitary System'][
                'control_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "control_type_set_point")
    def test_control_type_set_point(self):
        # todo_eo: supply fan operating mode schedule must be constant or
        #  else error is issues, which happens in legacy
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'control_type'] = 'SetPoint'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'SetPoint',
            epjson_output['AirLoopHVAC:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd Unitary System'][
                'control_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:cooling_supplY_air_flow_rate")
    def test_cooling_supply_air_flow_rate(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'cooling_supply_air_flow_rate'] = 1.01
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            1.01,
            epjson_output['Sizing:System']['Sys 1 Furnace DX Cool SnglSpd Sizing System'][
                'cooling_supply_air_flow_rate'])
        self.assertEqual(
            1.01,
            epjson_output['AirLoopHVAC:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd Unitary System'][
                'cooling_supply_air_flow_rate'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:heating_supplY_air_flow_rate")
    def test_heating_supply_air_flow_rate(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'heating_supply_air_flow_rate'] = 1.01
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            1.01,
            epjson_output['Sizing:System']['Sys 1 Furnace DX Cool SnglSpd Sizing System'][
                'heating_supply_air_flow_rate'])
        self.assertEqual(
            1.01,
            epjson_output['AirLoopHVAC:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd Unitary System'][
                'heating_supply_air_flow_rate'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:no_load_supplY_air_flow_rate")
    def test_no_load_supply_air_flow_rate(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'no_load_supply_air_flow_rate'] = 1.01
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            1.01,
            epjson_output['AirLoopHVAC:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd Unitary System'][
                'no_load_supply_air_flow_rate'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "supply_fan_operating_mode_schedule_name")
    def test_supply_fan_operating_mode_schedule_name(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'supply_fan_operating_mode_schedule_name'] = 'OCCUPY-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['AirLoopHVAC:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd Unitary System'][
                'supply_air_fan_operating_mode_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "supply_fan_placement_blow_through")
    def test_supply_fan_placement_blow_through(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'supply_fan_placement'] = 'BlowThrough'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'BlowThrough',
            epjson_output['AirLoopHVAC:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd Unitary System'][
                'fan_placement'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "supply_fan_placement_draw_through")
    def test_supply_fan_placement_draw_through(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'supply_fan_placement'] = 'DrawThrough'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'DrawThrough',
            epjson_output['AirLoopHVAC:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd Unitary System'][
                'fan_placement'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:supply_fan_total_efficiency")
    def test_supply_fan_total_efficiency(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'supply_fan_total_efficiency'] = 0.65
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.65,
            epjson_output['Fan:OnOff']['Sys 1 Furnace DX Cool SnglSpd Supply Fan']['fan_total_efficiency'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:supply_fan_delta_pressure")
    def test_supply_fan_delta_pressure(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'supply_fan_delta_pressure'] = 500
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            500,
            epjson_output['Fan:OnOff']['Sys 1 Furnace DX Cool SnglSpd Supply Fan']['pressure_rise'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:supply_fan_motor_efficiency")
    def test_supply_fan_motor_efficiency(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'supply_fan_motor_efficiency'] = 0.8
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.8,
            epjson_output['Fan:OnOff']['Sys 1 Furnace DX Cool SnglSpd Supply Fan']['motor_efficiency'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "supply_fan_motor_in_air_stream_fraction")
    def test_supply_fan_motor_in_air_stream_fraction(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'supply_fan_motor_in_air_stream_fraction'] = 0.9
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.9,
            epjson_output['Fan:OnOff']['Sys 1 Furnace DX Cool SnglSpd Supply Fan']['motor_in_airstream_fraction'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "cooling_coil_type_single_speed_dx")
    def test_cooling_coil_type_single_speed_dx(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'cooling_coil_type'] = 'SingleSpeedDX'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Coil:Cooling:DX:SingleSpeed'].get('Sys 1 Furnace DX Cool SnglSpd Cooling Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "cooling_coil_type_two_speed_dx")
    def test_cooling_coil_type_two_speed_dx(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'cooling_coil_type'] = 'TwoSpeedDX'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Coil:Cooling:DX:SingleSpeed'].get('Sys 1 Furnace DX Cool SnglSpd Cooling Coil'))
        return
