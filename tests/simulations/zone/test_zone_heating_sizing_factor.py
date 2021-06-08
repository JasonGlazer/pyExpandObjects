from pathlib import Path

from tests.simulations import BaseSimulationTest
from src.epjson_handler import EPJSON

test_dir = Path(__file__).parent.parent.parent


class TestSimulationsZoneZoneHeatingSizingFactor(BaseSimulationTest):
    def setUp(self):
        return

    def teardown(self):
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:zone_heating_sizing_factor:HVACTemplate-5ZoneBaseboardHeat")
    def test_5_zone_baseboard_heat(self):
        base_idf_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles', 'HVACTemplate-5ZoneBaseboardHeat.idf')
        base_copy_file_path = self._copy_to_test_directory(base_idf_file_path)
        # read in base file, then edit inputs for alternate tests
        base_epjson = self.get_epjson_object_from_idf_file(base_copy_file_path)
        base_epjson['HVACTemplate:Zone:BaseboardHeat']['HVACTemplate:Zone:BaseboardHeat 1']['zone_heating_sizing_factor'] = 1.2
        base_file_path = self.create_idf_file_from_epjson(epjson=base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        ej = EPJSON()
        epjson_output = ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            1.2,
            epjson_output['Sizing:Zone']['SPACE1-1 Sizing Zone']['zone_heating_sizing_factor'])
        return
