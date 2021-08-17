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
            epjson_output['Coil:Cooling:DX:TwoSpeed'].get('Sys 1 Furnace DX Cool SnglSpd Cooling Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "cooling_coil_type_multi_speed_dx")
    def test_cooling_coil_type_multi_speed_dx(self):
        # todo_eo: EO fails with input error on value type
        #   [Coil:Cooling:DX:MultiSpeed][Sys 1 Furnace DX Cool SnglSpd Cooling Coil]
        #   [speed_2_evaporative_condenser_effectiveness] - Value type "string" for input
        #   "Dimensionless" not permitted by \'type\' constraint.\r\n<root>[Coil:Cooling:DX:MultiSpeed]
        #   [Sys 1 Furnace DX Cool SnglSpd Cooling Coil][speed_2_gross_rated_sensible_heat_ratio] -
        #   Value type "string" for input "Sys 1 Furnace DX Cool SnglSpd Cool Coil Cap-FT" not permitted by
        #   \'type\' constraint.
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'cooling_coil_type'] = 'MultiSpeedDX'
        # proper speed input must be se to pass schema validation
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'number_of_speeds_for_cooling'] = 2
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Coil:Cooling:DX:TwoSpeed'].get('Sys 1 Furnace DX Cool SnglSpd Cooling Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "cooling_coil_type_two_stage_dx")
    def test_cooling_coil_type_two_stage_dx(self):
        # todo_eo: humidity control enabled on this option, which is not consistent with other systems
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'cooling_coil_type'] = 'TwoStageDX'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Coil:Cooling:DX:TwoStageWithHumidityControlMode']
            .get('Sys 1 Furnace DX Cool SnglSpd Cooling Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "cooling_coil_type_two_stage_humidity_control_dx")
    def test_cooling_coil_type_two_stage_humidity_control_dx(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'cooling_coil_type'] = 'TwoStageHumidityControlDX'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Coil:Cooling:DX:TwoStageWithHumidityControlMode']
            .get('Sys 1 Furnace DX Cool SnglSpd Cooling Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "cooling_coil_type_heat_exchanger_assisted_dx")
    def test_cooling_coil_type_heat_exchanger_assisted_dx(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'cooling_coil_type'] = 'HeatExchangerAssistedDX'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['CoilSystem:Cooling:DX:HeatExchangerAssisted']
            .get('Sys 1 Furnace DX Cool SnglSpd Heat Exchanger Assisted Cooling Coil'))
        self.assertIsNotNone(
            epjson_output['HeatExchanger:AirToAir:SensibleAndLatent']
            .get('Sys 1 Furnace DX Cool SnglSpd Cooling Coil Heat Exchanger'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "cooling_coil_type_single_speed_dx_water_cooled")
    def test_cooling_coil_type_single_speed_dx_water_cooled(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'cooling_coil_type'] = 'SingleSpeedDXWaterCooled'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Coil:Cooling:WaterToAirHeatPump:EquationFit']
            .get('Sys 1 Furnace DX Cool SnglSpd Cooling Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "cooling_coil_type_chilled_water")
    def test_cooling_coil_type_chilled_water(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'cooling_coil_type'] = 'ChilledWater'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Coil:Cooling:Water']
            .get('Sys 1 Furnace DX Cool SnglSpd Cooling Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "cooling_coil_type_chilled_water_detailed_flat_model")
    def test_cooling_coil_type_chilled_water_detailed_flat_model(self):
        # todo_eo: EO and pyEO fail with same error.  ** Severe  ** Coil:Cooling:Water:DetailedGeometry:
        #  "SYS 1 FURNACE DX COOL SNGLSPD COOLING COIL"
        #  **   ~~~   ** Coil Minimum Airflow Area must be greater than 0. Coil area = 0.000000
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'cooling_coil_type'] = 'ChilledWaterDetailedFlatModel'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        # self.assertIsNotNone(
        #     epjson_output['Coil:Cooling:Water']
        #     .get('Sys 1 Furnace DX Cool SnglSpd Cooling Coil'))
        return

    def test_cooling_coil_type_heat_exchanger_assisted_chilled_water(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'cooling_coil_type'] = 'HeatExchangerAssistedChilledWater'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Coil:Cooling:Water']
            .get('Sys 1 Furnace DX Cool SnglSpd Cooling Coil'))
        self.assertIsNotNone(
            epjson_output['HeatExchanger:AirToAir:SensibleAndLatent']
            .get('Sys 1 Furnace DX Cool SnglSpd Cooling Coil Heat Exchanger'))
        return

    def test_cooling_coil_type_none(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'cooling_coil_type'] = 'None'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNone(
            epjson_output['Coil:Cooling:DX:SingleSpeed']
            .get('Sys 1 Furnace DX Cool SnglSpd Cooling Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "cooling_coil_availability_schedule_name")
    def test_cooling_coil_availability_schedule_name(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'cooling_coil_availability_schedule_name'] = 'OCCUPY-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['Coil:Cooling:DX:SingleSpeed']['Sys 1 Furnace DX Cool SnglSpd Cooling Coil'][
                'availability_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "cooling_design_supply_air_temperature")
    def test_cooling_design_supply_air_temperature(self):
        # todo_eo: why is the SetpointManager:SingleZone:Cooling object not affected by this input
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'cooling_design_supply_air_temperature'] = 12.9
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            12.9,
            epjson_output['Sizing:System']['Sys 1 Furnace DX Cool SnglSpd Sizing System'][
                'central_cooling_design_supply_air_temperature'])
        self.assertEqual(
            12.9,
            epjson_output['SetpointManager:SingleZone:Cooling'][
                'Sys 1 Furnace DX Cool SnglSpd Cooling Supply Air Temp Manager']['minimum_supply_air_temperature'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "dx_cooling_coil_gross_rated_total_capacity")
    def test_dx_cooling_coil_gross_rated_total_capacity(self):
        # todo_eo: It appears that SHR and cooling capacity should be required for sizing but EO doesn't enforce it.
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'dx_cooling_coil_gross_rated_sensible_heat_ratio'] = 0.66
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'dx_cooling_coil_gross_rated_total_capacity'] = 2000
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            2000,
            epjson_output['Coil:Cooling:DX:SingleSpeed']['Sys 1 Furnace DX Cool SnglSpd Cooling Coil'][
                'gross_rated_total_cooling_capacity'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "dx_cooling_coil_gross_rated_cop")
    def test_dx_cooling_coil_gross_rated_cop(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'dx_cooling_coil_gross_rated_cop'] = 2.77
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            2.77,
            epjson_output['Coil:Cooling:DX:SingleSpeed']['Sys 1 Furnace DX Cool SnglSpd Cooling Coil'][
                'gross_rated_cooling_cop'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "heating_coil_type_gas")
    def test_heating_coil_type_gas(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'heating_coil_type'] = 'Gas'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Coil:Heating:Fuel'].get('Sys 1 Furnace DX Cool SnglSpd Heating Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "heating_coil_type_electric")
    def test_heating_coil_type_electric(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'heating_coil_type'] = 'Electric'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Coil:Heating:Electric'].get('Sys 1 Furnace DX Cool SnglSpd Heating Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "heating_coil_type_hot_water")
    def test_heating_coil_type_hot_water(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'heating_coil_type'] = 'HotWater'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Coil:Heating:Water'].get('Sys 1 Furnace DX Cool SnglSpd Heating Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "heating_coil_type_single_speed_dx_heat_pump_air_source")
    def test_heating_coil_type_single_speed_dx_heat_pump_air_source(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'heating_coil_type'] = 'SingleSpeedDXHeatPumpAirSource'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Coil:Heating:DX:SingleSpeed'].get('Sys 1 Furnace DX Cool SnglSpd Heating Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "heating_coil_type_multi_speed_dx_heat_pump_air_source")
    def test_heating_coil_type_multi_speed_dx_heat_pump_air_source(self):
        # todo_eo: EO fails so making identical template objects is difficult.  Check in with team
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'heating_coil_type'] = 'MultiSpeedDXHeatPumpAirSource'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Coil:Heating:DX:SingleSpeed'].get('Sys 1 Furnace DX Cool SnglSpd Heating Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "heating_coil_type_single_speed_dx_heat_pump_water_source")
    def test_heating_coil_type_single_speed_dx_heat_pump_water_source(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'heating_coil_type'] = 'SingleSpeedDXHeatPumpWaterSource'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Coil:Heating:WaterToAirHeatPump:EquationFit']
            .get('Sys 1 Furnace DX Cool SnglSpd Heating Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "heating_coil_type_multi_stage_electric")
    def test_heating_coil_type_multi_stage_electric(self):
        # todo_eo: EO fails and unable to make comparison for template objects
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'number_of_speeds_or_stages_for_heating'] = 2
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'heating_coil_type'] = 'MultiStageElectric'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Coil:Heating:WaterToAirHeatPump:EquationFit']
            .get('Sys 1 Furnace DX Cool SnglSpd Heating Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "heating_coil_type_multi_stage_gas")
    def test_heating_coil_type_multi_stage_gas(self):
        # todo_eo: EO fails and unable to make comparison for template objects
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'number_of_speeds_or_stages_for_heating'] = 2
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'heating_coil_type'] = 'MultiStageGas'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Coil:Heating:WaterToAirHeatPump:EquationFit']
            .get('Sys 1 Furnace DX Cool SnglSpd Heating Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "heating_coil_type_none")
    def test_heating_coil_type_none(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'heating_coil_type'] = 'None'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNone(
            epjson_output.get('Coil:Heating:Fuel'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "heating_coil_type_none")
    def test_cooling_coil_type_none_heating_coil_type_none(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'cooling_coil_type'] = 'None'
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'heating_coil_type'] = 'None'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNone(
            epjson_output.get('Coil:Heating:Fuel'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "heating_coil_type_none")
    def test_cooling_coil_type_none_heating_coil_type_none_with_supplemental(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'cooling_coil_type'] = 'None'
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'heating_coil_type'] = 'None'
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'supplemental_heating_or_reheat_coil_type'] = 'Electric'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNone(
            epjson_output.get('Coil:Heating:Fuel'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "heat_pump_heating_coil_availability_schedule_name")
    def test_heating_coil_availability_schedule_name(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'heating_coil_availability_schedule_name'] = 'OCCUPY-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['Coil:Heating:Fuel'][
                'Sys 1 Furnace DX Cool SnglSpd Heating Coil']['availability_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "heating_design_supply_air_temperature")
    def test_heating_design_supply_air_temperature(self):
        # todo_eo: why is the SetpointManager:SingleZone:Cooling object not affected by this input
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'heating_design_supply_air_temperature'] = 48
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            48,
            epjson_output['Sizing:System']['Sys 1 Furnace DX Cool SnglSpd Sizing System'][
                'central_heating_design_supply_air_temperature'])
        self.assertEqual(
            48,
            epjson_output['SetpointManager:SingleZone:Cooling'][
                'Sys 1 Furnace DX Cool SnglSpd Cooling Supply Air Temp Manager']['maximum_supply_air_temperature'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "heating_coil_gross_rated_capacity_hot_water")
    def test_heating_coil_gross_rated_capacity_hot_water(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'heating_coil_type'] = 'HotWater'
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'heating_coil_gross_rated_capacity'] = 2000
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            2000,
            epjson_output['Coil:Heating:Water']['Sys 1 Furnace DX Cool SnglSpd Heating Coil']['rated_capacity'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "heating_coil_gross_rated_capacity_gas")
    def test_heating_coil_gross_rated_capacity_gas(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'heating_coil_type'] = 'Gas'
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'heating_coil_gross_rated_capacity'] = 2000
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            2000,
            epjson_output['Coil:Heating:Fuel']['Sys 1 Furnace DX Cool SnglSpd Heating Coil']['nominal_capacity'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "heating_coil_gross_rated_capacity_electric")
    def test_heating_coil_gross_rated_capacity_electric(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'heating_coil_type'] = 'Electric'
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'heating_coil_gross_rated_capacity'] = 2000
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            2000,
            epjson_output['Coil:Heating:Electric']['Sys 1 Furnace DX Cool SnglSpd Heating Coil']['nominal_capacity'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "gas_heating_coil_efficiency")
    def test_gas_heating_coil_efficiency(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'gas_heating_coil_efficiency'] = 0.77
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.77,
            epjson_output['Coil:Heating:Fuel']['Sys 1 Furnace DX Cool SnglSpd Heating Coil']['burner_efficiency'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "gas_heating_coil_parasitic_electric_load")
    def test_gas_heating_coil_parasitic_electric_load(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'gas_heating_coil_parasitic_electric_load'] = 1
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            1,
            epjson_output['Coil:Heating:Fuel']['Sys 1 Furnace DX Cool SnglSpd Heating Coil']['parasitic_electric_load'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "heat_pump_heating_coil_gross_rated_cop")
    def test_heat_pump_heating_coil_gross_rated_cop(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'heating_coil_type'] = 'SingleSpeedDXHeatPumpAirSource'
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'heat_pump_heating_coil_gross_rated_cop'] = 2.9
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            2.9,
            epjson_output['Coil:Heating:DX:SingleSpeed']['Sys 1 Furnace DX Cool SnglSpd Heating Coil'][
                'gross_rated_heating_cop'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitarySystem:"
                                              "heat_pump_outdoor_dry_bulb_temperatures")
    def test_heat_pump_outdoor_dry_bulb_temperatures(self):
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'heating_coil_type'] = 'SingleSpeedDXHeatPumpAirSource'
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'heat_pump_heating_minimum_outdoor_dry_bulb_temperature'] = -7
        self.base_epjson['HVACTemplate:System:UnitarySystem']['Sys 1 Furnace DX Cool SnglSpd'][
            'heat_pump_defrost_maximum_outdoor_dry_bulb_temperature'] = 2
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            -7,
            epjson_output['Coil:Heating:DX:SingleSpeed']['Sys 1 Furnace DX Cool SnglSpd Heating Coil'][
                'minimum_outdoor_dry_bulb_temperature_for_compressor_operation'])
        self.assertEqual(
            2,
            epjson_output['Coil:Heating:DX:SingleSpeed']['Sys 1 Furnace DX Cool SnglSpd Heating Coil'][
                'maximum_outdoor_dry_bulb_temperature_for_defrost_operation'])
        return
