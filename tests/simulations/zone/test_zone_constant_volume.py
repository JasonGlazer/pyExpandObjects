from pathlib import Path

from tests.simulations import BaseSimulationTest
from src.epjson_handler import EPJSON

test_dir = Path(__file__).parent.parent.parent


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
