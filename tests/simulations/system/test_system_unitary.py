from pathlib import Path

from tests.simulations import BaseSimulationTest
from src.epjson_handler import EPJSON

test_dir = Path(__file__).parent.parent.parent

hot_water_objects = {
    "HVACTemplate:Plant:Boiler": {
        "Main Boiler": {
            "boiler_type": "HotWaterBoiler",
            "capacity": "Autosize",
            "efficiency": 0.8,
            "fuel_type": "NaturalGas",
            "priority": "1"
        }
    },
    "HVACTemplate:Plant:HotWaterLoop": {
        "Hot Water Loop": {
            "hot_water_design_setpoint": 82,
            "hot_water_plant_operation_scheme_type": "Default",
            "hot_water_pump_configuration": "ConstantFlow",
            "hot_water_pump_rated_head": 179352,
            "hot_water_reset_outdoor_dry_bulb_high": 10,
            "hot_water_reset_outdoor_dry_bulb_low": -6.7,
            "hot_water_setpoint_at_outdoor_dry_bulb_high": 65.6,
            "hot_water_setpoint_at_outdoor_dry_bulb_low": 82.2,
            "hot_water_setpoint_reset_type": "OutdoorAirTemperatureReset",
            "pump_control_type": "Intermittent"
        }
    }
}


