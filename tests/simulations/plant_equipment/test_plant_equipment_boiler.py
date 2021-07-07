from pathlib import Path

from tests.simulations import BaseSimulationTest
from src.epjson_handler import EPJSON

test_dir = Path(__file__).parent.parent.parent


class TestSimulationsPlantEquipmentBoiler(BaseSimulationTest):
    def setUp(self):
        self.ej = EPJSON()
        base_idf_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles', 'HVACTemplate-5ZoneVAVWaterCooled.idf')
        base_copy_file_path = self._copy_to_test_directory(base_idf_file_path)
        # read in base file, then edit inputs for alternate tests
        self.base_epjson = self.get_epjson_object_from_idf_file(base_copy_file_path)
        return

    def teardown(self):
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:PlantEquipment:Boiler:boiler_type_hot_water_boiler")
    def test_boiler_type_hot_water_boiler(self):
        self.base_epjson['HVACTemplate:Plant:Boiler']['Main Boiler']['boiler_type'] = 'HotWaterBoiler'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output.get('Boiler:HotWater'))
        self.assertEqual(
            'Main Boiler Efficiency Curve',
            epjson_output['Boiler:HotWater']['Main Boiler']['normalized_boiler_efficiency_curve_name'])
        self.assertEqual(
            'LeavingBoiler',
            epjson_output['Boiler:HotWater']['Main Boiler']['efficiency_curve_temperature_evaluation_variable'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:PlantEquipment:Boiler:boiler_type_district_hot_water")
    def test_boiler_type_district_hot_water(self):
        # todo_eo: Legacy does not appear to map this value to anything.  HotWaterBoiler used.
        self.base_epjson['HVACTemplate:Plant:Boiler']['Main Boiler']['boiler_type'] = 'DistrictHotWater'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output.get('DistrictHeating'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:PlantEquipment:Boiler:boiler_type_condensing_hot_water_boiler")
    def test_boiler_type_condensing_hot_water_boiler(self):
        self.base_epjson['HVACTemplate:Plant:Boiler']['Main Boiler']['boiler_type'] = 'CondensingHotWaterBoiler'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'Main Boiler Condensing Boiler Efficiency Curve',
            epjson_output['Boiler:HotWater']['Main Boiler']['normalized_boiler_efficiency_curve_name'])
        self.assertEqual(
            'EnteringBoiler',
            epjson_output['Boiler:HotWater']['Main Boiler']['efficiency_curve_temperature_evaluation_variable'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:PlantEquipment:Boiler:hot_water_boiler_efficiency")
    def test_hot_water_boiler_efficiency(self):
        self.base_epjson['HVACTemplate:Plant:Boiler']['Main Boiler']['boiler_type'] = 'HotWaterBoiler'
        self.base_epjson['HVACTemplate:Plant:Boiler']['Main Boiler']['efficiency'] = 0.77
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output.get('Boiler:HotWater'))
        self.assertEqual(
            0.77,
            epjson_output['Boiler:HotWater']['Main Boiler']['nominal_thermal_efficiency'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:PlantEquipment:Boiler:fuel_type")
    def test_fuel_type(self):
        self.base_epjson['HVACTemplate:Plant:Boiler']['Main Boiler']['boiler_type'] = 'HotWaterBoiler'
        self.base_epjson['HVACTemplate:Plant:Boiler']['Main Boiler']['fuel_type'] = 'Coal'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output.get('Boiler:HotWater'))
        self.assertEqual(
            'Coal',
            epjson_output['Boiler:HotWater']['Main Boiler']['fuel_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:PlantEquipment:Boiler:priority")
    def test_priority(self):
        # todo_eo: discuss with team that priority requires a string and not integer.  Otherwise, it silently fails
        #  and removes any object that is not 1 priority
        self.base_epjson['HVACTemplate:Plant:Boiler']['Main Boiler']['boiler_type'] = 'HotWaterBoiler'
        self.base_epjson['HVACTemplate:Plant:Boiler']['Main Boiler']['fuel_type'] = 'Coal'
        self.base_epjson['HVACTemplate:Plant:Boiler']['Main Boiler']['priority'] = '2'
        self.ej.merge_epjson(
            super_dictionary=self.base_epjson,
            object_dictionary={
                'HVACTemplate:Plant:Boiler': {
                    'Second Boiler': {
                        "boiler_type": "HotWaterBoiler",
                        "capacity": "Autosize",
                        "efficiency": 0.8,
                        "fuel_type": "Coal",
                        "priority": '1'
                    }
                }
            }
        )
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'Second Boiler',
            epjson_output['PlantEquipmentList']['Hot Water Loop All Equipment']['equipment'][0]['equipment_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:PlantEquipment:Boiler:inputs")
    def test_inputs(self):
        self.base_epjson['HVACTemplate:Plant:Boiler']['Main Boiler']['boiler_type'] = 'HotWaterBoiler'
        self.base_epjson['HVACTemplate:Plant:Boiler']['Main Boiler']['sizing_factor'] = 1.1
        self.base_epjson['HVACTemplate:Plant:Boiler']['Main Boiler']['minimum_part_load_ratio'] = 0.1
        self.base_epjson['HVACTemplate:Plant:Boiler']['Main Boiler']['maximum_part_load_ratio'] = 0.9
        self.base_epjson['HVACTemplate:Plant:Boiler']['Main Boiler']['optimum_part_load_ratio'] = 0.75
        self.base_epjson['HVACTemplate:Plant:Boiler']['Main Boiler']['water_outlet_upper_temperature_limit'] = 95
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            1.1,
            epjson_output['Boiler:HotWater']['Main Boiler']['sizing_factor'])
        self.assertEqual(
            0.1,
            epjson_output['Boiler:HotWater']['Main Boiler']['minimum_part_load_ratio'])
        self.assertEqual(
            0.9,
            epjson_output['Boiler:HotWater']['Main Boiler']['maximum_part_load_ratio'])
        self.assertEqual(
            0.75,
            epjson_output['Boiler:HotWater']['Main Boiler']['optimum_part_load_ratio'])
        self.assertEqual(
            95,
            epjson_output['Boiler:HotWater']['Main Boiler']['water_outlet_upper_temperature_limit'])
        return
