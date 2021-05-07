import copy
from pathlib import Path

from tests.simulations import BaseSimulationTest
from src.hvac_template import HVACTemplate
from src.epjson_handler import EPJSON
from src.expand_objects import ExpandPlantLoop

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

mock_chiller_water_cooled_template = {
    "HVACTemplate:Plant:Chiller": {
        "Main Chiller": {
            "capacity": "Autosize",
            "chiller_type": "ElectricReciprocatingChiller",
            "condenser_type": "WaterCooled",
            "nominal_cop": 3.2,
            "priority": "1"
        }
    }
}


class TestSimulationSimplePlantLoop(BaseSimulationTest):
    def setUp(self):
        return

    def teardown(self):
        return

    @BaseSimulationTest._test_logger(doc_text="HVACTemplate:Plant:ChilledWaterLoop ConstantPrimaryNoSecondary w/o connections")
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
                'PlantEquipmentOperationSchemes': 'Chilled Water Loop Chiller.*',
                'PlantLoop': 'Chilled Water Loop Chilled Water Loop'
            }
        )
        test_epjson = copy.deepcopy(test_purged_epjson)
        epj.merge_epjson(
            super_dictionary=test_epjson,
            object_dictionary=mock_chw_plant_loop_template
        )
        # perform steps that would be run in main
        self.hvactemplate = HVACTemplate()
        self.hvactemplate._hvac_template_preprocess(epjson=test_epjson)
        self.hvactemplate.epjson_process(epjson_ref=test_epjson)
        self.expanded_plant_loops = self.hvactemplate._expand_templates(
            templates=mock_chw_plant_loop_template,
            expand_class=ExpandPlantLoop)
        merge_list = [
            self.hvactemplate.epjson,
            self.hvactemplate.base_objects,
            *[j.epjson for i, j in self.expanded_plant_loops.items()]
        ]
        output_epjson = {}
        for merge_dictionary in merge_list:
            self.hvactemplate.merge_epjson(
                super_dictionary=output_epjson,
                object_dictionary=merge_dictionary)
        # Rename connection objects due to naming discrepancies from old program to new
        output_epjson['PlantEquipmentOperation:CoolingLoad']['Chilled Water Loop ChW All Hours']['range_1_equipment_list_name'] = \
            "Chilled Water Loop All Chillers"
        test_input_file_path = self.write_file_for_testing(
            epjson=output_epjson,
            file_name='test_input_epjson.epJSON')
        # check outputs and compare epJSONs
        self.perform_comparison([base_input_file_path, test_input_file_path])
        self.compare_epjsons(base_formatted_epjson, output_epjson)
        return

    @BaseSimulationTest._test_logger(doc_text="HVACTemplate:Plant:ChilledWaterLoop VariablePrimaryNoSecondary w/o connections")
    def test_simulation_chilled_water_variable_primary_no_secondary_wo_connections(self):
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
                        "design_maximum_flow_rate": "Autosize",
                        "design_power_consumption": "Autosize",
                        "design_pump_head": 179352,
                        "inlet_node_name": "Chilled Water Loop ChW Supply Inlet",
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
                'PlantEquipmentOperationSchemes': 'Chilled Water Loop Chiller.*',
                'PlantLoop': 'Chilled Water Loop Chilled Water Loop'
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
        self.hvactemplate._hvac_template_preprocess(epjson=test_epjson)
        self.hvactemplate.epjson_process(epjson_ref=test_epjson)
        self.expanded_plant_loops = self.hvactemplate._expand_templates(
            templates=tmp_mock,
            expand_class=ExpandPlantLoop)
        merge_list = [
            self.hvactemplate.epjson,
            self.hvactemplate.base_objects,
            *[j.epjson for i, j in self.expanded_plant_loops.items()]
        ]
        output_epjson = {}
        for merge_dictionary in merge_list:
            self.hvactemplate.merge_epjson(
                super_dictionary=output_epjson,
                object_dictionary=merge_dictionary)
        # Rename connection objects due to naming discrepancies from old program to new
        output_epjson['PlantEquipmentOperation:CoolingLoad']['Chilled Water Loop ChW All Hours']['range_1_equipment_list_name'] = \
            "Chilled Water Loop All Chillers"
        test_input_file_path = self.write_file_for_testing(
            epjson=output_epjson,
            file_name='test_input_epjson.epJSON')
        # check outputs and compare epJSONs
        self.perform_comparison([base_input_file_path, test_input_file_path])
        self.compare_epjsons(base_formatted_epjson, output_epjson)
        return

    @BaseSimulationTest._test_logger(doc_text="HVACTemplate:Plant:HotWaterLoop ConstantPrimaryNoSecondary w/o connections")
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
                'PlantEquipmentOperationSchemes': 'Hot Water Loop.*',
                'PlantLoop': 'Hot Water Loop Hot Water Loop'
            }
        )
        test_epjson = copy.deepcopy(test_purged_epjson)
        epj.merge_epjson(
            super_dictionary=test_epjson,
            object_dictionary=mock_hw_plant_loop_template
        )
        # perform steps that would be run in main
        self.hvactemplate = HVACTemplate()
        self.hvactemplate._hvac_template_preprocess(epjson=test_epjson)
        self.hvactemplate.epjson_process(epjson_ref=test_epjson)
        self.expanded_plant_loops = self.hvactemplate._expand_templates(
            templates=mock_hw_plant_loop_template,
            expand_class=ExpandPlantLoop)
        merge_list = [
            self.hvactemplate.epjson,
            self.hvactemplate.base_objects,
            *[j.epjson for i, j in self.expanded_plant_loops.items()]
        ]
        output_epjson = {}
        for merge_dictionary in merge_list:
            self.hvactemplate.merge_epjson(
                super_dictionary=output_epjson,
                object_dictionary=merge_dictionary)
        # Rename connection objects due to naming discrepancies from old program to new
        output_epjson['PlantEquipmentOperation:HeatingLoad']['Hot Water Loop HW All Hours']['range_1_equipment_list_name'] = \
            "Hot Water Loop All Equipment"
        test_input_file_path = self.write_file_for_testing(
            epjson=output_epjson,
            file_name='test_input_epjson.epJSON')
        # check outputs and compare epJSONs
        self.perform_comparison([base_input_file_path, test_input_file_path])
        self.compare_epjsons(base_formatted_epjson, output_epjson)
        return
