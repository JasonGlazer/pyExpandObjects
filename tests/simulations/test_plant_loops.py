import unittest
import copy
from pathlib import Path

from tests import BaseTest
from tests.simulations import BaseSimulationTest
from src.hvac_template import HVACTemplate
from src.epjson_handler import EPJSON

test_dir = Path(__file__).parent.parent

mock_chw_plant_loop_template = {
    "HVACTemplate:Plant:ChilledWaterLoop": {
        "Chilled Water Loop ChW": {
            "chilled_water_design_setpoint": 7.22,
            "chilled_water_pump_configuration": "ConstantPrimaryNoSecondary",
            "chilled_water_reset_outdoor_dry_bulb_high": 26.7,
            "chilled_water_reset_outdoor_dry_bulb_low": 15.6,
            "chilled_water_setpoint_at_outdoor_dry_bulb_high": 6.7,
            "chilled_water_setpoint_at_outdoor_dry_bulb_low": 12.2,
            "chilled_water_setpoint_reset_type": "None",
            "chiller_plant_operation_scheme_type": "Default",
            "condenser_plant_operation_scheme_type": "Default",
            "condenser_water_design_setpoint": 29.4,
            "condenser_water_pump_rated_head": 179352,
            "minimum_outdoor_dry_bulb_temperature": 7.22,
            "primary_chilled_water_pump_rated_head": 179352,
            "pump_control_type": "Intermittent",
            "secondary_chilled_water_pump_rated_head": 179352
        }
    }
}


class TestSimulationSimple(BaseTest, BaseSimulationTest, unittest.TestCase):
    def setUp(self):
        return

    def teardown(self):
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Plant:ChilledWaterLoop ConstPrimaryNoSecondary w/o connections")
    def test_simulation_chilled_water_constant_primary_no_secondary_wo_connections(self):
        base_file_path = str(test_dir / '..' / 'simulation' / 'ExampleFiles' /
                             'HVACTemplate-5ZoneVAVWaterCooledExpanded.epJSON')
        base_formatted_epjson = self.setup_file(base_file_path)
        base_input_file_path = self.write_file_for_testing(
            epjson=base_formatted_epjson,
            file_name='base_input_epjson.epJSON')
        # drop objects that will be inserted
        epj = EPJSON()
        epj.epjson_process(epjson_ref=base_formatted_epjson)
        test_purged_epjson = epj.purge_epjson(
            epjson=epj.input_epjson,
            purge_dictionary={
                'AvailabilityManager:LowTemperatureTurnOff': '.*',
                'AvailabilityManagerAssignmentList': 'Chilled Water Loop.*',
                'Branch': 'Chilled Water Loop ChW.*',
                'OutdoorAir:Node': 'Chilled Water Loop.*',
                'Pipe:Adiabatic': 'Chilled Water Loop ChW.*',
                'Pump:ConstantSpeed': 'Chilled Water Loop ChW.*',
                'SetpointManager:Scheduled': 'Chilled Water Loop ChW.*',
                'Sizing:Plant': 'Sizing:Plant 2'
            }
        )
        test_epjson = copy.deepcopy(test_purged_epjson)
        epj.merge_epjson(
            super_dictionary=test_epjson,
            object_dictionary=mock_chw_plant_loop_template
        )
        # perform steps that would be run in main
        self.hvactemplate = HVACTemplate()
        self.hvactemplate.epjson_process(epjson_ref=test_epjson)
        output_epjson = self.hvactemplate.run()['epJSON']
        # Rename connection objects due to naming discrepancies from old program to new
        output_epjson['PlantLoop']['Chilled Water Loop Chilled Water Loop']['availability_manager_list_name'] = \
            'Chilled Water Loop ChW Availability List'
        output_epjson['Sizing:Plant']['Chilled Water Loop ChW Sizing Plant']['plant_or_condenser_loop_name'] = \
            'Chilled Water Loop Chilled Water Loop'
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
        # compare epJSONs
        comparison_results = self.compare_epjsons(base_formatted_epjson, output_epjson)
        if comparison_results:
            # trigger failure
            self.assertEqual('', comparison_results, comparison_results)
        return
