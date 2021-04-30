import unittest
from pathlib import Path
from argparse import Namespace

from tests import BaseTest
from tests.simulations import BaseSimulationTest
from src.main import main

test_dir = Path(__file__).parent.parent


class TestSimulationsFull(BaseTest, BaseSimulationTest, unittest.TestCase):
    def setUp(self):
        return

    def teardown(self):
        return

    def perform_full_comparison(self, baseline_file_location):
        """
        Simulate and compare two files where only the objects controlling output data are manipulated.
        Due to conversion issues within EnergyPlus, the baseline file must be simulated as an idf.
        :param baseline_file_location: idf file containing HVACTemplate:.* objects
        :return: None.  Assertions performed within function.
        """
        # setup outputs for perform_comparison to function and write base file
        base_formatted_epjson = self.setup_file(baseline_file_location)
        base_input_file_path = self.write_file_for_testing(
            epjson=base_formatted_epjson,
            file_name='base_input_epjson.epJSON')
        # convert to idf for simulation (epJSONs are unstable with the legacy process)
        base_idf_file_path = self.convert_file(base_input_file_path)
        # write the preformatted base file for main to call
        test_pre_input_file_path = self.write_file_for_testing(
            epjson=base_formatted_epjson,
            file_name='test_pre_input_epjson.epJSON')
        # Expand and perform comparisons between the files
        output = main(
            Namespace(
                no_schema=False,
                file=str(test_dir / '..' / 'simulation' / 'ExampleFiles' / 'test' / test_pre_input_file_path)))
        output_epjson = output['epJSON']
        test_input_file_path = self.write_file_for_testing(
            epjson=output_epjson,
            file_name='test_input_epjson.epJSON')
        # check outputs
        status_checks = self.perform_comparison([base_idf_file_path, test_input_file_path])
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

    @BaseTest._test_logger(doc_text="Simulation:Full:HVACTemplate-5ZoneVAVWAterCooled")
    def test_simulation_full_hvactemplate_5_zone_vav_watercooled(self):
        base_file_path = str(test_dir / '..' / 'simulation' / 'ExampleFiles' /
                             'HVACTemplate-5ZoneVAVWaterCooled.epJSON')
        self.perform_full_comparison(baseline_file_location=base_file_path)
        return
