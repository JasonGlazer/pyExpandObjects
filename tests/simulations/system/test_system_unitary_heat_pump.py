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

schedule_objects = {
    "Schedule:Compact": {
        "Always0.8": {
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
                    "field": 0.8
                }
            ],
            "schedule_type_limits_name": "Any Number"
        },
        "Always6.8": {
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
                    "field": 6.8
                }
            ],
            "schedule_type_limits_name": "Any Number"
        },
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
        },
        "Always15.5": {
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
                    "field": 15.5
                }
            ],
            "schedule_type_limits_name": "Any Number"
        },
        "Always62": {
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
                    "field": 62.0
                }
            ],
            "schedule_type_limits_name": "Any Number"
        },
        "Always29": {
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
                    "field": 29.0
                }
            ],
            "schedule_type_limits_name": "Any Number"
        }
    }
}


class TestSimulationsSystemUnitaryHeatPump(BaseSimulationTest):
    def setUp(self):
        self.ej = EPJSON()
        base_idf_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles',
                                               'HVACTemplate-5ZoneUnitaryHeatPump.idf')
        base_copy_file_path = self._copy_to_test_directory(base_idf_file_path)
        # read in base file, then edit inputs for alternate tests
        self.base_epjson = self.get_epjson_object_from_idf_file(base_copy_file_path)
        self.base_epjson.pop('Output:Variable')
        return

    def teardown(self):
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:system_availability_schedule_name")
    def test_system_availability_schedule_name(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'system_availability_schedule_name'] = 'OCCUPY-1'
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'night_cycle_control'] = 'CycleOnAny'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['Fan:OnOff']['Heat Pump 1 Supply Fan']['availability_schedule_name'])
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['AvailabilityManager:NightCycle']['Heat Pump 1 Availability']['fan_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:cooling_supplY_air_flow_rate")
    def test_cooling_supply_air_flow_rate(self):
        # todo_eo: rated_air_flow_rate in cooling coil is set by this input, but is not in other systems.  Is that
        #  correct?  Usually just the Sizing:System an AirLoop objects are set.
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'cooling_supply_air_flow_rate'] = 1.01
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            1.01,
            epjson_output['Sizing:System']['Heat Pump 1 Sizing System']['cooling_supply_air_flow_rate'])
        self.assertEqual(
            1.01,
            epjson_output['AirLoopHVAC:UnitaryHeatPump:AirToAir']['Heat Pump 1 Heat Pump'][
                'cooling_supply_air_flow_rate'])
        self.assertEqual(
            1.01,
            epjson_output['Coil:Cooling:DX:SingleSpeed']['Heat Pump 1 Cooling Coil'][
                'rated_air_flow_rate'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:heating_supplY_air_flow_rate")
    def test_heating_supply_air_flow_rate(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'heating_supply_air_flow_rate'] = 1.01
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            1.01,
            epjson_output['Sizing:System']['Heat Pump 1 Sizing System']['heating_supply_air_flow_rate'])
        self.assertEqual(
            1.01,
            epjson_output['AirLoopHVAC:UnitaryHeatPump:AirToAir']['Heat Pump 1 Heat Pump'][
                'heating_supply_air_flow_rate'])
        self.assertEqual(
            1.01,
            epjson_output['Coil:Heating:DX:SingleSpeed']['Heat Pump 1 Cooling Coil'][
                'rated_air_flow_rate'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:no_load_supplY_air_flow_rate")
    def test_no_load_supply_air_flow_rate(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'no_load_supply_air_flow_rate'] = 1.01
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            1.01,
            epjson_output['AirLoopHVAC:UnitaryHeatPump:AirToAir']['Heat Pump 1 Heat Pump'][
                'no_load_supply_air_flow_rate'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:"
                                              "supply_fan_operating_mode_schedule_name")
    def test_supply_fan_operating_mode_schedule_name(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'supply_fan_operating_mode_schedule_name'] = 'OCCUPY-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['AirLoopHVAC:UnitaryHeatPump:AirToAir']['Heat Pump 1 Heat Pump'][
                'supply_air_fan_operating_mode_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:"
                                              "supply_fan_placement_blow_through")
    def test_supply_fan_placement_blow_through(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'supply_fan_placement_blow_through'] = 'BlowThrough'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'BlowThrough',
            epjson_output['AirLoopHVAC:UnitaryHeatPump:AirToAir']['Heat Pump 1 Heat Pump'][
                'fan_placement'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:"
                                              "supply_fan_placement_draw_through")
    def test_supply_fan_placement_draw_through(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'supply_fan_placement'] = 'DrawThrough'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'DrawThrough',
            epjson_output['AirLoopHVAC:UnitaryHeatPump:AirToAir']['Heat Pump 1 Heat Pump'][
                'fan_placement'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:supply_fan_total_efficiency")
    def test_supply_fan_total_efficiency(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'supply_fan_total_efficiency'] = 0.65
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.65,
            epjson_output['Fan:OnOff']['Heat Pump 1 Supply Fan']['fan_total_efficiency'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:supply_fan_delta_pressure")
    def test_supply_fan_delta_pressure(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'supply_fan_delta_pressure'] = 500
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            500,
            epjson_output['Fan:OnOff']['Heat Pump 1 Supply Fan']['pressure_rise'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:supply_fan_motor_efficiency")
    def test_supply_fan_motor_efficiency(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'supply_fan_motor_efficiency'] = 0.8
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.8,
            epjson_output['Fan:OnOff']['Heat Pump 1 Supply Fan']['motor_efficiency'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:"
                                              "supply_fan_motor_in_air_stream_fraction")
    def test_supply_fan_motor_in_air_stream_fraction(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'supply_fan_motor_in_air_stream_fraction'] = 0.9
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.9,
            epjson_output['Fan:OnOff']['Heat Pump 1 Supply Fan']['motor_in_airstream_fraction'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:"
                                              "cooling_coil_availability_schedule_name")
    def test_cooling_coil_availability_schedule_name(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'cooling_coil_availability_schedule_name'] = 'OCCUPY-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['Coil:Cooling:DX:SingleSpeed']['Heat Pump 1 Cooling Coil']['availability_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:"
                                              "cooling_design_supply_air_temperature")
    def test_cooling_design_supply_air_temperature(self):
        # todo_eo: why is the SetpointManager:SingleZone:Cooling object not affected by this input
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'cooling_design_supply_air_temperature'] = 12.9
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            12.9,
            epjson_output['Sizing:System']['Heat Pump 1 Sizing System'][
                'central_cooling_design_supply_air_temperature'])
        self.assertEqual(
            12.9,
            epjson_output['SetpointManager:SingleZone:Cooling']['Heat Pump 1 Cooling Supply Air Temp Manager'][
                'minimum_supply_air_temperature'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:"
                                              "cooling_coil_gross_rated_total_capacity")
    def test_cooling_coil_gross_rated_total_capacity(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'cooling_coil_gross_rated_total_capacity'] = 2000
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            2000,
            epjson_output['Coil:Cooling:DX:SingleSpeed']['Heat Pump 1 Cooling Coil'][
                'gross_rated_total_cooling_capacity'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:"
                                              "cooling_coil_gross_rated_sensible_heat_ratio")
    def test_cooling_coil_gross_rated_sensible_heat_ratio(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'cooling_coil_gross_rated_sensible_heat_ratio'] = 0.75
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.75,
            epjson_output['Coil:Cooling:DX:SingleSpeed']['Heat Pump 1 Cooling Coil'][
                'gross_rated_sensible_heat_ratio'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:"
                                              "cooling_coil_gross_rated_cop")
    def test_cooling_coil_gross_rated_cop(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'cooling_coil_gross_rated_cop'] = 3.1
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            3.1,
            epjson_output['Coil:Cooling:DX:SingleSpeed']['Heat Pump 1 Cooling Coil'][
                'gross_rated_cooling_cop'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:"
                                              "heat_pump_heating_coil_availability_schedule_name")
    def test_heat_pump_heating_coil_availability_schedule_name(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'heat_pump_heating_coil_availability_schedule_name'] = 'OCCUPY-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['Coil:Heating:DX:SingleSpeed']['Heat Pump 1 Heating Coil']['availability_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:"
                                              "heating_design_supply_air_temperature")
    def test_heating_design_supply_air_temperature(self):
        # todo_eo: why is the SetpointManager:SingleZone:Cooling object not affected by this input
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'heating_design_supply_air_temperature'] = 48
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            48,
            epjson_output['Sizing:System']['Heat Pump 1 Sizing System'][
                'central_heating_design_supply_air_temperature'])
        self.assertEqual(
            48,
            epjson_output['SetpointManager:SingleZone:Cooling']['Heat Pump 1 Cooling Supply Air Temp Manager'][
                'maximum_supply_air_temperature'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:"
                                              "heat_pump_heating_coil_rated_cop")
    def test_heat_pump_heating_coil_rated_cop(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'heat_pump_heating_coil_rated_cop'] = 2.9
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            2.9,
            epjson_output['Coil:Heating:DX:SingleSpeed']['Heat Pump 1 Heating Coil'][
                'gross_rated_heating_cop'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:"
                                              "heat_pump_heating_minimum_outdoor_dry_bulb_temperature")
    def test_heat_pump_heating_minimum_outdoor_dry_bulb_temperature(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'heat_pump_heating_minimum_outdoor_dry_bulb_temperature'] = -7.5
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            -7.5,
            epjson_output['Coil:Heating:DX:SingleSpeed']['Heat Pump 1 Heating Coil'][
                'minimum_outdoor_dry_bulb_temperature_for_compressor_operation'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:"
                                              "heat_pump_defrost_maximum_outdoor_dry_bulb_temperature")
    def test_heat_pump_defrost_maximum_outdoor_dry_bulb_temperature(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'heat_pump_defrost_maximum_outdoor_dry_bulb_temperature'] = 4.5
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            4.5,
            epjson_output['Coil:Heating:DX:SingleSpeed']['Heat Pump 1 Heating Coil'][
                'maximum_outdoor_dry_bulb_temperature_for_defrost_operation'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:"
                                              "heat_pump_defrost_strategy_reverse_cycle")
    def test_heat_pump_defrost_strategy_reverse_cycle(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'heat_pump_defrost_strategy'] = 'ReverseCycle'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'ReverseCycle',
            epjson_output['Coil:Heating:DX:SingleSpeed']['Heat Pump 1 Heating Coil'][
                'defrost_strategy'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:"
                                              "heat_pump_defrost_strategy_resistive")
    def test_heat_pump_defrost_strategy_resistive(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'heat_pump_defrost_strategy'] = 'Resistive'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'Resistive',
            epjson_output['Coil:Heating:DX:SingleSpeed']['Heat Pump 1 Heating Coil'][
                'defrost_strategy'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:"
                                              "heat_pump_defrost_control_timed")
    def test_heat_pump_defrost_control_timed(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'heat_pump_defrost_control'] = 'Timed'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'Timed',
            epjson_output['Coil:Heating:DX:SingleSpeed']['Heat Pump 1 Heating Coil'][
                'defrost_control'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:"
                                              "heat_pump_defrost_control_on_demand")
    def test_heat_pump_defrost_control_on_demand(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'heat_pump_defrost_control'] = 'OnDemand'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'OnDemand',
            epjson_output['Coil:Heating:DX:SingleSpeed']['Heat Pump 1 Heating Coil'][
                'defrost_control'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:"
                                              "heat_pump_defrost_time_period_fraction")
    def test_heat_pump_defrost_time_period_fraction(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'heat_pump_defrost_time_period_fraction'] = 0.06
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.06,
            epjson_output['Coil:Heating:DX:SingleSpeed']['Heat Pump 1 Heating Coil'][
                'defrost_time_period_fraction'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:"
                                              "supplemental_heating_coil_type_electric")
    def test_supplemental_heating_coil_type_electric(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'supplemental_heating_coil_type'] = 'Electric'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output['Coil:Heating:Electric'].get('Heat Pump 1 Supp Heating Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:"
                                              "supplemental_heating_coil_type_gas")
    def test_supplemental_heating_coil_type_gas(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'supplemental_heating_coil_type'] = 'Gas'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output['Coil:Heating:Fuel'].get('Heat Pump 1 Supp Heating Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:"
                                              "supplemental_heating_coil_type_hot_water")
    def test_supplemental_heating_coil_type_hot_water(self):
        self.ej.merge_epjson(
            super_dictionary=self.base_epjson,
            object_dictionary=hot_water_objects)
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'supplemental_heating_coil_type'] = 'HotWater'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output['Coil:Heating:Water'].get('Heat Pump 1 Supp Heating Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:"
                                              "supplemental_heating_coil_availability_schedule_name")
    def test_supplemental_heating_coil_availability_schedule_name(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'supplemental_heating_coil_availability_schedule_name'] = 'OCCUPY-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['Coil:Heating:Electric']['Heat Pump 1 Supp Heating Coil']['availability_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:"
                                              "supplemental_heating_coil_capacity")
    def test_supplemental_heating_coil_capacity(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'supplemental_heating_coil_capacity'] = 1000
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            1000,
            epjson_output['Coil:Heating:Electric']['Heat Pump 1 Supp Heating Coil']['nominal_capacity'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:"
                                              "supplemental_heating_coil_maximum_outdoor_dry_bulb_temperature")
    def test_supplemental_heating_coil_maximum_outdoor_dry_bulb_temperature(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'supplemental_heating_coil_maximum_outdoor_dry_bulb_temperature'] = 20
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            20,
            epjson_output['AirLoopHVAC:UnitaryHeatPump:AirToAir']['Heat Pump 1 Heat Pump'][
                'maximum_outdoor_dry_bulb_temperature_for_supplemental_heater_operation'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:"
                                              "supplemental_gas_heating_coil_efficiency")
    def test_supplemental_gas_heating_coil_efficiency(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'supplemental_heating_coil_type'] = 'Gas'
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'supplemental_gas_heating_coil_efficiency'] = 0.77
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.77,
            epjson_output['Coil:Heating:Fuel']['Heat Pump 1 Supp Heating Coil']['burner_efficiency'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:"
                                              "outdoor_air_flow_rates")
    def test_outdoor_air_flow_rates(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'maximum_outdoor_air_flow_rate'] = 0.66
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'minimum_outdoor_air_flow_rate'] = 0.1
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.66,
            epjson_output['Controller:OutdoorAir']['Heat Pump 1 OA Controller']['maximum_outdoor_air_flow_rate'])
        self.assertEqual(
            0.1,
            epjson_output['Controller:OutdoorAir']['Heat Pump 1 OA Controller']['minimum_outdoor_air_flow_rate'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:minimum_outdoor_air_schedule_name")
    def test_minimum_outdoor_air_schedule_name(self):
        self.ej.merge_epjson(
            super_dictionary=self.base_epjson,
            object_dictionary=schedule_objects)
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'minimum_outdoor_air_schedule_name'] = 'Always0.8'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'Always0.8',
            epjson_output['Controller:OutdoorAir']['Heat Pump 1 OA Controller'][
                'minimum_outdoor_air_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:economizer_type_no_economizer")
    def test_economizer_type_no_economizer(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'economizer_type'] = 'NoEconomizer'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'NoEconomizer',
            epjson_output['Controller:OutdoorAir']['Heat Pump 1 OA Controller']['economizer_control_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:economizer_type_fixed_dry_bulb")
    def test_economizer_type_fixed_dry_bulb(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'economizer_type'] = 'FixedDryBulb'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'FixedDryBulb',
            epjson_output['Controller:OutdoorAir']['Heat Pump 1 OA Controller']['economizer_control_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:economizer_type_fixed_enthalpy")
    def test_economizer_type_fixed_enthalpy(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'economizer_type'] = 'FixedEnthalpy'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'FixedEnthalpy',
            epjson_output['Controller:OutdoorAir']['Heat Pump 1 OA Controller']['economizer_control_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:economizer_type_differential_dry_bulb")
    def test_economizer_type_differential_dry_bulb(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'economizer_type'] = 'DifferentialDryBulb'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'DifferentialDryBulb',
            epjson_output['Controller:OutdoorAir']['Heat Pump 1 OA Controller']['economizer_control_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:economizer_type_differential_enthalpy")
    def test_economizer_type_differential_enthalpy(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'economizer_type'] = 'DifferentialEnthalpy'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'DifferentialEnthalpy',
            epjson_output['Controller:OutdoorAir']['Heat Pump 1 OA Controller']['economizer_control_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:"
                                              "economizer_type_fixed_dew_point_and_dry_bulb")
    def test_economizer_type_fixed_dew_point_and_dry_bulb(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'economizer_type'] = 'FixedDewPointAndDryBulb'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'FixedDewPointAndDryBulb',
            epjson_output['Controller:OutdoorAir']['Heat Pump 1 OA Controller']['economizer_control_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:"
                                              "electronic_enthalpy")
    def test_economizer_type_electronic_enthalpy(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'economizer_type'] = 'ElectronicEnthalpy'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'ElectronicEnthalpy',
            epjson_output['Controller:OutdoorAir']['Heat Pump 1 OA Controller']['economizer_control_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:economizer_type_"
                                              "differential_dry_bulb_and_enthalpy")
    def test_economizer_type_differential_dry_bulb_and_enthalpy(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir'][':System:UnitaryHeatPump:AirToAir'][
            'economizer_type'] = 'DifferentialDryBulbAndEnthalpy'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'DifferentialDryBulbAndEnthalpy',
            epjson_output['Controller:OutdoorAir']['Heat Pump 1 OA Controller']['economizer_control_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:"
                                              "supplemental_gas_heating_coil_parasitic_electric_load")
    def test_supplemental_gas_heating_coil_parasitic_electric_load(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'supplemental_heating_coil_type'] = 'Gas'
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'supplemental_gas_heating_coil_parasitic_electric_load'] = 1
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            1,
            epjson_output['Coil:Heating:Fuel']['Heat Pump 1 Supp Heating Coil']['parasitic_electric_load'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:night_cycle_control_stay_off")
    def test_night_cycle_control_stay_off(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'night_cycle_control'] = 'StayOff'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'StayOff',
            epjson_output['AvailabilityManager:NightCycle']['Heat Pump 1 Availability']['control_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:night_cycle_control_cycle_on_any")
    def test_night_cycle_control_cycle_on_any(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'night_cycle_control'] = 'CycleOnAny'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'CycleOnAny',
            epjson_output['AvailabilityManager:NightCycle']['Heat Pump 1 Availability']['control_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:"
                                              "night_cycle_control_cycle_on_control_zone")
    def test_night_cycle_control_cycle_on_control_zone(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'night_cycle_control'] = 'CycleOnControlZone'
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'night_cycle_control_zone_name'] = 'SPACE1-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'CycleOnControlZone',
            epjson_output['AvailabilityManager:NightCycle']['Heat Pump 1 Availability']['control_type'])
        self.assertEqual(
            'SPACE1-1',
            epjson_output['AvailabilityManager:NightCycle']['Heat Pump 1 Availability'][
                'control_zone_or_zone_list_name'])
        return
