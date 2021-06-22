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
        # todo_eo: legacy does not seem to update Fan:ConstantVolume or AirLoopHVAC
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

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:supply_fan_placement_draw_through_cooling_warmest")
    def test_supply_fan_placement_draw_through_cooling_warmest(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'supply_fan_placement'] = 'DrawThrough'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'cooling_coil_setpoint_control_type'] = 'Warmest'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:supply_fan_placement_blow_through_cooling_warmest")
    def test_supply_fan_placement_blow_through_cooling_warmest(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'supply_fan_placement'] = 'BlowThrough'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'cooling_coil_setpoint_control_type'] = 'Warmest'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        # todo_eo: odd warning coming from legacy but not current program even though they appear to be the same.
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:supply_fan_placement_draw_through_cooling_fixed_setpoint")
    def test_supply_fan_placement_draw_through_cooling_fixed_setpoint(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'supply_fan_placement'] = 'DrawThrough'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'cooling_coil_setpoint_control_type'] = 'FixedSetpoint'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:supply_fan_placement_draw_through_cooling_fixed_setpoint")
    def test_supply_fan_placement_blow_through_cooling_fixed_setpoint(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'supply_fan_placement'] = 'DrawThrough'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'cooling_coil_setpoint_control_type'] = 'FixedSetpoint'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:supply_fan_placement_draw_through_cooling_scheduled")
    def test_supply_fan_placement_draw_through_cooling_scheduled(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'supply_fan_placement'] = 'DrawThrough'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'cooling_coil_setpoint_control_type'] = 'Scheduled'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:supply_fan_placement_blow_through_cooling_scheduled")
    def test_supply_fan_placement_blow_through_cooling_scheduled(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'supply_fan_placement'] = 'BlowThrough'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'cooling_coil_setpoint_control_type'] = 'Scheduled'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        # todo_eo: odd warning coming from legacy but not current program even though they appear to be the same.
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:supply_fan_placement_draw_"
                                              "through_cooling_outdoor_air_temperature_reset")
    def test_supply_fan_placement_draw_through_cooling_outdoor_air_temperature_reset(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'supply_fan_placement'] = 'DrawThrough'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'cooling_coil_setpoint_control_type'] = 'OutdoorAirTemperatureReset'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:supply_fan_placement_blow_"
                                              "through_cooling_outdoor_air_temperature_reset")
    def test_supply_fan_placement_blow_through_cooling_outdoor_air_temperature_reset(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'supply_fan_placement'] = 'BlowThrough'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'cooling_coil_setpoint_control_type'] = 'OutdoorAirTemperatureReset'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        # todo_eo: odd warning coming from legacy but not current program even though they appear to be the same.
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:supply_fan_placement_draw_"
                                              "through_cooling_control_zone")
    def test_supply_fan_placement_draw_through_cooling_control_zone(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'supply_fan_placement'] = 'DrawThrough'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'cooling_coil_setpoint_control_type'] = 'ControlZone'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'cooling_coil_control_zone_name'] = 'SPACE1-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:supply_fan_placement_blow_"
                                              "through_cooling_control_zone")
    def test_supply_fan_placement_blow_through_cooling_control_zone(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'supply_fan_placement'] = 'BlowThrough'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'cooling_coil_setpoint_control_type'] = 'ControlZone'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'cooling_coil_control_zone_name'] = 'SPACE1-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:supply_fan_placement_blow_"
                                              "through_cooling_control_zone_no_heating")
    def test_supply_fan_placement_blow_through_cooling_control_zone_no_heating(self):
        # todo_eo: Legacy fails with this option
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'supply_fan_placement'] = 'BlowThrough'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'cooling_coil_setpoint_control_type'] = 'ControlZone'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'cooling_coil_control_zone_name'] = 'SPACE1-1'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'heating_coil_type'] = 'None'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:supply_fan_placement_draw_"
                                              "through_cooling_control_zone_no_heating")
    def test_supply_fan_placement_draw_through_cooling_control_zone_no_heating(self):
        # todo_eo: Legacy fails with this option.  Legacy will alter multiple systems if one is set to no heating coil
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'supply_fan_placement'] = 'DrawThrough'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'cooling_coil_setpoint_control_type'] = 'ControlZone'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'cooling_coil_control_zone_name'] = 'SPACE1-1'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'heating_coil_type'] = 'None'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'].pop('preheat_coil_design_setpoint')
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:supply_fan_placement_draw_through"
                                              "_heating_outdoor_air_temperature_reset")
    def test_supply_fan_placement_draw_through_heating_control_outdoor_air_temperature_reset(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'supply_fan_placement'] = 'DrawThrough'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'heating_coil_setpoint_control_type'] = 'OutdoorAirTemperatureReset'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:supply_fan_placement_blow_through"
                                              "_heating_outdoor_air_temperature_reset")
    def test_supply_fan_placement_blow_through_heating_control_outdoor_air_temperature_reset(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'supply_fan_placement'] = 'BlowThrough'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'heating_coil_setpoint_control_type'] = 'OutdoorAirTemperatureReset'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    def test_supply_fan_placement_draw_through_heating_control_fixed_setpoint(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'supply_fan_placement'] = 'DrawThrough'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'heating_coil_setpoint_control_type'] = 'FixedSetpoint'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    def test_supply_fan_placement_blow_through_heating_control_fixed_setpoint(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'supply_fan_placement'] = 'BlowThrough'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'heating_coil_setpoint_control_type'] = 'FixedSetpoint'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        # todo_eo: odd warning coming from legacy but not current program even though they appear to be the same.
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:supply_fan_placement_draw_through_heating_scheduled")
    def test_supply_fan_placement_draw_through_heating_scheduled(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'supply_fan_placement'] = 'DrawThrough'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'heating_coil_setpoint_control_type'] = 'Scheduled'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:supply_fan_placement_blow_through_heating_scheduled")
    def test_supply_fan_placement_blow_through_heating_scheduled(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'supply_fan_placement'] = 'BlowThrough'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'heating_coil_setpoint_control_type'] = 'Scheduled'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:supply_fan_placement_draw_through_heating_control_zone")
    def test_supply_fan_placement_draw_through_heating_control_zone(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'supply_fan_placement'] = 'DrawThrough'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'heating_coil_setpoint_control_type'] = 'ControlZone'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'heating_coil_control_zone_name'] = 'SPACE1-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:supply_fan_placement_draw_through_heating_control_zone")
    def test_supply_fan_placement_blow_through_heating_control_zone(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'supply_fan_placement'] = 'BlowThrough'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'heating_coil_setpoint_control_type'] = 'ControlZone'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'heating_coil_control_zone_name'] = 'SPACE1-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:cooling_coil_type_chilled_water")
    def test_cooling_coil_type_chilled_water(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'cooling_coil_type'] = 'ChilledWater'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'AHU 1 Spaces 1-4 Mixed Air Outlet',
            epjson_output['Coil:Cooling:Water']['AHU 1 Spaces 1-4 Cooling Coil'][
                'air_inlet_node_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:cooling_coil_type_chilled_water"
                                              "_detailed_flat_model")
    def test_cooling_coil_type_chilled_water_detailed_flat_model(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'cooling_coil_type'] = 'ChilledWaterDetailedFlatModel'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'AHU 1 Spaces 1-4 Mixed Air Outlet',
            epjson_output['Coil:Cooling:Water:DetailedGeometry']['AHU 1 Spaces 1-4 Cooling Coil'][
                'air_inlet_node_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:cooling_coil_type_chilled_water"
                                              "_heat_exchanger_assisted_chilled_water")
    def test_cooling_coil_type_chilled_water_heat_exchanger_assisted_chilled_water(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'cooling_coil_type'] = 'HeatExchangerAssistedChilledWater'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['CoilSystem:Cooling:Water:HeatExchangerAssisted'].get('AHU 1 Spaces 1-4 Heat Exchanger Assisted Cooling Coil'))
        self.assertIsNotNone(
            epjson_output['HeatExchanger:AirToAir:SensibleAndLatent'].get('AHU 1 Spaces 1-4 Cooling Coil Heat Exchanger'))
        return
    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:cooling_coil_type_chilled_water_blow_through"
                                              "_heat_exchanger_assisted_chilled_water")
    def test_cooling_coil_type_chilled_water_heat_exchanger_assisted_chilled_water_blow_through(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'supply_fan_placement'] = 'BlowThrough'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'cooling_coil_type'] = 'HeatExchangerAssistedChilledWater'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['CoilSystem:Cooling:Water:HeatExchangerAssisted'].get('AHU 1 Spaces 1-4 Heat Exchanger Assisted Cooling Coil'))
        self.assertIsNotNone(
            epjson_output['HeatExchanger:AirToAir:SensibleAndLatent'].get('AHU 1 Spaces 1-4 Cooling Coil Heat Exchanger'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:cooling_coil_availability_schedule_name")
    def test_cooling_coil_availability_schedule_name(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'cooling_coil_availability_schedule_name'] = 'OCCUPY-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['Coil:Cooling:Water']['AHU 1 Spaces 1-4 Cooling Coil']['availability_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:cooling_coil_design_setpoint_temperature")
    def test_cooling_coil_design_setpoint_temperature(self):
        # todo_eo: Zones not recieving updated temperature setpoint from SystemSupplyAirTemperature
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'cooling_coil_design_setpoint_temperature'] = 13
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            13,
            epjson_output['Sizing:System']['AHU 1 Spaces 1-4 Sizing System']['central_cooling_design_supply_air_temperature'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:cooling_coil_setpoint_schedule_name")
    def test_cooling_coil_setpoint_schedule_name(self):
        # todo_eo: legacy doesn't seem to map the value to anything
        self.ej.merge_epjson(
            super_dictionary=self.base_epjson,
            object_dictionary=schedule_objects)
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'cooling_coil_setpoint_schedule_name'] = 'Always12.5'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'cooling_coil_setpoint_control_type'] = 'FixedSetpoint'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'Always12.5',
            epjson_output['SetpointManager:Scheduled']['AHU 1 Spaces 1-4 Cooling Supply Air Temp Manager']['schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:cooling_coil_outdoor_reset_inputs")
    def test_cooling_coil_outdoor_reset_inputs(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'cooling_coil_setpoint_control_type'] = 'OutdoorAirTemperatureReset'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'cooling_coil_setpoint_at_outdoor_dry_bulb_low'] = 15.5
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'cooling_coil_reset_outdoor_dry_bulb_low'] = 15.4
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'cooling_coil_setpoint_at_outdoor_dry_bulb_high'] = 12.5
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'cooling_coil_reset_outdoor_dry_bulb_high'] = 23.2
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            23.2,
            epjson_output['SetpointManager:OutdoorAirReset']['AHU 1 Spaces 1-4 Cooling Supply Air Temp Manager']['outdoor_high_temperature'])
        self.assertEqual(
            12.5,
            epjson_output['SetpointManager:OutdoorAirReset']['AHU 1 Spaces 1-4 Cooling Supply Air Temp Manager']['setpoint_at_outdoor_high_temperature'])
        self.assertEqual(
            15.4,
            epjson_output['SetpointManager:OutdoorAirReset']['AHU 1 Spaces 1-4 Cooling Supply Air Temp Manager']['outdoor_low_temperature'])
        self.assertEqual(
            15.5,
            epjson_output['SetpointManager:OutdoorAirReset']['AHU 1 Spaces 1-4 Cooling Supply Air Temp Manager']['setpoint_at_outdoor_low_temperature'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:heating_coil_availability_schedule_name")
    def test_heating_coil_availability_schedule_name(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'heating_coil_availability_schedule_name'] = 'OCCUPY-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['Coil:Heating:Water']['AHU 1 Spaces 1-4 Heating Coil']['availability_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:heating_coil_design_setpoint_temperature")
    def test_heating_coil_design_setpoint_temperature(self):
        # todo_eo: Zones not receiving updated temperature setpoint from SystemSupplyAirTemperature
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'heating_coil_design_setpoint'] = 16
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            16,
            epjson_output['Sizing:System']['AHU 1 Spaces 1-4 Sizing System']['central_heating_design_supply_air_temperature'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:heating_coil_setpoint_schedule_name")
    def test_heating_coil_setpoint_schedule_name(self):
        # todo_eo: legacy doesn't seem to map the value to anything
        self.ej.merge_epjson(
            super_dictionary=self.base_epjson,
            object_dictionary=schedule_objects)
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'heating_coil_setpoint_schedule_name'] = 'Always15.5'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'heating_coil_setpoint_control_type'] = 'FixedSetpoint'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'Always15.5',
            epjson_output['SetpointManager:Scheduled']['AHU 1 Spaces 1-4 Heating Supply Air Temp Manager']['schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:heating_coil_outdoor_reset_inputs")
    def test_heating_coil_outdoor_reset_inputs(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'heating_coil_setpoint_control_type'] = 'OutdoorAirTemperatureReset'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'heating_coil_setpoint_at_outdoor_dry_bulb_low'] = 14.9
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'heating_coil_reset_outdoor_dry_bulb_low'] = 7.7
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'heating_coil_setpoint_at_outdoor_dry_bulb_high'] = 12.1
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'heating_coil_reset_outdoor_dry_bulb_high'] = 12.2
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            12.2,
            epjson_output['SetpointManager:OutdoorAirReset']['AHU 1 Spaces 1-4 Heating Supply Air Temp Manager']['outdoor_high_temperature'])
        self.assertEqual(
            12.1,
            epjson_output['SetpointManager:OutdoorAirReset']['AHU 1 Spaces 1-4 Heating Supply Air Temp Manager']['setpoint_at_outdoor_high_temperature'])
        self.assertEqual(
            7.7,
            epjson_output['SetpointManager:OutdoorAirReset']['AHU 1 Spaces 1-4 Heating Supply Air Temp Manager']['outdoor_low_temperature'])
        self.assertEqual(
            14.9,
            epjson_output['SetpointManager:OutdoorAirReset']['AHU 1 Spaces 1-4 Heating Supply Air Temp Manager']['setpoint_at_outdoor_low_temperature'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:heating_coil_capacity")
    def test_heating_coil_design_capacity(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'heating_coil_capacity'] = 2000
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            2000,
            epjson_output['Sizing:System']['AHU 1 Spaces 1-4 Sizing System']['heating_design_capacity'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:gas_heating_coil_inputs")
    def test_gas_heating_coil_inputs(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'heating_coil_type'] = 'Gas'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'gas_heating_coil_efficiency'] = 0.75
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'gas_heating_coil_parasitic_electric_load'] = 1
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.75,
            epjson_output['Coil:Heating:Fuel']['AHU 1 Spaces 1-4 Heating Coil']['burner_efficiency'])
        self.assertEqual(
            1,
            epjson_output['Coil:Heating:Fuel']['AHU 1 Spaces 1-4 Heating Coil']['parasitic_electric_load'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:preheat_coil_type_hot_water")
    def test_preheat_coil_type_hot_water(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'preheat_coil_type'] = 'HotWater'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        # self.assertEqual(
        #     0.75,
        #     epjson_output['Coil:Heating:Fuel']['AHU 1 Spaces 1-4 Heating Coil']['burner_efficiency'])
        # self.assertEqual(
        #     1,
        #     epjson_output['Coil:Heating:Fuel']['AHU 1 Spaces 1-4 Heating Coil']['parasitic_electric_load'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:dehumidification_control_type")
    def test_dehumidification_control_type(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'dehumidification_control_type'] = 'CoolReheat'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'dehumidification_control_zone_name'] = 'SPACE1-1'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'dehumidification_relative_humidity_setpoint'] = 62
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'TemperatureAndHumidityRatio',
            epjson_output['Controller:WaterCoil']['AHU 1 Spaces 1-4 Cooling Coil Controller']['control_variable'])
        self.assertEqual(
            'HVACTemplate-Always62.0',
            epjson_output['ZoneControl:Humidistat']['AHU 1 Spaces 1-4 Dehumidification Humidistat'][
                'dehumidifying_relative_humidity_setpoint_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:dehumidification_relative_"
                                              "humidity_setpoint_schedule_name")
    def test_dehumidification_relative_humidity_setpoint_schedule_name(self):
        # todo_eo: legacy doesn't map schedule_name value
        self.ej.merge_epjson(
            super_dictionary=self.base_epjson,
            object_dictionary=schedule_objects)
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'supply_fan_placement'] = 'DrawThrough'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'cooling_coil_setpoint_control_type'] = 'Warmest'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'dehumidification_control_type'] = 'CoolReheat'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'dehumidification_control_zone_name'] = 'SPACE1-1'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'dehumidification_relative_humidity_setpoint_schedule_name'] = 'Always62'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'TemperatureAndHumidityRatio',
            epjson_output['Controller:WaterCoil']['AHU 1 Spaces 1-4 Cooling Coil Controller']['control_variable'])
        self.assertEqual(
            'Always62',
            epjson_output['ZoneControl:Humidistat']['AHU 1 Spaces 1-4 Dehumidification Humidistat'][
                'dehumidifying_relative_humidity_setpoint_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:humidifier_type")
    def test_humidifier_type(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'humidifier_type'] = 'ElectricSteam'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'humidifier_control_zone_name'] = 'SPACE1-1'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'humidifier_relative_humidity_setpoint'] = 29
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output['Humidifier:Steam:Electric'].get('AHU 1 Spaces 1-4 Humidifier'))
        self.assertEqual(
            'HVACTemplate-Always29.0',
            epjson_output['ZoneControl:Humidistat']['AHU 1 Spaces 1-4 humidification Humidistat'][
                'humidifying_relative_humidity_setpoint_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:humidifier_schedule")
    def test_humidifier_schedule(self):
        self.ej.merge_epjson(
            super_dictionary=self.base_epjson,
            object_dictionary=schedule_objects)
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'humidifier_type'] = 'ElectricSteam'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'humidifier_control_zone_name'] = 'SPACE1-1'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'humidifier_relative_humidity_setpoint_schedule_name'] = 'Always29'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output['Humidifier:Steam:Electric'].get('AHU 1 Spaces 1-4 Humidifier'))
        self.assertEqual(
            'Always29',
            epjson_output['ZoneControl:Humidistat']['AHU 1 Spaces 1-4 humidification Humidistat'][
                'humidifying_relative_humidity_setpoint_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:ConstantVolume:humidification_and_dehumidification")
    def test_humidification_and_dehumidification(self):
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'humidifier_type'] = 'ElectricSteam'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'humidifier_control_zone_name'] = 'SPACE1-1'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'dehumidification_control_type'] = 'CoolReheat'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'dehumidification_control_zone_name'] = 'SPACE1-1'
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'dehumidification_relative_humidity_setpoint'] = 62
        self.base_epjson['HVACTemplate:System:ConstantVolume']['AHU 1 Spaces 1-4'][
            'humidifier_relative_humidity_setpoint'] = 29
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'TemperatureAndHumidityRatio',
            epjson_output['Controller:WaterCoil']['AHU 1 Spaces 1-4 Cooling Coil Controller']['control_variable'])
        self.assertEqual(
            'HVACTemplate-Always62.0',
            epjson_output['ZoneControl:Humidistat']['AHU 1 Spaces 1-4 Humidistat'][
                'dehumidifying_relative_humidity_setpoint_schedule_name'])
        self.assertIsNotNone(epjson_output['Humidifier:Steam:Electric'].get('AHU 1 Spaces 1-4 Humidifier'))
        self.assertEqual(
            'HVACTemplate-Always29.0',
            epjson_output['ZoneControl:Humidistat']['AHU 1 Spaces 1-4 Humidistat'][
                'humidifying_relative_humidity_setpoint_schedule_name'])
        return
