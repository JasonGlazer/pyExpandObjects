from pathlib import Path

from tests.simulations import BaseSimulationTest
from src.epjson_handler import EPJSON

test_dir = Path(__file__).parent.parent.parent

design_specification_objects = {
    "DesignSpecification:OutdoorAir": {
        "SPACE1-1 SZ DSOA Custom Object": {
            "outdoor_air_flow_per_zone": 0.01,
            "outdoor_air_method": "Flow/Zone"
        }
    },
    "DesignSpecification:ZoneAirDistribution": {
        "SPACE1-1 SZ DSZAD Custom Object": {}
    }
}


class TestSimulationsZoneDualDuct(BaseSimulationTest):
    def setUp(self):
        self.ej = EPJSON()
        base_idf_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles', 'HVACTemplate-5ZoneDualDuct.idf')
        base_copy_file_path = self._copy_to_test_directory(base_idf_file_path)
        # read in base file, then edit inputs for alternate tests
        self.base_epjson = self.get_epjson_object_from_idf_file(base_copy_file_path)
        # Remove Output:Variable Objects that cause naming conflicts
        self.base_epjson.pop('Output:Variable')
        return

    def teardown(self):
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:DualDuct:supply_air_maximum_flow_rate")
    def test_supply_air_maximum_flow_rate(self):
        # todo_eo: AirTerminal:DualDuct:ConstantVolume maximum_air_flow_rate is not set in legacy with these
        #  inputs which is causing the discrepancy.
        self.base_epjson['HVACTemplate:Zone:DualDuct']['HVACTemplate:Zone:DualDuct 1']['supply_air_maximum_flow_rate'] = 0.1
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.1,
            epjson_output['Sizing:Zone']['SPACE1-1 Sizing Zone']['cooling_design_air_flow_rate'])
        self.assertEqual(
            'Flow/Zone',
            epjson_output['Sizing:Zone']['SPACE1-1 Sizing Zone']['cooling_design_air_flow_method'])
        self.assertEqual(
            0.1,
            epjson_output['Sizing:Zone']['SPACE1-1 Sizing Zone']['heating_design_air_flow_rate'])
        self.assertEqual(
            'Flow/Zone',
            epjson_output['Sizing:Zone']['SPACE1-1 Sizing Zone']['heating_design_air_flow_method'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:DualDuct:zone_heating_sizing_factor")
    def test_zone_heating_sizing_factor(self):
        self.base_epjson['HVACTemplate:Zone:DualDuct']['HVACTemplate:Zone:DualDuct 1']['zone_heating_sizing_factor'] = 1.2
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            1.2,
            epjson_output['Sizing:Zone']['SPACE1-1 Sizing Zone']['zone_heating_sizing_factor'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:DualDuct:zone_cooling_sizing_factor")
    def test_zone_cooling_sizing_factor(self):
        self.base_epjson['HVACTemplate:Zone:DualDuct']['HVACTemplate:Zone:DualDuct 1']['zone_cooling_sizing_factor'] = 1.2
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            1.2,
            epjson_output['Sizing:Zone']['SPACE1-1 Sizing Zone']['zone_cooling_sizing_factor'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:DualDuct:zone_minimum_air_flow_fraction")
    def test_zone_minimum_air_flow_fraction(self):
        self.base_epjson['HVACTemplate:Zone:DualDuct']['HVACTemplate:Zone:DualDuct 1']['zone_minimum_air_flow_fraction'] = 0.3
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        # todo_eo: this option should create an AirTerminal:DualDuct:VAV object, but does not.  Given the default value,
        #  this should be the default operation
        # self.assertEqual(
        #     1.2,
        #     epjson_output['Sizing:Zone']['SPACE1-1 Sizing Zone']['zone_cooling_sizing_factor'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:ConstantVolume:outdoor_air_method_flow_per_person")
    def test_outdoor_air_method_flow_per_person(self):
        self.base_epjson['HVACTemplate:Zone:DualDuct']['HVACTemplate:Zone:DualDuct 1'][
            'outdoor_air_method'] = 'Flow/Person'
        self.base_epjson['HVACTemplate:Zone:DualDuct']['HVACTemplate:Zone:DualDuct 1'][
            'outdoor_air_flow_rate_per_person'] = 0.01
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'Flow/Person',
            epjson_output['DesignSpecification:OutdoorAir']['SPACE1-1 SZ DSOA']['outdoor_air_method'])
        self.assertEqual(
            0.01,
            epjson_output['DesignSpecification:OutdoorAir']['SPACE1-1 SZ DSOA']['outdoor_air_flow_per_person'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:DualDuct:outdoor_air_method_flow_per_area")
    def test_outdoor_air_method_flow_per_area(self):
        self.base_epjson['HVACTemplate:Zone:DualDuct']['HVACTemplate:Zone:DualDuct 1'][
            'outdoor_air_method'] = 'Flow/Area'
        self.base_epjson['HVACTemplate:Zone:DualDuct']['HVACTemplate:Zone:DualDuct 1'][
            'outdoor_air_flow_rate_per_zone_floor_area'] = 0.0014
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'Flow/Area',
            epjson_output['DesignSpecification:OutdoorAir']['SPACE1-1 SZ DSOA']['outdoor_air_method'])
        self.assertEqual(
            0.0014,
            epjson_output['DesignSpecification:OutdoorAir']['SPACE1-1 SZ DSOA']['outdoor_air_flow_per_zone_floor_area'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:DualDuct:outdoor_air_method_flow_per_zone")
    def test_outdoor_air_method_flow_per_zone(self):
        self.base_epjson['HVACTemplate:Zone:DualDuct']['HVACTemplate:Zone:DualDuct 1'][
            'outdoor_air_method'] = 'Flow/Zone'
        self.base_epjson['HVACTemplate:Zone:DualDuct']['HVACTemplate:Zone:DualDuct 1'][
            'outdoor_air_flow_rate_per_zone'] = 0.01
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'Flow/Zone',
            epjson_output['DesignSpecification:OutdoorAir']['SPACE1-1 SZ DSOA']['outdoor_air_method'])
        self.assertEqual(
            0.01,
            epjson_output['DesignSpecification:OutdoorAir']['SPACE1-1 SZ DSOA']['outdoor_air_flow_per_zone'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:DualDuct:outdoor_air_method_detailed_specification")
    def test_outdoor_air_method_detailed_specification(self):
        self.ej.merge_epjson(
            super_dictionary=self.base_epjson,
            object_dictionary=design_specification_objects)
        self.base_epjson['HVACTemplate:Zone:DualDuct']['HVACTemplate:Zone:DualDuct 1'][
            'outdoor_air_method'] = 'DetailedSpecification'
        self.base_epjson['HVACTemplate:Zone:DualDuct']['HVACTemplate:Zone:DualDuct 1'][
            'design_specification_outdoor_air_object_name_for_sizing'] = 'SPACE1-1 SZ DSOA Custom Object'
        self.base_epjson['HVACTemplate:Zone:DualDuct']['HVACTemplate:Zone:DualDuct 1'][
            'design_specification_zone_air_distribution_object_name'] = 'SPACE1-1 SZ DSZAD Custom Object'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output['DesignSpecification:OutdoorAir'].get('SPACE1-1 SZ DSOA Custom Object'))
        self.assertIsNotNone(epjson_output['DesignSpecification:ZoneAirDistribution'].get('SPACE1-1 SZ DSZAD Custom Object'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:DualDuct:outdoor_air_method_detailed_specification")
    def test_design_specification_outdoor_air_object_name_for_control(self):
        self.ej.merge_epjson(
            super_dictionary=self.base_epjson,
            object_dictionary=design_specification_objects)
        # todo_eo: it is unclear what changes should be triggered for this option
        self.base_epjson['HVACTemplate:Zone:DualDuct']['HVACTemplate:Zone:DualDuct 1'][
            'design_specification_outdoor_air_object_name_for_control'] = 'SPACE1-1 SZ DSOA Custom Object'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output['DesignSpecification:OutdoorAir'].get('SPACE1-1 SZ DSOA Custom Object'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:DualDuct:cold_supply_plenum_name")
    def test_cold_supply_plenum_name(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1'].pop('return_plenum_name')
        self.base_epjson['HVACTemplate:Zone:DualDuct']['HVACTemplate:Zone:DualDuct 1'][
            'cold_supply_plenum_name'] = 'PLENUM-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output['AirLoopHVAC:SupplyPlenum'].get('SPACE1-1 Cold Supply Plenum'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:DualDuct:hot_supply_plenum_name")
    def test_hot_supply_plenum_name(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1'].pop('return_plenum_name')
        self.base_epjson['HVACTemplate:Zone:DualDuct']['HVACTemplate:Zone:DualDuct 1'][
            'hot_supply_plenum_name'] = 'PLENUM-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output['AirLoopHVAC:SupplyPlenum'].get('SPACE1-1 Hot Supply Plenum'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:DualDuct:return_plenum_name")
    def test_return_plenum_name(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1'].pop('return_plenum_name')
        self.base_epjson['HVACTemplate:Zone:DualDuct']['HVACTemplate:Zone:DualDuct 1'][
            'return_plenum_name'] = 'PLENUM-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output['AirLoopHVAC:ReturnPlenum'].get('SPACE1-1 Return Plenum'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:DualDuct:baseboard_heating_type_hot_water")
    def test_baseboard_heating_type_hot_water(self):
        self.base_epjson['HVACTemplate:Zone:DualDuct']['HVACTemplate:Zone:DualDuct 1'][
            'baseboard_heating_type'] = 'HotWater'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output['ZoneHVAC:Baseboard:RadiantConvective:Water'].get('SPACE1-1 Baseboard Heat'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:DualDuct:baseboard_heating_type_electric")
    def test_baseboard_heating_type_electric(self):
        self.base_epjson['HVACTemplate:Zone:DualDuct']['HVACTemplate:Zone:DualDuct 1'][
            'baseboard_heating_type'] = 'Electric'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output['ZoneHVAC:Baseboard:Convective:Electric'].get('SPACE1-1 Baseboard Heat'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:DualDuct:baseboard_heating_availability_schedule_name")
    def test_baseboard_heating_availability_schedule_name(self):
        self.base_epjson['HVACTemplate:Zone:DualDuct']['HVACTemplate:Zone:DualDuct 1'][
            'baseboard_heating_type'] = 'HotWater'
        self.base_epjson['HVACTemplate:Zone:DualDuct']['HVACTemplate:Zone:DualDuct 1'][
            'baseboard_heating_availability_schedule_name'] = 'OCCUPY-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['ZoneHVAC:Baseboard:RadiantConvective:Water']['SPACE1-1 Baseboard Heat']['availability_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:DualDuct:baseboard_heating_capacity")
    def test_baseboard_heating_capacity(self):
        self.base_epjson['HVACTemplate:Zone:DualDuct']['HVACTemplate:Zone:DualDuct 1'][
            'baseboard_heating_type'] = 'HotWater'
        self.base_epjson['HVACTemplate:Zone:DualDuct']['HVACTemplate:Zone:DualDuct 1'][
            'baseboard_heating_capacity'] = 200
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            200,
            epjson_output['ZoneHVAC:Baseboard:RadiantConvective:Water']['SPACE1-1 Baseboard Heat']['heating_design_capacity'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:DualDuct:"
                                              "zone_cooling_design_supply_air_temperature_input_method_"
                                              "system_supply_air_temperature")
    def test_zone_cooling_design_supply_air_temperature_input_method_system_supply_air_temperature(self):
        self.base_epjson['HVACTemplate:System:DualDuct']['SYS 1'][
            'cooling_coil_design_setpoint_temperature'] = 13.0
        self.base_epjson['HVACTemplate:Zone:DualDuct']['HVACTemplate:Zone:DualDuct 1'][
            'zone_cooling_design_supply_air_temperature_input_method'] = "SystemSupplyAirTemperature"
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            13.0,
            epjson_output['Sizing:Zone']['SPACE1-1 Sizing Zone']['zone_cooling_design_supply_air_temperature'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:DualDuct:"
                                              "zone_cooling_design_supply_air_temperature_input_method_"
                                              "supply_air_temperature")
    def test_zone_cooling_design_supply_air_temperature_input_method_supply_air_temperature(self):
        self.base_epjson['HVACTemplate:Zone:DualDuct']['HVACTemplate:Zone:DualDuct 1'][
            'zone_cooling_design_supply_air_temperature'] = 13.0
        self.base_epjson['HVACTemplate:Zone:DualDuct']['HVACTemplate:Zone:DualDuct 1'][
            'zone_cooling_design_supply_air_temperature_input_method'] = "SupplyAirTemperature"
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            13.0,
            epjson_output['Sizing:Zone']['SPACE1-1 Sizing Zone']['zone_cooling_design_supply_air_temperature'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:DualDuct:"
                                              "zone_cooling_design_supply_air_temperature_input_method_"
                                              "temperature_difference")
    def test_zone_cooling_design_supply_air_temperature_input_method_temperature_difference(self):
        self.base_epjson['HVACTemplate:Zone:DualDuct']['HVACTemplate:Zone:DualDuct 1'][
            'zone_cooling_design_supply_air_temperature_difference'] = 11.5
        self.base_epjson['HVACTemplate:Zone:DualDuct']['HVACTemplate:Zone:DualDuct 1'][
            'zone_cooling_design_supply_air_temperature_input_method'] = "TemperatureDifference"
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            11.5,
            epjson_output['Sizing:Zone']['SPACE1-1 Sizing Zone']['zone_cooling_design_supply_air_temperature_difference'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:DualDuct:"
                                              "zone_heating_design_supply_air_temperature_input_method_"
                                              "supply_air_temperature")
    def test_zone_heating_design_supply_air_temperature_input_method_supply_air_temperature(self):
        self.base_epjson['HVACTemplate:Zone:DualDuct']['HVACTemplate:Zone:DualDuct 1'][
            'zone_heating_design_supply_air_temperature'] = 51
        self.base_epjson['HVACTemplate:Zone:DualDuct']['HVACTemplate:Zone:DualDuct 1'][
            'zone_heating_design_supply_air_temperature_input_method'] = "SupplyAirTemperature"
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            51,
            epjson_output['Sizing:Zone']['SPACE1-1 Sizing Zone']['zone_heating_design_supply_air_temperature'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:DualDuct:"
                                              "zone_heating_design_supply_air_temperature_input_method_"
                                              "temperature_difference")
    def test_zone_heating_design_supply_air_temperature_input_method_temperature_difference(self):
        self.base_epjson['HVACTemplate:Zone:DualDuct']['HVACTemplate:Zone:DualDuct 1'][
            'zone_heating_design_supply_air_temperature_difference'] = 31
        self.base_epjson['HVACTemplate:Zone:DualDuct']['HVACTemplate:Zone:DualDuct 1'][
            'zone_heating_design_supply_air_temperature_input_method'] = "TemperatureDifference"
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            31,
            epjson_output['Sizing:Zone']['SPACE1-1 Sizing Zone']['zone_heating_design_supply_air_temperature_difference'])
        return