class TestSimulationsSystemUnitary(BaseSimulationTest):
    def setUp(self):
        self.ej = EPJSON()
        base_idf_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles', 'HVACTemplate-5ZoneFurnaceDX.idf')
        base_copy_file_path = self._copy_to_test_directory(base_idf_file_path)
        # read in base file, then edit inputs for alternate tests
        self.base_epjson = self.get_epjson_object_from_idf_file(base_copy_file_path)
        self.base_epjson.pop('Output:Variable')
        return

    def teardown(self):
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:Unitary:system_availability_schedule_name")
    def test_system_availability_schedule_name(self):
        self.base_epjson['HVACTemplate:System:Unitary']['Furnace DX 1-1'][
            'system_availability_schedule_name'] = 'OCCUPY-1'
        self.base_epjson['HVACTemplate:System:Unitary']['Furnace DX 1-1'][
            'night_cycle_control'] = 'CycleOnAny'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['Fan:OnOff']['Furnace DX 1-1 Supply Fan']['availability_schedule_name'])
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['AvailabilityManager:NightCycle']['Furnace DX 1-1 Availability']['fan_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:Unitary:supply_fan_maximum_flow_rate")
    def test_supply_fan_maximum_flow_rate(self):
        self.base_epjson['HVACTemplate:System:Unitary']['Furnace DX 1-1']['supply_fan_maximum_flow_rate'] = 1.01
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            1.01,
            epjson_output['Sizing:System']['Furnace DX 1-1 Sizing System']['cooling_supply_air_flow_rate'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:Unitary:supply_fan_operating_mode_schedule_name")
    def test_supply_fan_operating_mode_schedule_name(self):
        self.base_epjson['HVACTemplate:System:Unitary']['Furnace DX 1-1'][
            'supply_fan_operating_mode_schedule_name'] = 'OCCUPY-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['AirLoopHVAC:Unitary:Furnace:HeatCool']['Furnace DX 1-1 Furnace with DX Cooling'][
                'supply_air_fan_operating_mode_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:Unitary:supply_fan_total_efficiency")
    def test_supply_fan_total_efficiency(self):
        self.base_epjson['HVACTemplate:System:Unitary']['Furnace DX 1-1']['supply_fan_total_efficiency'] = 0.65
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.65,
            epjson_output['Fan:OnOff']['Furnace DX 1-1 Supply Fan']['fan_total_efficiency'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:Unitary:supply_fan_delta_pressure")
    def test_supply_fan_delta_pressure(self):
        self.base_epjson['HVACTemplate:System:Unitary']['Furnace DX 1-1']['supply_fan_delta_pressure'] = 500
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            500,
            epjson_output['Fan:OnOff']['Furnace DX 1-1 Supply Fan']['pressure_rise'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:Unitary:supply_fan_motor_efficiency")
    def test_supply_fan_motor_efficiency(self):
        self.base_epjson['HVACTemplate:System:Unitary']['Furnace DX 1-1']['supply_fan_motor_efficiency'] = 0.8
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.8,
            epjson_output['Fan:OnOff']['Furnace DX 1-1 Supply Fan']['motor_efficiency'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:Unitary:supply_fan_motor_in_air_stream_fraction")
    def test_supply_fan_motor_in_air_stream_fraction(self):
        self.base_epjson['HVACTemplate:System:Unitary']['Furnace DX 1-1'][
            'supply_fan_motor_in_air_stream_fraction'] = 0.9
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.9,
            epjson_output['Fan:OnOff']['Furnace DX 1-1 Supply Fan']['motor_in_airstream_fraction'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:Unitary:cooling_coil_type_single_speed_dx")
    def test_cooling_coil_type_single_speed_dx(self):
        self.base_epjson['HVACTemplate:System:Unitary']['Furnace DX 1-1'][
            'cooling_coil_type'] = 'SingleSpeedDX'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Coil:Cooling:DX:SingleSpeed'].get('Furnace DX 1-1 Cooling Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:Unitary:cooling_coil_type_none")
    def test_cooling_coil_type_none(self):
        self.base_epjson['HVACTemplate:System:Unitary']['Furnace DX 1-1'][
            'cooling_coil_type'] = 'None'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNone(
            epjson_output['Coil:Cooling:DX:SingleSpeed'].get('Furnace DX 1-1 Cooling Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:Unitary:cooling_coil_availability_schedule_name")
    def test_cooling_coil_availability_schedule_name(self):
        self.base_epjson['HVACTemplate:System:Unitary']['Furnace DX 1-1'][
            'cooling_coil_availability_schedule_name'] = 'OCCUPY-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['Coil:Cooling:DX:SingleSpeed']['Furnace DX 1-1 Cooling Coil']['availability_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:Unitary:"
                                              "cooling_coil_design_supply_air_temperature")
    def test_cooling_coil_design_supply_air_temperature(self):
        # todo_eo: why is the SetpointManager:SingleZone:Cooling object not affected by this input
        self.base_epjson['HVACTemplate:System:Unitary']['Furnace DX 1-1'][
            'cooling_design_supply_air_temperature'] = 12.9
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            12.9,
            epjson_output['Sizing:System']['Furnace DX 1-1 Sizing System'][
                'central_cooling_design_supply_air_temperature'])
        self.assertEqual(
            12.9,
            epjson_output['SetpointManager:SingleZone:Cooling']['Furnace DX 1-1 Cooling Supply Air Temp Manager'][
                'minimum_supply_air_temperature'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:Unitary:"
                                              "cooling_coil_gross_rated_total_capacity")
    def test_cooling_coil_gross_rated_total_capacity(self):
        self.base_epjson['HVACTemplate:System:Unitary']['Furnace DX 1-1'][
            'cooling_coil_gross_rated_total_capacity'] = 2000
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            2000,
            epjson_output['Coil:Cooling:DX:SingleSpeed']['Furnace DX 1-1 Cooling Coil'][
                'gross_rated_total_cooling_capacity'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:Unitary:"
                                              "cooling_coil_gross_rated_sensible_heat_ratio")
    def test_cooling_coil_gross_rated_sensible_heat_ratio(self):
        self.base_epjson['HVACTemplate:System:Unitary']['Furnace DX 1-1'][
            'cooling_coil_gross_rated_sensible_heat_ratio'] = 0.75
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.75,
            epjson_output['Coil:Cooling:DX:SingleSpeed']['Furnace DX 1-1 Cooling Coil'][
                'gross_rated_sensible_heat_ratio'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:Unitary:"
                                              "cooling_coil_gross_rated_cop")
    def test_cooling_coil_gross_rated_cop(self):
        self.base_epjson['HVACTemplate:System:Unitary']['Furnace DX 1-1'][
            'cooling_coil_gross_rated_cop'] = 3.1
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            3.1,
            epjson_output['Coil:Cooling:DX:SingleSpeed']['Furnace DX 1-1 Cooling Coil'][
                'gross_rated_cooling_cop'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:Unitary:heating_coil_type_electric")
    def test_heating_coil_type_electric(self):
        self.base_epjson['HVACTemplate:System:Unitary']['Furnace DX 1-1'][
            'heating_coil_type'] = 'Electric'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Coil:Heating:Electric'].get('Furnace DX 1-1 Heating Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:Unitary:heating_coil_type_gas")
    def test_heating_coil_type_gas(self):
        self.base_epjson['HVACTemplate:System:Unitary']['Furnace DX 1-1'][
            'heating_coil_type'] = 'Gas'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Coil:Heating:Fuel'].get('Furnace DX 1-1 Heating Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:Unitary:heating_coil_type_hot_water")
    def test_heating_coil_type_hot_water(self):
        self.ej.merge_epjson(
            super_dictionary=self.base_epjson,
            object_dictionary=hot_water_objects)
        self.base_epjson['HVACTemplate:System:Unitary']['Furnace DX 1-1'][
            'heating_coil_type'] = 'HotWater'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Coil:Heating:Water'].get('Furnace DX 1-1 Heating Coil'))
        return
