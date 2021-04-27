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

mock_hw_plant_loop_template = {
    "HVACTemplate:Plant:HotWaterLoop": {
        "Hot Water Loop HW": {
            "hot_water_design_setpoint": 82,
            "hot_water_plant_operation_scheme_type": "Default",
            "hot_water_pump_configuration": "ConstantFlow",
            "hot_water_pump_rated_head": 179352,
            "hot_water_reset_outdoor_dry_bulb_high": 10,
            "hot_water_reset_outdoor_dry_bulb_low": -6.7,
            "hot_water_setpoint_at_outdoor_dry_bulb_high": 65.6,
            "hot_water_setpoint_at_outdoor_dry_bulb_low": 82.2,
            "hot_water_setpoint_reset_type": "OutdoorAirTemperatureReset",
            "pump_control_type": "Intermittent"
        }
    }
}


class TestSimulationSimple(BaseTest, BaseSimulationTest, unittest.TestCase):
    def setUp(self):
        return

    def teardown(self):
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Plant:ChilledWaterLoop ConstantPrimaryNoSecondary w/o connections")
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
                'Sizing:Plant': 'Sizing:Plant 2',
                'PlantEquipmentOperation:CoolingLoad': 'Chilled Water Loop Chiller.*',
                'PlantEquipmentOperationSchemes': 'Chilled Water Loop Chiller.*'
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
        output_epjson['PlantLoop']['Chilled Water Loop Chilled Water Loop']['plant_equipment_operation_scheme_name'] = \
            'Chilled Water Loop ChW Operation'
        output_epjson['PlantEquipmentOperation:CoolingLoad']['Chilled Water Loop ChW All Hours']['range_1_equipment_list_name'] = \
            "Chilled Water Loop All Chillers"
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

    @BaseTest._test_logger(doc_text="HVACTemplate:Plant:ChilledWaterLoop VariablePrimaryNoSecondary w/o connections")
    def test_simulation_chilled_water_variable_primary_no_secondary_wo_connections(self):
        # todo_eo: base file needs to be modified for variable pumping.
        base_file_path = str(test_dir / '..' / 'simulation' / 'ExampleFiles' /
                             'HVACTemplate-5ZoneVAVWaterCooledExpanded.epJSON')
        base_formatted_epjson = self.setup_file(base_file_path)
        # replace chilled water loop constant primary with variable primary
        epj = EPJSON()
        base_formatted_epjson = epj.purge_epjson(
            epjson=base_formatted_epjson,
            purge_dictionary={
                'Pump:ConstantSpeed': 'Chilled Water Loop ChW.*',
                'Branch': 'Chilled Water Loop ChW Supply Inlet Branch'
            }
        )
        epj.merge_epjson(
            super_dictionary=base_formatted_epjson,
            object_dictionary={
                'Pump:VariableSpeed': {
                    "Chilled Water Loop ChW Supply Pump": {
                        "design_flow_rate": "Autosize",
                        "design_power_consumption": "Autosize",
                        "design_pump_head": 179352,
                        "fraction_of_motor_inefficiencies_to_fluid_stream": 0,
                        "inlet_node_name": "Chilled Water Loop ChW Supply Inlet",
                        "motor_efficiency": 0.9,
                        "outlet_node_name": "Chilled Water Loop ChW Pump Outlet",
                        "pump_control_type": "Intermittent"
                    }
                },
                "Branch": {
                    "Chilled Water Loop ChW Supply Inlet Branch": {
                        "components": [
                            {
                                "component_inlet_node_name": "Chilled Water Loop ChW Supply Inlet",
                                "component_name": "Chilled Water Loop ChW Supply Pump",
                                "component_object_type": "Pump:VariableSpeed",
                                "component_outlet_node_name": "Chilled Water Loop ChW Pump Outlet"
                            }
                        ]
                    }
                }
            })
        base_input_file_path = self.write_file_for_testing(
            epjson=base_formatted_epjson,
            file_name='base_input_epjson.epJSON')
        # drop objects that will be inserted
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
                'Sizing:Plant': 'Sizing:Plant 2',
                'PlantEquipmentOperation:CoolingLoad': 'Chilled Water Loop Chiller.*',
                'PlantEquipmentOperationSchemes': 'Chilled Water Loop Chiller.*'
            }
        )
        test_epjson = copy.deepcopy(test_purged_epjson)
        tmp_mock = copy.deepcopy(mock_chw_plant_loop_template)
        tmp_mock['HVACTemplate:Plant:ChilledWaterLoop']['Chilled Water Loop ChW']['chilled_water_pump_configuration'] = \
            'VariablePrimaryNoSecondary'
        epj.merge_epjson(
            super_dictionary=test_epjson,
            object_dictionary=tmp_mock
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
        output_epjson['PlantLoop']['Chilled Water Loop Chilled Water Loop']['plant_equipment_operation_scheme_name'] = \
            'Chilled Water Loop ChW Operation'
        output_epjson['PlantEquipmentOperation:CoolingLoad']['Chilled Water Loop ChW All Hours']['range_1_equipment_list_name'] = \
            "Chilled Water Loop All Chillers"
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

    @BaseTest._test_logger(doc_text="HVACTemplate:Plant:HotWaterLoop ConstantPrimaryNoSecondary w/o connections")
    def test_simulation_hot_water_constant_primary_no_secondary_wo_connections(self):
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
                'Branch': 'Hot Water Loop HW.*',
                'Pipe:Adiabatic': 'Hot Water Loop HW.*',
                'Pump:ConstantSpeed': 'Hot Water Loop HW.*',
                'SetpointManager:OutdoorAirReset': 'Chilled Water Loop ChW.*',
                'Sizing:Plant': 'Sizing:Plant 1',
                'PlantEquipmentOperation:HeatingLoad': 'Hot Water Loop.*',
                'PlantEquipmentOperationSchemes': 'Hot Water Loop.*'
            }
        )
        test_epjson = copy.deepcopy(test_purged_epjson)
        epj.merge_epjson(
            super_dictionary=test_epjson,
            object_dictionary=mock_hw_plant_loop_template
        )
        # perform steps that would be run in main
        self.hvactemplate = HVACTemplate()
        self.hvactemplate.epjson_process(epjson_ref=test_epjson)
        output_epjson = self.hvactemplate.run()['epJSON']
        # Rename connection objects due to naming discrepancies from old program to new
        output_epjson['Sizing:Plant']['Hot Water Loop HW Sizing Plant']['plant_or_condenser_loop_name'] = \
            'Hot Water Loop Hot Water Loop'
        output_epjson['PlantLoop']['Hot Water Loop Hot Water Loop']['plant_equipment_operation_scheme_name'] = \
            'Hot Water Loop HW Operation'
        output_epjson['PlantEquipmentOperation:HeatingLoad']['Hot Water Loop HW All Hours']['range_1_equipment_list_name'] = \
            "Hot Water Loop All Equipment"
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
