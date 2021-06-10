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


class TestSimulationsZoneConstantVolume(BaseSimulationTest):
    def setUp(self):
        self.ej = EPJSON()
        base_idf_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles', 'HVACTemplate-5ZoneConstantVolumeChillerBoiler.idf')
        base_copy_file_path = self._copy_to_test_directory(base_idf_file_path)
        # read in base file, then edit inputs for alternate tests
        self.base_epjson = self.get_epjson_object_from_idf_file(base_copy_file_path)
        return

    def teardown(self):
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:ConstantVolume:supply_air_maximum_flow_rate_no_reheat")
    def test_supply_air_maximum_flow_rate_no_reheat(self):
        # todo_eo: AirTerminal:SingleDuct:ConstantVolume:NoReheat maximum_air_flow_rate is not set in legacy with these
        #  inputs which is causing the discrepancy.
        self.base_epjson['HVACTemplate:Zone:ConstantVolume']['HVACTemplate:Zone:ConstantVolume 1']['supply_air_maximum_flow_rate'] = 0.1
        self.base_epjson['HVACTemplate:Zone:ConstantVolume']['HVACTemplate:Zone:ConstantVolume 1']['reheat_coil_type'] = 'None'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.1,
            epjson_output['AirTerminal:SingleDuct:ConstantVolume:NoReheat']['SPACE1-1 CV']['maximum_air_flow_rate'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:ConstantVolume:zone_heating_sizing_factor")
    def test_zone_heating_sizing_factor(self):
        self.base_epjson['HVACTemplate:Zone:ConstantVolume']['HVACTemplate:Zone:ConstantVolume 1']['zone_heating_sizing_factor'] = 1.2
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            1.2,
            epjson_output['Sizing:Zone']['SPACE1-1 Sizing Zone']['zone_heating_sizing_factor'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:ConstantVolume:zone_cooling_sizing_factor")
    def test_zone_cooling_sizing_factor(self):
        self.base_epjson['HVACTemplate:Zone:ConstantVolume']['HVACTemplate:Zone:ConstantVolume 1']['zone_cooling_sizing_factor'] = 1.2
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            1.2,
            epjson_output['Sizing:Zone']['SPACE1-1 Sizing Zone']['zone_cooling_sizing_factor'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:ConstantVolume:outdoor_air_method_flow_per_person")
    def test_outdoor_air_method_flow_per_person(self):
        self.base_epjson['HVACTemplate:Zone:ConstantVolume']['HVACTemplate:Zone:ConstantVolume 1'][
            'outdoor_air_method'] = 'Flow/Person'
        self.base_epjson['HVACTemplate:Zone:ConstantVolume']['HVACTemplate:Zone:ConstantVolume 1'][
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

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:ConstantVolume:outdoor_air_method_flow_per_area")
    def test_outdoor_air_method_flow_per_area(self):
        self.base_epjson['HVACTemplate:Zone:ConstantVolume']['HVACTemplate:Zone:ConstantVolume 1'][
            'outdoor_air_method'] = 'Flow/Area'
        self.base_epjson['HVACTemplate:Zone:ConstantVolume']['HVACTemplate:Zone:ConstantVolume 1'][
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

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:ConstantVolume:outdoor_air_method_flow_per_zone")
    def test_outdoor_air_method_flow_per_zone(self):
        self.base_epjson['HVACTemplate:Zone:ConstantVolume']['HVACTemplate:Zone:ConstantVolume 1'][
            'outdoor_air_method'] = 'Flow/Zone'
        self.base_epjson['HVACTemplate:Zone:ConstantVolume']['HVACTemplate:Zone:ConstantVolume 1'][
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

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:ConstantVolume:outdoor_air_method_detailed_specification")
    def test_outdoor_air_method_detailed_specification(self):
        self.ej.merge_epjson(
            super_dictionary=self.base_epjson,
            object_dictionary=design_specification_objects)
        self.base_epjson['HVACTemplate:Zone:ConstantVolume']['HVACTemplate:Zone:ConstantVolume 1'][
            'outdoor_air_method'] = 'DetailedSpecification'
        self.base_epjson['HVACTemplate:Zone:ConstantVolume']['HVACTemplate:Zone:ConstantVolume 1'][
            'design_specification_outdoor_air_object_name'] = 'SPACE1-1 SZ DSOA Custom Object'
        self.base_epjson['HVACTemplate:Zone:ConstantVolume']['HVACTemplate:Zone:ConstantVolume 1'][
            'design_specification_zone_air_distribution_object_name'] = 'SPACE1-1 SZ DSZAD Custom Object'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output['DesignSpecification:OutdoorAir'].get('SPACE1-1 SZ DSOA Custom Object'))
        self.assertIsNotNone(epjson_output['DesignSpecification:ZoneAirDistribution'].get('SPACE1-1 SZ DSZAD Custom Object'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:ConstantVolume:reheat_coil_type_none")
    def test_reheat_coil_type_none(self):
        self.base_epjson['HVACTemplate:Zone:ConstantVolume']['HVACTemplate:Zone:ConstantVolume 1'][
            'reheat_coil_type'] = 'None'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output['AirTerminal:SingleDuct:ConstantVolume:NoReheat']['SPACE1-1 CV'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:ConstantVolume:reheat_coil_type_electric")
    def test_reheat_coil_type_electric(self):
        # todo_eo: legacy fails on this option.
        self.base_epjson['HVACTemplate:Zone:ConstantVolume']['HVACTemplate:Zone:ConstantVolume 1'][
            'reheat_coil_type'] = 'Electric'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output['AirTerminal:SingleDuct:ConstantVolume:Reheat']['SPACE1-1 CV'])
        return