import unittest
from pathlib import Path

from tests import BaseTest
from tests.simulations import BaseSimulationTest
from src.hvac_template import HVACTemplate

test_dir = Path(__file__).parent.parent


class TestSimulationsFull(BaseTest, BaseSimulationTest, unittest.TestCase):
    def setUp(self):
        return

    def teardown(self):
        return

    @BaseTest._test_logger(doc_text="Simulation:Full:HVACTemplate-5ZoneVAVWAterCooledExpanded")
    def test_simulation_full_hvactemplate_5_zone_vav_watercooled(self):
        base_file_path = str(test_dir / '..' / 'simulation' / 'ExampleFiles' /
                             'HVACTemplate-5ZoneVAVWaterCooled.epJSON')
        base_formatted_epjson = self.setup_file(base_file_path)
        base_input_file_path = self.write_file_for_testing(
            epjson=base_formatted_epjson,
            file_name='base_input_epjson.epJSON')
        self.hvactemplate = HVACTemplate()
        output = self.hvactemplate.run(input_epjson=base_formatted_epjson)
        output_epjson = output['epJSON']
        test_input_file_path = self.write_file_for_testing(
            epjson=output_epjson,
            file_name='test_input_epjson.epJSON')
        # check outputs
        status_checks = self.perform_comparison([base_input_file_path, test_input_file_path])
        for energy_val in status_checks['total_energy_outputs']:
            self.assertAlmostEqual(energy_val / max(status_checks['total_energy_outputs']), 1, 2)
        for warning in status_checks['warning_outputs']:
            self.assertEqual(warning, max(status_checks['warning_outputs']))
        for error in status_checks['error_outputs']:
            self.assertEqual(error, max(status_checks['error_outputs']))
            self.assertGreaterEqual(error, 0)
        for status in status_checks['finished_statuses']:
            self.assertEqual(1, status)
        return
