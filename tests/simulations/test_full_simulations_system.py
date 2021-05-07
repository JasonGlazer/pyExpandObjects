from pathlib import Path

from tests.simulations import BaseSimulationTest

test_dir = Path(__file__).parent.parent


class TestSimulationsFullSystem(BaseSimulationTest):
    def setUp(self):
        return

    def teardown(self):
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Full:System:HVACTemplate-5ZoneVAVWAterCooled:Return Fan")
    def test_simulation_full_hvactemplate_5_zone_vav_watercooled_with_return_fan(self):
        base_idf_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles', 'HVACTemplate-5ZoneVAVWaterCooled.idf')
        # read in base file, then edit inputs for alternate tests
        base_epjson = self.get_epjson_object_from_idf_file(base_idf_file_path)
        base_epjson['HVACTemplate:System:VAV']['VAV Sys 1']['return_fan'] = 'Yes'
        base_file_path = self.create_idf_file_from_epjson(epjson=base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        return
