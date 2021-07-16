from pathlib import Path

from tests.simulations import BaseSimulationTest
from src.epjson_handler import EPJSON

test_dir = Path(__file__).parent.parent.parent


class TestSimulationsSystemPackagedVAV(BaseSimulationTest):
    def setUp(self):
        self.ej = EPJSON()
        base_idf_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles', 'HVACTemplate-5ZonePackagedVAV.idf')
        base_copy_file_path = self._copy_to_test_directory(base_idf_file_path)
        # read in base file, then edit inputs for alternate tests
        self.base_epjson = self.get_epjson_object_from_idf_file(base_copy_file_path)
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
                                              "_draw_through_cooling_none_heating_none")
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
                                              "draw_through_cooling_outdoor_air_temperature_reset_heating_none")
    def test_supply_fan_placement_blow_through_cooling_outdoor_air_temperature_reset_heating_none(self):
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
                                              "draw_through_cooling_warmest_first_heating_none")
    def test_supply_fan_placement_draw_through_cooling_warmest_first_heating_none(self):
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
                                              "blow_through_cooling_warmest_first_heating_none")
    def test_supply_fan_placement_blow_through_cooling_warmest_first_heating_none(self):
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

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:minimum_outdoor_air_control_type"
                                              "proportional_minimum")
    def test_minimum_outdoor_air_control_type_proportional_minimum(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['minimum_outdoor_air_control_type'] = \
            'ProportionalMinimum'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'ProportionalMinimum',
            epjson_output['Controller:OutdoorAir']['DXVAV Sys 1 OA Controller']['minimum_limit_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:PackagedVAV:minimum_outdoor_air_control_type"
                                              "fixed_minimum")
    def test_minimum_outdoor_air_control_type_fixed_minimum(self):
        self.base_epjson['HVACTemplate:System:PackagedVAV']['DXVAV Sys 1']['minimum_outdoor_air_control_type'] = \
            'FixedMinimum'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'FixedMinimum',
            epjson_output['Controller:OutdoorAir']['DXVAV Sys 1 OA Controller']['minimum_limit_type'])
        return
