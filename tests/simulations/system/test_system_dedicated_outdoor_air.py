from pathlib import Path

from tests.simulations import BaseSimulationTest
from src.epjson_handler import EPJSON

test_dir = Path(__file__).parent.parent.parent


class TestSimulationsSystemDedicatedOutdoorAir(BaseSimulationTest):
    def setUp(self):
        self.ej = EPJSON()
        base_idf_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles', 'HVACTemplate-5ZonePTAC-DOAS.idf')
        base_copy_file_path = self._copy_to_test_directory(base_idf_file_path)
        # read in base file, then edit inputs for alternate tests
        self.base_epjson = self.get_epjson_object_from_idf_file(base_copy_file_path)
        return

    def teardown(self):
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DedicatedOutdoorAir:system_availability_schedule_name")
    def test_system_availability_schedule_name(self):
        self.base_epjson['HVACTemplate:System:DedicatedOutdoorAir']['DOAS']['system_availability_schedule_name'] = 'LIGHTS-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'LIGHTS-1',
            epjson_output['Fan:VariableVolume']['DOAS Supply Fan']['availability_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:DedicatedOutdoorAir:supply_fan_flow_rate")
    def test_supply_fan_flow_rate(self):
        # todo_eo: pick up here
        self.base_epjson['HVACTemplate:System:DedicatedOutdoorAir']['DOAS']['supply_fan_flow_rate'] = 2.0
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            2.0,
            epjson_output['Fan:VariableVolume']['DOAS Supply Fan']['maximum_flow_rate'])
        self.assertEqual(
            2.0,
            epjson_output['AirLoopHVAC']['DOAS']['design_supply_air_flow_rate'])
        return
