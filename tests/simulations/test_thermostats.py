import unittest
from pathlib import Path

from tests import BaseTest
from tests.simulations import BaseSimulationTest
from src.epjson_handler import EPJSON
from src.expand_objects import ExpandThermostat

test_dir = Path(__file__).parent.parent


class TestSimulationSimple(BaseTest, BaseSimulationTest, unittest.TestCase):
    def setUp(self):
        return

    def teardown(self):
        return

    def test_simulation(self):
        base_file_path = str(test_dir / '..' / 'simulation' / 'ExampleFiles' /
                             'HVACTemplate-5ZoneVAVWaterCooledExpanded.epJSON')
        base_formatted_epjson = self.setup_file(base_file_path)
        base_input_file_path = self.write_file_for_testing(
            epjson=base_formatted_epjson,
            file_name='base_input_epjson.epJSON')
        # drop objects that will be inserted
        epj = EPJSON()
        epj.load_epjson(epjson_ref=base_formatted_epjson)
        test_purged_epjson = epj.purge_epjson(
            epjson=epj.input_epjson,
            purge_dictionary={
                'ThermostatSetpoint:DualSetpoint': '.*'
            })
        # Create template for expansion
        test_thermostat_template = {
            "HVACTemplate:Thermostat": {
                "All Zones Dual": {
                    "cooling_setpoint_schedule_name": "Clg-SetP-Sch",
                    "heating_setpoint_schedule_name": "Htg-SetP-Sch"
                }
            }
        }
        eo = ExpandThermostat(template=test_thermostat_template)
        eo.run()
        test_formatted_epjson = epj.merge_epjson(
            super_dictionary=test_purged_epjson,
            object_dictionary=eo.epjson,
            unique_name_override=False
        )
        test_input_file_path = self.write_file_for_testing(
            epjson=test_formatted_epjson,
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
        # compare epJSONs
        comparison_results = self.compare_epjsons(base_formatted_epjson, test_formatted_epjson)
        if comparison_results:
            # trigger failure
            self.assertEqual('', comparison_results, comparison_results)
        return
