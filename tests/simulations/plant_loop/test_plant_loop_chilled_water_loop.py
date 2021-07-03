from pathlib import Path

from tests.simulations import BaseSimulationTest
from src.epjson_handler import EPJSON

test_dir = Path(__file__).parent.parent.parent

schedule_objects = {
    "Schedule:Compact": {
        "Always7.2": {
            "data": [
                {
                    "field": "Through: 12/31"
                },
                {
                    "field": "For: AllDays"
                },
                {
                    "field": "Until: 24:00"
                },
                {
                    "field": 7.2
                }
            ],
            "schedule_type_limits_name": "Any Number"
        }
    }
}


class TestSimulationsPlantLoopChilledWaterLoop(BaseSimulationTest):
    def setUp(self):
        self.ej = EPJSON()
        base_idf_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles', 'HVACTemplate-5ZoneVAVWaterCooled.idf')
        base_copy_file_path = self._copy_to_test_directory(base_idf_file_path)
        # read in base file, then edit inputs for alternate tests
        self.base_epjson = self.get_epjson_object_from_idf_file(base_copy_file_path)
        return

    def teardown(self):
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:PlantLoop:ChilledWaterLoop:pump_schedule_name")
    def test_pump_schedule_name(self):
        self.base_epjson['HVACTemplate:Plant:ChilledWaterLoop']['Chilled Water Loop']['pump_schedule_name'] = 'OCCUPY-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['Pump:ConstantSpeed']['Chilled Water Loop Supply Pump']['pump_flow_rate_schedule_name'])
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['Pump:VariableSpeed']['Condenser Water Loop Supply Pump']['pump_flow_rate_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:PlantLoop:ChilledWaterLoop:pump_control_type_intermittent")
    def test_pump_control_type_intermittent(self):
        self.base_epjson['HVACTemplate:Plant:ChilledWaterLoop']['Chilled Water Loop']['pump_control_type'] = 'Intermittent'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'Intermittent',
            epjson_output['Pump:ConstantSpeed']['Chilled Water Loop Supply Pump']['pump_control_type'])
        self.assertEqual(
            'Intermittent',
            epjson_output['Pump:VariableSpeed']['Condenser Water Loop Supply Pump']['pump_control_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:PlantLoop:ChilledWaterLoop:pump_control_type_continuous")
    def test_pump_control_type_continuous(self):
        self.base_epjson['HVACTemplate:Plant:ChilledWaterLoop']['Chilled Water Loop']['pump_control_type'] = 'Continuous'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'Continuous',
            epjson_output['Pump:ConstantSpeed']['Chilled Water Loop Supply Pump']['pump_control_type'])
        self.assertEqual(
            'Continuous',
            epjson_output['Pump:VariableSpeed']['Condenser Water Loop Supply Pump']['pump_control_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:PlantLoop:ChilledWaterLoop:"
                                              "chiller_plant_operation_scheme_type")
    def test_chiller_plant_operation_scheme_type(self):
        # todo_eo: legacy fails with message: PlantEquipmentOperationSchemes = "CHILLED WATER LOOP OPERATION",
        #  could not find PlantEquipmentOperation:CoolingLoad = "CHILLED WATER LOOP OPERATION ALL HOURS".
        self.ej.merge_epjson(
            super_dictionary=self.base_epjson,
            object_dictionary={
                "Schedule:Compact": {
                    "HVACTemplate-Always1": {
                        "data": [
                            {
                                "field": "Through 12/31"
                            },
                            {
                                "field": "For AllDays"
                            },
                            {
                                "field": "Until 24:00"
                            },
                            {
                                "field": 1.0
                            }
                        ],
                        "schedule_type_limits_name": "Any Number"
                    }
                },
                "PlantEquipmentOperationSchemes": {
                    "Chilled Water Loop Operation": {
                        "control_scheme_1_name": "Chilled Water Loop Operation All Hours",
                        "control_scheme_1_object_type": "PlantEquipmentOperation:CoolingLoad",
                        "control_scheme_1_schedule_name": "HVACTemplate-Always1"
                    }
                }
            }
        )
        self.base_epjson['HVACTemplate:Plant:ChilledWaterLoop']['Chilled Water Loop'][
            'chiller_plant_operation_scheme_type'] = 'UserDefined'
        self.base_epjson['HVACTemplate:Plant:ChilledWaterLoop']['Chilled Water Loop'][
            'chiller_plant_equipment_operation_schemes_name'] = 'Chilled Water Loop Operation'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'Continuous',
            epjson_output['Pump:ConstantSpeed']['Chilled Water Loop Supply Pump']['pump_control_type'])
        self.assertEqual(
            'Continuous',
            epjson_output['Pump:VariableSpeed']['Condenser Water Loop Supply Pump']['pump_control_type'])
        return

    def test_chilled_water_setpoint_schedule_name(self):
        self.ej.merge_epjson(
            super_dictionary=self.base_epjson,
            object_dictionary=schedule_objects)
        self.base_epjson['HVACTemplate:Plant:ChilledWaterLoop']['Chilled Water Loop'][
            'chilled_water_setpoint_schedule_name'] = 'Always7.2'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'Always7.2',
            epjson_output['SetpointManager:Scheduled']['Chilled Water Loop Temp Manager']['schedule_name'])
        return

    def test_chilled_water_design_setpoint(self):
        self.base_epjson['HVACTemplate:Plant:ChilledWaterLoop']['Chilled Water Loop'][
            'chilled_water_design_setpoint'] = 7.1
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'HVACTemplate-Always7.1',
            epjson_output['SetpointManager:Scheduled']['Chilled Water Loop Temp Manager']['schedule_name'])
        self.assertEqual(
            7.1,
            epjson_output['Sizing:Plant']['Chilled Water Loop Sizing Plant']['design_loop_exit_temperature'])
        return

    def test_chilled_water_pump_configuration_constant_primary_no_secondary(self):
        self.base_epjson['HVACTemplate:Plant:ChilledWaterLoop']['Chilled Water Loop'][
            'chilled_water_pump_configuration'] = 'ConstantPrimaryNoSecondary'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output['Pump:ConstantSpeed'].get('Chilled Water Loop Supply Pump'))
        return

    def test_chilled_water_pump_configuration_variable_primary_no_secondary(self):
        self.base_epjson['HVACTemplate:Plant:ChilledWaterLoop']['Chilled Water Loop'][
            'chilled_water_pump_configuration'] = 'VariablePrimaryNoSecondary'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output['Pump:VariableSpeed'].get('Chilled Water Loop Supply Pump'))
        self.assertEqual(
            'LeavingSetpointModulated',
            epjson_output['Chiller:Electric:EIR']['Main Chiller']['chiller_flow_mode'])
        return

    def test_chilled_water_pump_configuration_constant_primary_variable_secondary(self):
        self.base_epjson['HVACTemplate:Plant:ChilledWaterLoop']['Chilled Water Loop'][
            'chilled_water_pump_configuration'] = 'ConstantPrimaryVariableSecondary'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output['Pump:ConstantSpeed'].get('Chilled Water Loop Supply Pump'))
        self.assertIsNotNone(epjson_output['Pump:VariableSpeed'].get('Chilled Water Loop Secondary Pump'))
        return