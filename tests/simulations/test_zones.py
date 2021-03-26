import unittest
from pathlib import Path

from tests import BaseTest
from tests.simulations import BaseSimulationTest
from src.hvac_template import HVACTemplate
from src.epjson_handler import EPJSON

mock_thermostat_template = {
    "HVACTemplate:Thermostat": {
        "All Zones Dual": {
            "cooling_setpoint_schedule_name": "Clg-SetP-Sch",
            "heating_setpoint_schedule_name": "Htg-SetP-Sch"
        }
    }
}

mock_zone_template = {
    "HVACTemplate:Zone:VAV": {
        "HVACTemplate:Zone:VAV 1": {
            "baseboard_heating_capacity": "Autosize",
            "baseboard_heating_type": "None",
            "constant_minimum_air_flow_fraction": 0.3,
            "damper_heating_action": "Reverse",
            "outdoor_air_flow_rate_per_person": 0.00944,
            "outdoor_air_flow_rate_per_zone": 0.0,
            "outdoor_air_flow_rate_per_zone_floor_area": 0.0,
            "outdoor_air_method": "Flow/Person",
            "reheat_coil_type": "HotWater",
            "supply_air_maximum_flow_rate": "Autosize",
            "template_thermostat_name": "All Zones Dual",
            "template_vav_system_name": "VAV Sys 1",
            "zone_cooling_design_supply_air_temperature_input_method": "SystemSupplyAirTemperature",
            "zone_heating_design_supply_air_temperature": 50.0,
            "zone_heating_design_supply_air_temperature_input_method": "SupplyAirTemperature",
            "zone_minimum_air_flow_input_method": "Constant",
            "zone_name": "SPACE1-1"
        }
    }
}

test_dir = Path(__file__).parent.parent


class TestSimulationSimple(BaseTest, BaseSimulationTest, unittest.TestCase):
    def setUp(self):
        return

    def teardown(self):
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Zone:VAV w/ HW Reheat Simulation test")
    def test_simulation(self):
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
                'AirTerminal:SingleDuct:VAV:Reheat': 'SPACE1-1.*',
                'Branch': 'SPACE1-1.*',
                'Coil:Heating:Water': 'SPACE1-1.*',
                'DesignSpecification:OutdoorAir': '.*SPACE1-1',
                'DesignSpecification:ZoneAirDistribution': '.*SPACE1-1',
                'Sizing:Zone': 'Sizing:Zone 1',
                'ZoneControl:Thermostat': 'SPACE1-1.*',
                'ZoneHVAC:AirDistributionUnit': 'SPACE1-1.*',
                'ZoneHVAC:EquipmentConnections': 'ZoneHVAC:EquipmentConnections 1',
                'ZoneHVAC:EquipmentList': 'SPACE1-1.*'
            }
        )
        test_epjson = epj.merge_epjson(
            super_dictionary=test_purged_epjson,
            object_dictionary=dict(**mock_zone_template, **mock_thermostat_template)
        )
        # perform steps that would be run in main
        self.hvactemplate = HVACTemplate()
        self.hvactemplate.epjson_process(epjson_ref=test_epjson)
        output_epjson = self.hvactemplate.run()['epJSON']
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
