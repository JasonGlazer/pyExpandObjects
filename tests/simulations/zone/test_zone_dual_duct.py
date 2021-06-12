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
        self.base_epjson['Output:Variable'].pop('Output:Variable 31')
        self.base_epjson['Output:Variable'].pop('Output:Variable 32')
        self.base_epjson['Output:Variable'].pop('Output:Variable 33')
        self.base_epjson['Output:Variable'].pop('Output:Variable 34')
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
            epjson_output['AAirTerminal:DualDuct:ConstantVolume']['SPACE1-1 Dual Duct']['maximum_air_flow_rate'])
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

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:ConstantVolume:outdoor_air_method_flow_per_zone")
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

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:ConstantVolume:outdoor_air_method_detailed_specification")
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
