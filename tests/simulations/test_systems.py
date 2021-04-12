import unittest
import copy
from pathlib import Path

from tests import BaseTest
from tests.simulations import BaseSimulationTest
from src.epjson_handler import EPJSON
from src.hvac_template import HVACTemplate

mock_template = {
    "HVACTemplate:System:VAV": {
        "VAV Sys 1": {
            "cooling_coil_design_setpoint": 12.8,
            "cooling_coil_setpoint_reset_type": "None",
            "cooling_coil_type": "ChilledWater",
            "dehumidification_control_type": "None",
            "dehumidification_setpoint": 60.0,
            "economizer_lockout": "NoLockout",
            "economizer_lower_temperature_limit": 4,
            "economizer_type": "DifferentialDryBulb",
            "economizer_upper_temperature_limit": 19,
            "gas_heating_coil_efficiency": 0.8,
            "gas_heating_coil_parasitic_electric_load": 0.0,
            "gas_preheat_coil_efficiency": 0.8,
            "gas_preheat_coil_parasitic_electric_load": 0.0,
            "heat_recovery_type": "None",
            "heating_coil_design_setpoint": 10.0,
            "heating_coil_setpoint_reset_type": "None",
            "heating_coil_type": "HotWater",
            "humidifier_rated_capacity": 1e-06,
            "humidifier_rated_electric_power": 2690.0,
            "humidifier_setpoint": 30.0,
            "humidifier_type": "None",
            "latent_heat_recovery_effectiveness": 0.65,
            "maximum_outdoor_air_flow_rate": "Autosize",
            "minimum_outdoor_air_control_type": "FixedMinimum",
            "minimum_outdoor_air_flow_rate": "Autosize",
            "minimum_outdoor_air_schedule_name": "Min OA Sched",
            "night_cycle_control": "CycleOnAny",
            "preheat_coil_type": "None",
            "return_plenum_name": "PLENUM-1",
            "sensible_heat_recovery_effectiveness": 0.7,
            "sizing_option": "NonCoincident",
            "supply_fan_delta_pressure": 600,
            "supply_fan_maximum_flow_rate": "Autosize",
            "supply_fan_minimum_flow_rate": "Autosize",
            "supply_fan_motor_efficiency": 0.9,
            "supply_fan_motor_in_air_stream_fraction": 1,
            "supply_fan_part_load_power_coefficients": "InletVaneDampers",
            "supply_fan_placement": "DrawThrough",
            "supply_fan_total_efficiency": 0.7,
            "system_availability_schedule_name": "FanAvailSched"
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
        # todo_eo: add objects to yaml file.  There may be issues with VAV Sys 1 Cooling Coil ChW Branch as the
        #  unique name is picked up in the plant loop template expansion.  also for Heating coil
        test_purged_epjson = epj.purge_epjson(
            epjson=epj.input_epjson,
            purge_dictionary={
                'AirLoopHVAC': 'VAV Sys 1',
                'AirLoopHVAC:ControllerList': '.*',
                'AirLoopHVAC:OutdoorAirSystem': '.*',
                'AirLoopHVAC:OutdoorAirSystem:EquipmentList': '.*',
                'AirLoopHVAC:ReturnPath': '.*',
                'AirLoopHVAC:ReturnPlenum': '.*',
                'AirLoopHVAC:SupplyPath': '.*',
                'AirLoopHVAC:ZoneSplitter': '.*',
                'AvailabilityManager:NightCycle': '.*',
                'AvailabilityManagerAssignmentList': '^VAV Sys 1.*',
                'Branch': ['VAV Sys 1 Cooling Coil ChW Branch', 'VAV Sys 1 Heating Coil HW Branch',
                           'VAV Sys 1 Main Branch'],
                'BranchList': ['VAV Sys 1 Branches'],
                'Coil:Cooling:Water': '^VAV Sys 1.*',
                'Coil:Heating:Water': '^VAV Sys 1.*',
                'Controller:OutdoorAir': '.*',
                'Controller:WaterCoil': '.*',
                'Fan:VariableVolume': '.*',
                'NodeList': 'VAV Sys 1 Mixed Air Nodes',
                'OutdoorAir:Mixer': '.*',
                'OutdoorAir:NodeList': '.*',
                'SetpointManager:MixedAir': '.*',
                'SetpointManager:Scheduled': '.*',
                'Schedule:Compact': r'^HVACTemplate-Always\w+'
            }
        )
        test_epjson = copy.deepcopy(test_purged_epjson)
        epj.merge_epjson(
            super_dictionary=test_epjson,
            object_dictionary=mock_template
        )
        # perform steps that would be run in main
        self.hvactemplate = HVACTemplate()
        self.hvactemplate.epjson_process(epjson_ref=test_epjson)
        output_epjson = self.hvactemplate.run()['epJSON']
        # Insert zone connections since only system template tested
        zone_splitter = {
            "AirLoopHVAC:ZoneSplitter": {
                "VAV Sys 1 Zone Splitter": {
                    "inlet_node_name": "VAV Sys 1 Supply Path Inlet",
                    "nodes": [
                        {
                            "outlet_node_name": "SPACE1-1 Zone Equip Inlet"
                        },
                        {
                            "outlet_node_name": "SPACE2-1 Zone Equip Inlet"
                        },
                        {
                            "outlet_node_name": "SPACE3-1 Zone Equip Inlet"
                        },
                        {
                            "outlet_node_name": "SPACE4-1 Zone Equip Inlet"
                        },
                        {
                            "outlet_node_name": "SPACE5-1 Zone Equip Inlet"
                        }
                    ]
                }
            }
        }
        return_plenum = {
            "AirLoopHVAC:ReturnPlenum": {
                "VAV Sys 1 Return Plenum": {
                    "nodes": [
                        {
                            "inlet_node_name": "SPACE1-1 Return Outlet"
                        },
                        {
                            "inlet_node_name": "SPACE2-1 Return Outlet"
                        },
                        {
                            "inlet_node_name": "SPACE3-1 Return Outlet"
                        },
                        {
                            "inlet_node_name": "SPACE4-1 Return Outlet"
                        },
                        {
                            "inlet_node_name": "SPACE5-1 Return Outlet"
                        }
                    ],
                    "outlet_node_name": "VAV Sys 1 Return Air Outlet",
                    "zone_name": "PLENUM-1",
                    "zone_node_name": "PLENUM-1 Zone Air Node"
                }
            }
        }
        self.hvactemplate.merge_epjson(
            super_dictionary=output_epjson,
            object_dictionary=dict(**zone_splitter, **return_plenum)
        )
        from pprint import pprint
        pprint(output_epjson, width=200)
        test_input_file_path = self.write_file_for_testing(
            epjson=output_epjson,
            file_name='test_input_epjson.epJSON')
        # check outputs
        # status_checks = self.perform_comparison([base_input_file_path, test_input_file_path])
        # for energy_val in status_checks['total_energy_outputs']:
        #     self.assertAlmostEqual(energy_val / max(status_checks['total_energy_outputs']), 1, 2)
        # for warning in status_checks['warning_outputs']:
        #     self.assertEqual(warning, max(status_checks['warning_outputs']))
        # for error in status_checks['error_outputs']:
        #     self.assertEqual(error, max(status_checks['error_outputs']))
        #     self.assertGreaterEqual(error, 0)
        # for status in status_checks['finished_statuses']:
        #     self.assertEqual(1, status)
        # # compare epJSONs
        # comparison_results = self.compare_epjsons(base_formatted_epjson, output_epjson)
        # if comparison_results:
        #     # trigger failure
        #     self.assertEqual('', comparison_results, comparison_results)
        return

    # todo_eo: do system-zone connection test as well
