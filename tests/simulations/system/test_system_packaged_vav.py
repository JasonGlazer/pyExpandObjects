from pathlib import Path

from tests.simulations import BaseSimulationTest
from src.epjson_handler import EPJSON

test_dir = Path(__file__).parent.parent.parent

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

class TestSimulationsSystemPackagedVAV(BaseSimulationTest):
    def setUp(self):
        self.ej = EPJSON()
        base_idf_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles', 'HVACTemplate-5ZonePackagedVAV.idf')
        base_copy_file_path = self._copy_to_test_directory(base_idf_file_path)
        # read in base file, then edit inputs for alternate tests
        self.base_epjson = self.get_epjson_object_from_idf_file(base_copy_file_path)
        self.base_epjson.pop('Output:Variable')
        return

    def teardown(self):
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:system_availability_schedule_name")
    def test_system_availability_schedule_name(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['system_availability_schedule_name'] = 'OCCUPY-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['Fan:VariableVolume']['DXVAV Sys 1 Supply Fan']['availability_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:supply_fan_maximum_flow_rate")
    def test_supply_fan_maximum_flow_rate(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['supply_fan_maximum_flow_rate'] = 2
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            2.0,
            epjson_output['Sizing:System']['DXVAV Sys 1 Sizing System']['cooling_supply_air_flow_rate'])
        self.assertEqual(
            'Flow/System',
            epjson_output['Sizing:System']['DXVAV Sys 1 Sizing System']['cooling_supply_air_flow_rate_method'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:supply_fan_minimum_flow_rate")
    def test_supply_fan_minimum_flow_rate(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['supply_fan_minimum_flow_rate'] = 0.25
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.25,
            epjson_output['Fan:VariableVolume']['DXVAV Sys 1 Supply Fan']['fan_power_minimum_air_flow_rate'])
        self.assertEqual(
            'FixedFlowRate',
            epjson_output['Fan:VariableVolume']['DXVAV Sys 1 Supply Fan']['fan_power_minimum_flow_rate_input_method'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:supply_fan_placement"
                                              "_draw_through_cooling_none_heating_none")
    def test_supply_fan_placement_draw_through_cooling_none_heating_none(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['supply_fan_placement'] = 'DrawThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['cooling_coil_setpoint_reset_type'] = \
            'None'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['heating_coil_setpoint_reset_type'] = \
            'None'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['supply_fan_placement'] = 'DrawThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['cooling_coil_setpoint_reset_type'] = \
            'None'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['heating_coil_setpoint_reset_type'] = \
            'None'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:supply_fan_placement"
                                              "_draw_through_cooling_none_heating_outdoor_air_temperature_reset")
    def test_supply_fan_placement_draw_through_cooling_none_heating_outdoor_air_temperature_reset(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['supply_fan_placement'] = 'DrawThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['cooling_coil_setpoint_reset_type'] = \
            'None'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['heating_coil_setpoint_reset_type'] = \
            'OutdoorAirTemperatureReset'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['supply_fan_placement'] = 'DrawThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['cooling_coil_setpoint_reset_type'] = \
            'None'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['heating_coil_setpoint_reset_type'] = \
            'OutdoorAirTemperatureReset'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:supply_fan_placement"
                                              "_blow_through_cooling_none_heating_none")
    def test_supply_fan_placement_blow_through_cooling_none_heating_none(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['supply_fan_placement'] = 'BlowThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['cooling_coil_setpoint_reset_type'] = \
            'None'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['heating_coil_setpoint_reset_type'] = \
            'None'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['supply_fan_placement'] = 'BlowThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['cooling_coil_setpoint_reset_type'] = \
            'None'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['heating_coil_setpoint_reset_type'] = \
            'None'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:supply_fan_placement"
                                              "_blow_through_cooling_none_heating_outdoor_air_temperature_reset")
    def test_supply_fan_placement_blow_through_cooling_none_heating_outdoor_air_temperature_reset(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['supply_fan_placement'] = 'BlowThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['cooling_coil_setpoint_reset_type'] = \
            'None'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['heating_coil_setpoint_reset_type'] = \
            'OutdoorAirTemperatureReset'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['supply_fan_placement'] = 'BlowThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['cooling_coil_setpoint_reset_type'] = \
            'None'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['heating_coil_setpoint_reset_type'] = \
            'OutdoorAirTemperatureReset'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:supply_fan_placement_"
                                              "draw_through_cooling_warmest_heating_none")
    def test_supply_fan_placement_draw_through_cooling_warmest_heating_none(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['supply_fan_placement'] = 'DrawThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['cooling_coil_setpoint_reset_type'] = \
            'Warmest'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['heating_coil_setpoint_reset_type'] = \
            'None'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['supply_fan_placement'] = 'DrawThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['cooling_coil_setpoint_reset_type'] = \
            'Warmest'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['heating_coil_setpoint_reset_type'] = \
            'None'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:supply_fan_placement_"
                                              "draw_through_cooling_warmest_heating_outdoor_air_temperature_reset")
    def test_supply_fan_placement_draw_through_cooling_warmest_heating_outdoor_air_temperature_reset(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['supply_fan_placement'] = 'DrawThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['cooling_coil_setpoint_reset_type'] = \
            'OutdoorAirTemperatureReset'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['heating_coil_setpoint_reset_type'] = \
            'None'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['supply_fan_placement'] = 'DrawThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['cooling_coil_setpoint_reset_type'] = \
            'Warmest'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['heating_coil_setpoint_reset_type'] = \
            'OutdoorAirTemperatureReset'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:supply_fan_placement_"
                                              "blow_through_cooling_warmest_heating_none")
    def test_supply_fan_placement_blow_through_cooling_warmest_heating_none(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['supply_fan_placement'] = 'BlowThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['cooling_coil_setpoint_reset_type'] = \
            'Warmest'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['heating_coil_setpoint_reset_type'] = \
            'None'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['supply_fan_placement'] = 'BlowThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['cooling_coil_setpoint_reset_type'] = \
            'Warmest'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['heating_coil_setpoint_reset_type'] = \
            'None'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:supply_fan_placement_"
                                              "blow_through_cooling_warmest_heating_outdoor_air_temperature_reset")
    def test_supply_fan_placement_blow_through_cooling_warmest_heating_outdoor_air_temperature_reset(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['supply_fan_placement'] = 'BlowThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['cooling_coil_setpoint_reset_type'] = \
            'Warmest'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['heating_coil_setpoint_reset_type'] = \
            'OutdoorAirTemperatureReset'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['supply_fan_placement'] = 'BlowThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['cooling_coil_setpoint_reset_type'] = \
            'Warmest'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['heating_coil_setpoint_reset_type'] = \
            'OutdoorAirTemperatureReset'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:supply_fan_placement_"
                                              "draw_through_cooling_warmest_temperature_first_heating_none")
    def test_supply_fan_placement_draw_through_cooling_warmest_temperature_first_heating_none(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['supply_fan_placement'] = 'DrawThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['cooling_coil_setpoint_reset_type'] = \
            'WarmestTemperatureFirst'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['heating_coil_setpoint_reset_type'] = \
            'None'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['supply_fan_placement'] = 'DrawThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['cooling_coil_setpoint_reset_type'] = \
            'WarmestTemperatureFirst'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['heating_coil_setpoint_reset_type'] = \
            'None'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:supply_fan_placement_"
                                              "draw_through_cooling_warmest_temperature_first_"
                                              "heating_outdoor_air_temperature_reset")
    def test_supply_fan_placement_draw_through_cooling_warmest_temperature_first_heating_outdoor_air_temperature_reset(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['supply_fan_placement'] = 'DrawThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['cooling_coil_setpoint_reset_type'] = \
            'WarmestTemperatureFirst'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['heating_coil_setpoint_reset_type'] = \
            'OutdoorAirTemperatureReset'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['supply_fan_placement'] = 'DrawThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['cooling_coil_setpoint_reset_type'] = \
            'WarmestTemperatureFirst'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['heating_coil_setpoint_reset_type'] = \
            'OutdoorAirTemperatureReset'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:supply_fan_placement_"
                                              "blow_through_cooling_warmest_first_heating_none")
    def test_supply_fan_placement_blow_through_cooling_warmest_temperature_first_heating_none(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['supply_fan_placement'] = 'BlowThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['cooling_coil_setpoint_reset_type'] = \
            'WarmestTemperatureFirst'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['heating_coil_setpoint_reset_type'] = \
            'None'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['supply_fan_placement'] = 'BlowThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['cooling_coil_setpoint_reset_type'] = \
            'WarmestTemperatureFirst'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['heating_coil_setpoint_reset_type'] = \
            'None'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:supply_fan_placement_"
                                              "blow_through_cooling_warmest_first_"
                                              "heating_outdoor_air_temperature_reset")
    def test_supply_fan_placement_blow_through_cooling_warmest_temperature_first_heating_outdoor_air_temperature_reset(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['supply_fan_placement'] = 'BlowThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['cooling_coil_setpoint_reset_type'] = \
            'WarmestTemperatureFirst'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['heating_coil_setpoint_reset_type'] = \
            'OutdoorAirTemperatureReset'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['supply_fan_placement'] = 'BlowThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['cooling_coil_setpoint_reset_type'] = \
            'WarmestTemperatureFirst'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['heating_coil_setpoint_reset_type'] = \
            'OutdoorAirTemperatureReset'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:supply_fan_placement_"
                                              "draw_through_cooling_outdoor_air_temperature_reset_heating_none")
    def test_supply_fan_placement_draw_through_cooling_outdoor_air_temperature_reset_heating_none(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['supply_fan_placement'] = 'DrawThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['cooling_coil_setpoint_reset_type'] = \
            'OutdoorAirTemperatureReset'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['heating_coil_setpoint_reset_type'] = \
            'None'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['supply_fan_placement'] = 'DrawThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['cooling_coil_setpoint_reset_type'] = \
            'OutdoorAirTemperatureReset'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['heating_coil_setpoint_reset_type'] = \
            'None'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:supply_fan_placement_"
                                              "draw_through_cooling_outdoor_air_temperature_reset_"
                                              "heating_outdoor_air_temperature_reset")
    def test_supply_fan_placement_draw_through_cooling_outdoor_air_temperature_reset_heating_outdoor_air_temperature_reset(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['supply_fan_placement'] = 'DrawThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['cooling_coil_setpoint_reset_type'] = \
            'OutdoorAirTemperatureReset'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['heating_coil_setpoint_reset_type'] = \
            'OutdoorAirTemperatureReset'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['supply_fan_placement'] = 'DrawThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['cooling_coil_setpoint_reset_type'] = \
            'OutdoorAirTemperatureReset'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['heating_coil_setpoint_reset_type'] = \
            'OutdoorAirTemperatureReset'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:supply_fan_placement_"
                                              "draw_through_cooling_outdoor_air_temperature_reset_heating_none")
    def test_supply_fan_placement_blow_through_cooling_outdoor_air_temperature_reset_heating_none(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['supply_fan_placement'] = 'BlowThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['cooling_coil_setpoint_reset_type'] = \
            'OutdoorAirTemperatureReset'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['heating_coil_setpoint_reset_type'] = \
            'None'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['supply_fan_placement'] = 'BlowThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['cooling_coil_setpoint_reset_type'] = \
            'OutdoorAirTemperatureReset'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['heating_coil_setpoint_reset_type'] = \
            'None'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:supply_fan_placement_"
                                              "draw_through_cooling_outdoor_air_temperature_reset_"
                                              "heating_outdoor_air_temperature_reset")
    def test_supply_fan_placement_blow_through_cooling_outdoor_air_temperature_reset_heating_outdoor_air_temperature_reset(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['supply_fan_placement'] = 'BlowThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['cooling_coil_setpoint_reset_type'] = \
            'OutdoorAirTemperatureReset'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['heating_coil_setpoint_reset_type'] = \
            'OutdoorAirTemperatureReset'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['supply_fan_placement'] = 'BlowThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['cooling_coil_setpoint_reset_type'] = \
            'OutdoorAirTemperatureReset'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 2']['heating_coil_setpoint_reset_type'] = \
            'OutdoorAirTemperatureReset'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:supply_fan_total_efficiency")
    def test_supply_fan_total_efficiency(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['supply_fan_total_efficiency'] = 0.75
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.75,
            epjson_output['Fan:VariableVolume']['DXVAV Sys 1 Supply Fan']['fan_total_efficiency'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:supply_fan_delta_pressure")
    def test_supply_fan_delta_pressure(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['supply_fan_delta_pressure'] = 1100
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            1100,
            epjson_output['Fan:VariableVolume']['DXVAV Sys 1 Supply Fan']['pressure_rise'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:supply_fan_motor_efficiency")
    def test_supply_fan_motor_efficiency(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['supply_fan_motor_efficiency'] = 0.8
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.8,
            epjson_output['Fan:VariableVolume']['DXVAV Sys 1 Supply Fan']['motor_efficiency'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:"
                                              "supply_fan_motor_in_air_stream_fraction")
    def test_supply_fan_motor_in_air_stream_fraction(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'supply_fan_motor_in_air_stream_fraction'] = 0.8
        base_file_path = self.create_idf_file_from_epjson(
            epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.8,
            epjson_output['Fan:VariableVolume']['DXVAV Sys 1 Supply Fan']['motor_in_airstream_fraction'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:"
                                              "cooling_coil_type_two_speed_dx")
    def test_cooling_coil_type_two_speed_dx(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'cooling_coil_type'] = 'TwoSpeedDX'
        base_file_path = self.create_idf_file_from_epjson(
            epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Coil:Cooling:DX:TwoSpeed'].get('DXVAV Sys 1 Cooling Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:"
                                              "cooling_coil_type_two_speed_humid_control_dx")
    def test_cooling_coil_type_two_speed_humid_control_dx(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'cooling_coil_type'] = 'TwoSpeedHumidControlDX'
        base_file_path = self.create_idf_file_from_epjson(
            epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Coil:Cooling:DX:TwoStageWithHumidityControlMode'].get('DXVAV Sys 1 Cooling Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:"
                                              "cooling_coil_availability_schedule_name")
    def test_cooling_coil_availability_schedule_name(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'cooling_coil_availability_schedule_name'] = 'OCCUPY-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['Coil:Cooling:DX:TwoSpeed']['DXVAV Sys 1 Cooling Coil']['availability_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:"
                                              "cooling_coil_setpoint_schedule_name")
    def test_cooling_coil_setpoint_schedule_name(self):
        self.ej.merge_epjson(
            super_dictionary=self.base_epjson,
            object_dictionary=schedule_objects)
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'cooling_coil_setpoint_schedule_name'] = 'Always12.5'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'cooling_coil_setpoint_reset_type'] = 'None'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'Always12.5',
            epjson_output['SetpointManager:Scheduled']['DXVAV Sys 1 Cooling Supply Air Temp Manager']['schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:"
                                              "cooling_coil_design_setpoint")
    def test_cooling_coil_design_setpoint(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'cooling_coil_design_setpoint'] = 13
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            13,
            epjson_output['Sizing:System']['DXVAV Sys 1 Sizing System'][
                'central_cooling_design_supply_air_temperature'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:"
                                              "cooling_coil_gross_rated_total_capacity")
    def test_cooling_coil_gross_rated_total_capacity(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'cooling_coil_gross_rated_total_capacity'] = 2000
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            2000,
            epjson_output['Coil:Cooling:DX:TwoSpeed']['DXVAV Sys 1 Cooling Coil'][
                'high_speed_gross_rated_total_cooling_capacity'])
        self.assertEqual(
            2000 * 0.33,
            epjson_output['Coil:Cooling:DX:TwoSpeed']['DXVAV Sys 1 Cooling Coil'][
                'low_speed_gross_rated_total_cooling_capacity'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:"
                                              "cooling_coil_gross_rated_total_capacity_two_speed_humid_control")
    def test_cooling_coil_gross_rated_total_capacity_two_speed_humid_control(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'cooling_coil_type'] = 'TwoSpeedHumidControlDX'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'cooling_coil_gross_rated_total_capacity'] = 2000
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            1000,
            epjson_output['CoilPerformance:DX:Cooling']['DXVAV Sys 1 Standard Perf 1'][
                'gross_rated_total_cooling_capacity'])
        self.assertEqual(
            2000,
            epjson_output['CoilPerformance:DX:Cooling']['DXVAV Sys 1 Standard Perf 1+2'][
                'gross_rated_total_cooling_capacity'])
        self.assertEqual(
            1000,
            epjson_output['CoilPerformance:DX:Cooling']['DXVAV Sys 1 Dehumid Perf 1'][
                'gross_rated_total_cooling_capacity'])
        self.assertEqual(
            2000,
            epjson_output['CoilPerformance:DX:Cooling']['DXVAV Sys 1 Dehumid Perf 1+2'][
                'gross_rated_total_cooling_capacity'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:"
                                              "cooling_coil_gross_rated_sensible_heat_ratio")
    def test_cooling_coil_gross_rated_sensible_heat_ratio(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'cooling_coil_gross_rated_sensible_heat_ratio'] = 0.75
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.75,
            epjson_output['Coil:Cooling:DX:TwoSpeed']['DXVAV Sys 1 Cooling Coil'][
                'low_speed_gross_rated_sensible_heat_ratio'])
        self.assertEqual(
            0.75,
            epjson_output['Coil:Cooling:DX:TwoSpeed']['DXVAV Sys 1 Cooling Coil'][
                'high_speed_rated_sensible_heat_ratio'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:"
                                              "cooling_coil_gross_rated_sensible_heat_ratio")
    def test_cooling_coil_gross_rated_sensible_heat_ratio_two_speed_humid_control(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'cooling_coil_type'] = 'TwoSpeedHumidControlDX'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'cooling_coil_gross_rated_sensible_heat_ratio'] = 0.75
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.75,
            epjson_output['CoilPerformance:DX:Cooling']['DXVAV Sys 1 Standard Perf 1'][
                'gross_rated_sensible_heat_ratio'])
        self.assertEqual(
            0.75,
            epjson_output['CoilPerformance:DX:Cooling']['DXVAV Sys 1 Standard Perf 1+2'][
                'gross_rated_sensible_heat_ratio'])
        self.assertEqual(
            0.75 * 0.9,
            epjson_output['CoilPerformance:DX:Cooling']['DXVAV Sys 1 Dehumid Perf 1'][
                'gross_rated_sensible_heat_ratio'])
        self.assertEqual(
            0.75 * 0.9,
            epjson_output['CoilPerformance:DX:Cooling']['DXVAV Sys 1 Dehumid Perf 1+2'][
                'gross_rated_sensible_heat_ratio'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:"
                                              "cooling_coil_gross_rated_cop")
    def test_cooling_coil_gross_rated_cop(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'cooling_coil_gross_rated_cop'] = 3.1
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            3.1,
            epjson_output['Coil:Cooling:DX:TwoSpeed']['DXVAV Sys 1 Cooling Coil'][
                'high_speed_gross_rated_cooling_cop'])
        self.assertEqual(
            3.1 * 1.5,
            epjson_output['Coil:Cooling:DX:TwoSpeed']['DXVAV Sys 1 Cooling Coil'][
                'low_speed_gross_rated_cooling_cop'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:"
                                              "cooling_coil_gross_rated_cop")
    def test_cooling_coil_gross_rated_cop_two_speed_humid_control(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'cooling_coil_type'] = 'TwoSpeedHumidControlDX'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'cooling_coil_gross_rated_cop'] = 3.1
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            3.1,
            epjson_output['CoilPerformance:DX:Cooling']['DXVAV Sys 1 Standard Perf 1'][
                'gross_rated_cooling_cop'])
        self.assertEqual(
            3.1,
            epjson_output['CoilPerformance:DX:Cooling']['DXVAV Sys 1 Standard Perf 1+2'][
                'gross_rated_cooling_cop'])
        self.assertEqual(
            3.1 * 0.9,
            epjson_output['CoilPerformance:DX:Cooling']['DXVAV Sys 1 Dehumid Perf 1'][
                'gross_rated_cooling_cop'])
        self.assertEqual(
            3.1 * 0.9,
            epjson_output['CoilPerformance:DX:Cooling']['DXVAV Sys 1 Dehumid Perf 1+2'][
                'gross_rated_cooling_cop'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:heating_coil_type_none")
    def test_heating_coil_type_none(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'heating_coil_type'] = 'None'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNone(
            epjson_output['Coil:Heating:Fuel'].get('DXVAV Sys 1 Heating Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:heating_coil_type_hot_water")
    def test_heating_coil_type_hot_water(self):
        self.ej.merge_epjson(
            super_dictionary=self.base_epjson,
            object_dictionary=hot_water_objects)
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'heating_coil_type'] = 'HotWater'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Coil:Heating:Water'].get('DXVAV Sys 1 Heating Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:heating_coil_type_electric")
    def test_heating_coil_type_electric(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'heating_coil_type'] = 'Electric'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Coil:Heating:Electric'].get('DXVAV Sys 1 Heating Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:heating_coil_type_gas")
    def test_heating_coil_type_gas(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'heating_coil_type'] = 'Gas'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Coil:Heating:Fuel'].get('DXVAV Sys 1 Heating Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:"
                                              "heating_coil_availability_schedule_name")
    def test_heating_coil_availability_schedule_name(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'heating_coil_availability_schedule_name'] = 'OCCUPY-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['Coil:Heating:Fuel']['DXVAV Sys 1 Heating Coil']['availability_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:"
                                              "heating_coil_setpoint_schedule_name")
    def test_heating_coil_setpoint_schedule_name(self):
        self.ej.merge_epjson(
            super_dictionary=self.base_epjson,
            object_dictionary=schedule_objects)
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'heating_coil_setpoint_schedule_name'] = 'Always6.8'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'heating_coil_setpoint_reset_type'] = 'None'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'Always6.8',
            epjson_output['SetpointManager:Scheduled']['DXVAV Sys 1 Heating Supply Air Temp Manager']['schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:"
                                              "heating_coil_design_setpoint")
    def test_heating_coil_design_setpoint(self):
        # todo_eo: Warning issued in legacy which does not appear to be correct.
        #   ** Warning ** Output:PreprocessorMessage="ExpandObjects" has the following Warning conditions:
        #   **   ~~~   ** Warning:  In HVACTemplate:System:PackagedVAV "DXVAV Sys 1" the Heating Coil
        #   **   ~~~   ** Design Setpoint is greater than the Cooling Coil Design Setpoint. This may
        #   **   ~~~   ** cause the heating coil and cooling coil to operate simultaneously. Check
        #   **   ~~~   ** results carefully and adjust controls if needed.
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'heating_coil_setpoint_reset_type'] = 'None'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'heating_coil_design_setpoint'] = 9.0
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'HVACTemplate-Always9.0',
            epjson_output['SetpointManager:Scheduled']['DXVAV Sys 1 Heating Supply Air Temp Manager']['schedule_name'])
        self.assertEqual(
            9.0,
            epjson_output['Sizing:System']['DXVAV Sys 1 Sizing System'][
                'central_heating_design_supply_air_temperature'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:"
                                              "heating_coil_capacity")
    def test_heating_coil_capacity(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'heating_coil_capacity'] = 1000
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            1000,
            epjson_output['Coil:Heating:Fuel']['DXVAV Sys 1 Heating Coil']['nominal_capacity'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:"
                                              "gas_heating_coil_efficiency")
    def test_gas_heating_coil_efficiency(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'gas_heating_coil_efficiency'] = 0.77
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.77,
            epjson_output['Coil:Heating:Fuel']['DXVAV Sys 1 Heating Coil']['burner_efficiency'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:"
                                              "gas_heating_coil_parasitic_electric_load")
    def test_gas_heating_coil_parasitic_electric_load(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'gas_heating_coil_parasitic_electric_load'] = 1
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            1,
            epjson_output['Coil:Heating:Fuel']['DXVAV Sys 1 Heating Coil']['parasitic_electric_load'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:"
                                              "outdoor_air_flow_rates")
    def test_outdoor_air_flow_rates(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'supply_fan_placement'] = 'BlowThrough'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'maximum_outdoor_air_flow_rate'] = 0.66
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'minimum_outdoor_air_flow_rate'] = 0.1
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.66,
            epjson_output['Controller:OutdoorAir']['DXVAV Sys 1 OA Controller']['maximum_outdoor_air_flow_rate'])
        self.assertEqual(
            0.1,
            epjson_output['Controller:OutdoorAir']['DXVAV Sys 1 OA Controller']['minimum_outdoor_air_flow_rate'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:"
                                              "minimum_outdoor_air_control_type_proportional_minimum")
    def test_minimum_outdoor_air_control_type_proportional_minimum(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'minimum_outdoor_air_control_type'] = 'ProportionalMinimum'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'ProportionalMimimum',
            epjson_output['Controller:OutdoorAir']['DXVAV Sys 1 OA Controller']['minimum_limit_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:"
                                              "minimum_outdoor_air_control_type_fixed_minimum")
    def test_minimum_outdoor_air_control_type_fixed_minimum(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'minimum_outdoor_air_control_type'] = 'FixedMinimum'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'FixedMimimum',
            epjson_output['Controller:OutdoorAir']['DXVAV Sys 1 OA Controller']['minimum_limit_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:minimum_outdoor_air_schedule_name")
    def test_minimum_outdoor_air_schedule_name(self):
        self.ej.merge_epjson(
            super_dictionary=self.base_epjson,
            object_dictionary=schedule_objects)
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'minimum_outdoor_air_schedule_name'] = 'Always0.8'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'Always0.8',
            epjson_output['Controller:OutdoorAir']['DXVAV Sys 1 OA Controller']['minimum_outdoor_air_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:economizer_type_no_economizer")
    def test_economizer_type_no_economizer(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'economizer_type'] = 'NoEconomizer'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'NoEconomizer',
            epjson_output['Controller:OutdoorAir']['DXVAV Sys 1 OA Controller']['economizer_control_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:economizer_type_fixed_dry_bulb")
    def test_economizer_type_fixed_dry_bulb(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'economizer_type'] = 'FixedDryBulb'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'FixedDryBulb',
            epjson_output['Controller:OutdoorAir']['DXVAV Sys 1 OA Controller']['economizer_control_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:economizer_type_fixed_enthalpy")
    def test_economizer_type_fixed_enthalpy(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'economizer_type'] = 'FixedEnthalpy'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'FixedEnthalpy',
            epjson_output['Controller:OutdoorAir']['DXVAV Sys 1 OA Controller']['economizer_control_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:economizer_type_differential_dry_bulb")
    def test_economizer_type_differential_dry_bulb(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'economizer_type'] = 'DifferentialDryBulb'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'DifferentialDryBulb',
            epjson_output['Controller:OutdoorAir']['DXVAV Sys 1 OA Controller']['economizer_control_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:economizer_type_differential_enthalpy")
    def test_economizer_type_differential_enthalpy(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'economizer_type'] = 'DifferentialEnthalpy'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'DifferentialEnthalpy',
            epjson_output['Controller:OutdoorAir']['DXVAV Sys 1 OA Controller']['economizer_control_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:"
                                              "economizer_type_fixed_dew_point_and_dry_bulb")
    def test_economizer_type_fixed_dew_point_and_dry_bulb(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'economizer_type'] = 'FixedDewPointAndDryBulb'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'FixedDewPointAndDryBulb',
            epjson_output['Controller:OutdoorAir']['DXVAV Sys 1 OA Controller']['economizer_control_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:"
                                              "electronic_enthalpy")
    def test_economizer_type_electronic_enthalpy(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'economizer_type'] = 'ElectronicEnthalpy'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'ElectronicEnthalpy',
            epjson_output['Controller:OutdoorAir']['DXVAV Sys 1 OA Controller']['economizer_control_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:economizer_type_"
                                              "differential_dry_bulb_and_enthalpy")
    def test_economizer_type_differential_dry_bulb_and_enthalpy(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'economizer_type'] = 'DifferentialDryBulbAndEnthalpy'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'DifferentialDryBulbAndEnthalpy',
            epjson_output['Controller:OutdoorAir']['DXVAV Sys 1 OA Controller']['economizer_control_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:economizer_lockout_no_lockout")
    def test_economizer_lockout_no_lockout(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'economizer_lockout'] = 'NoLockout'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'NoLockout',
            epjson_output['Controller:OutdoorAir']['DXVAV Sys 1 OA Controller']['lockout_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:economizer_lockout_lockout_with_heating")
    def test_economizer_lockout_lockout_with_heating(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'economizer_lockout'] = 'LockoutWithHeating'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'LockoutWithHeating',
            epjson_output['Controller:OutdoorAir']['DXVAV Sys 1 OA Controller']['lockout_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:"
                                              "economizer_lockout_lockout_with_compressor")
    def test_economizer_lockout_lockout_with_compressor(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'economizer_lockout'] = 'LockoutWithCompressor'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'LockoutWithCompressor',
            epjson_output['Controller:OutdoorAir']['DXVAV Sys 1 OA Controller']['lockout_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:economizer_temperature_limits")
    def test_economizer_temperature_limits(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'economizer_type'] = 'FixedDryBulb'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'economizer_maximum_limit_dry_bulb_temperature'] = 18
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'economizer_minimum_limit_dry_bulb_temperature'] = 5
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            18,
            epjson_output['Controller:OutdoorAir']['DXVAV Sys 1 OA Controller'][
                'economizer_maximum_limit_dry_bulb_temperature'])
        self.assertEqual(
            5,
            epjson_output['Controller:OutdoorAir']['DXVAV Sys 1 OA Controller'][
                'economizer_minimum_limit_dry_bulb_temperature'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:economizer_maximum_limit_enthalpy")
    def test_economizer_maximum_limit_enthalpy(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'economizer_type'] = 'FixedEnthalpy'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'economizer_maximum_limit_enthalpy'] = 100
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            100,
            epjson_output['Controller:OutdoorAir']['DXVAV Sys 1 OA Controller'][
                'economizer_maximum_limit_enthalpy'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:"
                                              "economizer_maximum_limit_dewpoint_temperature")
    def test_economizer_maximum_limit_dewpoint_temperature(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'economizer_type'] = 'FixedDewPointAndDryBulb'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'economizer_maximum_limit_dewpoint_temperature'] = 7.1
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            7.1,
            epjson_output['Controller:OutdoorAir']['DXVAV Sys 1 OA Controller'][
                'economizer_maximum_limit_dewpoint_temperature'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:supply_plenum_name")
    def test_supply_plenum_name(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'].pop('return_plenum_name')
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'supply_plenum_name'] = 'PLENUM-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'PLENUM-1',
            epjson_output['AirLoopHVAC:SupplyPlenum']['DXVAV Sys 1 Supply Plenum']['zone_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:return_plenum_name")
    def test_return_plenum_name(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'return_plenum_name'] = 'PLENUM-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'PLENUM-1',
            epjson_output['AirLoopHVAC:ReturnPlenum']['DXVAV Sys 1 Return Plenum']['zone_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:"
                                              "supply_fan_part_load_power_coefficients_inlet_vane_dampers")
    def test_supply_fan_part_load_power_coefficients_inlet_vane_dampers(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'supply_fan_part_load_power_coefficients'] = 'InletVaneDampers'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.35071223,
            epjson_output['Fan:VariableVolume']['DXVAV Sys 1 Supply Fan']['fan_power_coefficient_1'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:"
                                              "supply_fan_part_load_power_coefficients_outlet_dampers")
    def test_supply_fan_part_load_power_coefficients_outlet_dampers(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'supply_fan_part_load_power_coefficients'] = 'OutletDampers'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.37073425,
            epjson_output['Fan:VariableVolume']['DXVAV Sys 1 Supply Fan']['fan_power_coefficient_1'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:"
                                              "supply_fan_part_load_power_coefficients_variable_speed_motor")
    def test_supply_fan_part_load_power_coefficients_variable_speed_motor(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'supply_fan_part_load_power_coefficients'] = 'VariableSpeedMotor'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.0015302446,
            epjson_output['Fan:VariableVolume']['DXVAV Sys 1 Supply Fan']['fan_power_coefficient_1'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:"
                                              "supply_fan_part_load_power_coefficients_ASHRAE901_2004_appendix_g")
    def test_supply_fan_part_load_power_coefficients_ASHRAE901_2004_appendix_g(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'supply_fan_part_load_power_coefficients'] = 'ASHRAE90.1-2004AppendixG'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.0013,
            epjson_output['Fan:VariableVolume']['DXVAV Sys 1 Supply Fan']['fan_power_coefficient_1'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:"
                                              "supply_fan_part_load_power_coefficients_"
                                              "variable_speed_motor_pressure_resst")
    def test_supply_fan_part_load_power_coefficients_variable_speed_motor_pressure_reset(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'supply_fan_part_load_power_coefficients'] = 'VariableSpeedMotorPressureReset'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.0013,
            epjson_output['Fan:VariableVolume']['DXVAV Sys 1 Supply Fan']['fan_power_coefficient_1'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:night_cycle_control_stay_off")
    def test_night_cycle_control_stay_off(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'night_cycle_control'] = 'StayOff'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'StayOff',
            epjson_output['AvailabilityManager:NightCycle']['DXVAV Sys 1 Availability']['control_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:night_cycle_control_cycle_on_any")
    def test_night_cycle_control_cycle_on_any(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'night_cycle_control'] = 'CycleOnAny'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'CycleOnAny',
            epjson_output['AvailabilityManager:NightCycle']['DXVAV Sys 1 Availability']['control_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:night_cycle_control_cycle_on_control_zone")
    def test_night_cycle_control_cycle_on_control_zone(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'night_cycle_control'] = 'CycleOnControlZone'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'night_cycle_control_zone_name'] = 'SPACE1-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'CycleOnControlZone',
            epjson_output['AvailabilityManager:NightCycle']['DXVAV Sys 1 Availability']['control_type'])
        self.assertEqual(
            'SPACE1-1',
            epjson_output['AvailabilityManager:NightCycle']['DXVAV Sys 1 Availability']['control_zone_or_zone_list_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:night_cycle_control_"
                                              "cycle_on_any_zone_fans_only")
    def test_night_cycle_control_cycle_on_any_zone_fans_only(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'night_cycle_control'] = 'CycleOnAnyZoneFansOnly'
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'night_cycle_control_zone_name'] = 'SPACE1-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'CycleOnAnyZoneFansOnly',
            epjson_output['AvailabilityManager:NightCycle']['DXVAV Sys 1 Availability']['control_type'])
        self.assertEqual(
            'SPACE1-1',
            epjson_output['AvailabilityManager:NightCycle']['DXVAV Sys 1 Availability'][
                'control_zone_or_zone_list_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:heat_recovery_sensible")
    def test_heat_recovery_sensible(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'heat_recovery_type'] = 'Sensible'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output.get('HeatExchanger:AirToAir:SensibleAndLatent'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:heat_recovery_enthalpy")
    def test_heat_recovery_enthalpy(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1'][
            'heat_recovery_type'] = 'Enthalpy'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output.get('HeatExchanger:AirToAir:SensibleAndLatent'))
        return
