import copy
from pathlib import Path
from argparse import Namespace

from tests.simulations import BaseSimulationTest
from src.epjson_handler import EPJSON
from src.main import main

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

test_dir = Path(__file__).parent.parent.parent


class TestSimulationFiles(BaseSimulationTest):
    """
    Simulation testing which writes epJSON objects to non-temporary files.
    """

    def setUp(self):
        return

    def teardown(self):
        return

    @BaseSimulationTest._test_logger(doc_text="HVACTemplate:Zone:VAV w/ HW Reheat Simulation test")
    def test_simulation(self):
        # initialize list of files to run
        file_run_list = []
        # set subdirectory
        sub_directory = ['simulation', 'test', 'output_files']
        original_file_path = str(test_dir / '..' / 'simulation' / 'ExampleFiles' /
                                 'HVACTemplate-5ZoneVAVWaterCooledExpanded.epJSON')
        original_formatted_epjson = self.setup_file(original_file_path)
        original_input_file_path = self.write_file_for_testing(
            epjson=original_formatted_epjson,
            sub_directory=sub_directory,
            file_name='HVACTemplate-5ZoneVAVWaterCooledOriginal.epJSON')
        file_run_list.append(original_input_file_path)
        # drop objects that will be inserted
        epj = EPJSON()
        epj.epjson_process(epjson_ref=original_input_file_path)
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
        test_epjson = copy.deepcopy(test_purged_epjson)
        # merge in HVACTemplate objects
        epj.merge_epjson(
            super_dictionary=test_epjson,
            object_dictionary=dict(**mock_zone_template, **mock_thermostat_template))
        prepared_file_path = self.write_file_for_testing(
            epjson=test_epjson,
            sub_directory=sub_directory,
            file_name='HVACTemplate-5ZoneVAVWaterCooledZoneTestPrepared.epJSON')
        # test the file prepped with new templates
        output_directory = test_dir.joinpath('../', *sub_directory)
        output = main(
            Namespace(
                file=prepared_file_path,
                no_schema=False,
                output_directory=output_directory))
        file_run_list.append(output_directory.joinpath(output['output_files']['expanded']))
        # check outputs and compare epJSONs
        self.perform_comparison(file_run_list)
        self.compare_epjsons(original_formatted_epjson, output['epJSON'])
        return
