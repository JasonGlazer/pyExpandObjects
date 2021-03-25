import unittest
from pathlib import Path

from tests import BaseTest
from tests.simulations import BaseSimulationTest
from src.epjson_handler import EPJSON

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
            "template_thermostat_name": "All Zones",
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

    # @BaseTest._test_logger(doc_text="HVACTemplate:Thermostat:Simulation test")
    # def test_simulation(self):
    #     base_file_path = str(test_dir / '..' / 'simulation' / 'ExampleFiles' /
    #                          'HVACTemplate-5ZoneVAVWaterCooledExpanded.epJSON')
    #     base_formatted_epjson = self.setup_file(base_file_path)
    #     base_input_file_path = self.write_file_for_testing(
    #         epjson=base_formatted_epjson,
    #         file_name='base_input_epjson.epJSON')
    #     # drop objects that will be inserted
    #     epj = EPJSON()
    #     epj.load_epjson(epjson_ref=base_formatted_epjson)
    #     test_purged_epjson = epj.purge_epjson(
    #         epjson=epj.input_epjson,
    #         purge_dictionary={})
    #     # Create template for expansion
    #     test_thermostat_template = {
    #         "HVACTemplate:Thermostat": {
    #             "All Zones Dual": {
    #                 "cooling_setpoint_schedule_name": "Clg-SetP-Sch",
    #                 "heating_setpoint_schedule_name": "Htg-SetP-Sch"
    #             }
    #         }
    #     }
    #     test_epjson = epj.merge_epjson(
    #         super_dictionary=test_purged_epjson,
    #         object_dictionary=test_thermostat_template
    #     )
