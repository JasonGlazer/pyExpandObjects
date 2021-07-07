from pathlib import Path

from tests.simulations import BaseSimulationTest
from src.epjson_handler import EPJSON

test_dir = Path(__file__).parent.parent.parent


class TestSimulationsPlantEquipmentTower(BaseSimulationTest):
    def setUp(self):
        self.ej = EPJSON()
        base_idf_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles',
                                               'HVACTemplate-5ZoneWaterToAirHeatPumpTowerBoiler.idf')
        base_copy_file_path = self._copy_to_test_directory(base_idf_file_path)
        # read in base file, then edit inputs for alternate tests
        self.base_epjson = self.get_epjson_object_from_idf_file(base_copy_file_path)
        return

    def teardown(self):
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:PlantEquipment:Tower:tower_type_single_speed")
    def test_tower_type_single_speed(self):
        self.base_epjson['HVACTemplate:Plant:Tower']['Main Tower']['tower_type'] = 'SingleSpeed'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output.get('CoolingTower:SingleSpeed'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:PlantEquipment:Tower:tower_type_two_speed")
    def test_tower_type_two_speed(self):
        self.base_epjson['HVACTemplate:Plant:Tower']['Main Tower']['tower_type'] = 'TwoSpeed'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output.get('CoolingTower:TwoSpeed'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:PlantEquipment:Tower:inputs_two_speed")
    def test_inputs_two_speed(self):
        # todo_eo: fan power inputs are not being mapped in legacy.
        # todo_eo: performance_input_method needs to be changed based on inputs for pyExpandObjects
        self.base_epjson['HVACTemplate:Plant:Tower']['Main Tower']['tower_type'] = 'TwoSpeed'
        self.base_epjson['HVACTemplate:Plant:Tower']['Main Tower']['high_speed_nominal_capacity'] = 25000
        self.base_epjson['HVACTemplate:Plant:Tower']['Main Tower']['high_speed_fan_power'] = 370
        self.base_epjson['HVACTemplate:Plant:Tower']['Main Tower']['low_speed_nominal_capacity'] = 10000
        self.base_epjson['HVACTemplate:Plant:Tower']['Main Tower']['low_speed_fan_power'] = 180
        self.base_epjson['HVACTemplate:Plant:Tower']['Main Tower']['free_convection_capacity'] = 2000
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            25000,
            epjson_output['CoolingTower:TwoSpeed']['Main Tower']['high_speed_nominal_capacity'])
        self.assertEqual(
            10000,
            epjson_output['CoolingTower:TwoSpeed']['Main Tower']['low_speed_nominal_capacity'])
        self.assertEqual(
            370,
            epjson_output['CoolingTower:TwoSpeed']['Main Tower']['high_fan_speed_fan_power'])
        self.assertEqual(
            180,
            epjson_output['CoolingTower:TwoSpeed']['Main Tower']['low_fan_speed_fan_power'])
        self.assertEqual(
            2000,
            epjson_output['CoolingTower:TwoSpeed']['Main Tower']['free_convection_nominal_capacity'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:PlantEquipment:Tower:inputs_single_speed")
    def test_inputs_single_speed(self):
        # todo_eo: fan power inputs are not being mapped in legacy.
        # todo_eo: performance_input_method needs to be changed based on inputs for pyExpandObjects
        self.base_epjson['HVACTemplate:Plant:Tower']['Main Tower']['tower_type'] = 'SingleSpeed'
        self.base_epjson['HVACTemplate:Plant:Tower']['Main Tower']['high_speed_nominal_capacity'] = 25000
        self.base_epjson['HVACTemplate:Plant:Tower']['Main Tower']['high_speed_fan_power'] = 370
        self.base_epjson['HVACTemplate:Plant:Tower']['Main Tower']['free_convection_capacity'] = 2000
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            25000,
            epjson_output['CoolingTower:SingleSpeed']['Main Tower']['nominal_capacity'])
        self.assertEqual(
            2000,
            epjson_output['CoolingTower:SingleSpeed']['Main Tower']['free_convection_capacity'])
        self.assertEqual(
            370,
            epjson_output['CoolingTower:SingleSpeed']['Main Tower']['design_fan_power'])
        return