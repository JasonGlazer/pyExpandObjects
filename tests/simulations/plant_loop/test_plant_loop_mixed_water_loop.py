from pathlib import Path

from tests.simulations import BaseSimulationTest
from src.epjson_handler import EPJSON

test_dir = Path(__file__).parent.parent.parent

schedule_objects = {
    "Schedule:Compact": {
        "Always21": {
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
                    "field": 21
                }
            ],
            "schedule_type_limits_name": "Any Number"
        },
        "Always33": {
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
                    "field": 33
                }
            ],
            "schedule_type_limits_name": "Any Number"
        }
    }
}


class TestSimulationsPlantLoopMixedWaterLoop(BaseSimulationTest):
    def setUp(self):
        self.ej = EPJSON()
        base_idf_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles',
                                               'HVACTemplate-5ZoneWaterToAirHeatPumpTowerBoiler.idf')
        base_copy_file_path = self._copy_to_test_directory(base_idf_file_path)
        # read in base file, then edit inputs for alternate tests
        self.base_epjson = self.get_epjson_object_from_idf_file(base_copy_file_path)
        return

    def teardown(self):
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:PlantLoop:MixedWaterLoop:pump_schedule_name")
    def test_pump_schedule_name(self):
        self.base_epjson['HVACTemplate:Plant:MixedWaterLoop']['Only Water Loop']['pump_schedule_name'] = 'OCCUPY-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['Pump:ConstantSpeed']['Only Water Loop Supply Pump']['pump_flow_rate_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:PlantLoop:MixedWaterLoop:pump_control_type_intermittent")
    def test_pump_control_type_intermittent(self):
        self.base_epjson['HVACTemplate:Plant:MixedWaterLoop']['Only Water Loop']['pump_control_type'] = 'Intermittent'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'Intermittent',
            epjson_output['Pump:ConstantSpeed']['Only Water Loop Supply Pump']['pump_control_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:PlantLoop:MixedWaterLoop:pump_control_type_continuous")
    def test_pump_control_type_continuous(self):
        self.base_epjson['HVACTemplate:Plant:MixedWaterLoop']['Only Water Loop']['pump_control_type'] = 'Continuous'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'Continuous',
            epjson_output['Pump:ConstantSpeed']['Only Water Loop Supply Pump']['pump_control_type'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:PlantLoop:HotWaterLoop:"
                                              "hot_water_plant_operation_scheme_type")
    def test_operation_scheme_type(self):
        # todo_eo: legacy fails with message: PlantEquipmentOperationSchemes = "HOT WATER LOOP OPERATION CUSTOM",
        #  could not find PlantEquipmentOperation:HeatingLoad = "HOT WATER LOOP OPERATION ALL HOURS".
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
                    "Only Water Loop Operation Custom": {
                        "control_scheme_1_name": "Only Water Loop Heat Operation All Hours",
                        "control_scheme_1_object_type": "PlantEquipmentOperation:HeatingLoad",
                        "control_scheme_1_schedule_name": "HVACTemplate-Always1",
                        "control_scheme_2_name": "Only Water Loop Cool Operation All Hours",
                        "control_scheme_2_object_type": "PlantEquipmentOperation:CoolingLoad",
                        "control_scheme_2_schedule_name": "HVACTemplate-Always1"
                    }
                },
                "PlantEquipmentOperation:CoolingLoad": {
                    "Only Water Loop Cool Operation All Hours": {
                        "load_range_1_lower_limit": 0,
                        "load_range_1_upper_limit": 1000000000000000,
                        "range_1_equipment_list_name": "Only Water Loop Cooling All Equipment"
                    }
                },
                "PlantEquipmentOperation:HeatingLoad": {
                    "Only Water Loop Heat Operation All Hours": {
                        "load_range_1_lower_limit": 0,
                        "load_range_1_upper_limit": 1000000000000000,
                        "range_1_equipment_list_name": "Only Water Loop Heating All Equipment"
                    }
                }
            }
        )
        self.base_epjson['HVACTemplate:Plant:MixedWaterLoop']['Only Water Loop'][
            'operation_scheme_type'] = 'UserDefined'
        self.base_epjson['HVACTemplate:Plant:MixedWaterLoop']['Only Water Loop'][
            'equipment_operation_schemes_name'] = 'Only Water Loop Operation Custom'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output['PlantEquipmentOperationSchemes'].get('Only Water Loop Operation Custom'))
        return

    def test_setpoint_schedule_name(self):
        self.ej.merge_epjson(
            super_dictionary=self.base_epjson,
            object_dictionary=schedule_objects)
        self.base_epjson['HVACTemplate:Plant:MixedWaterLoop']['Only Water Loop'][
            'high_temperature_setpoint_schedule_name'] = 'Always33'
        self.base_epjson['HVACTemplate:Plant:MixedWaterLoop']['Only Water Loop'][
            'low_temperature_setpoint_schedule_name'] = 'Always21'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'Always21',
            epjson_output['SetpointManager:Scheduled:DualSetpoint']['Only Water Loop Temp Manager'][
                'low_setpoint_schedule_name'])
        self.assertEqual(
            'Always33',
            epjson_output['SetpointManager:Scheduled:DualSetpoint']['Only Water Loop Temp Manager'][
                'high_setpoint_schedule_name'])
        return

    def test_design_setpoint(self):
        self.ej.merge_epjson(
            super_dictionary=self.base_epjson,
            object_dictionary=schedule_objects)
        self.base_epjson['HVACTemplate:Plant:MixedWaterLoop']['Only Water Loop'][
            'high_temperature_design_setpoint'] = 33
        self.base_epjson['HVACTemplate:Plant:MixedWaterLoop']['Only Water Loop'][
            'low_temperature_design_setpoint'] = 21
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'HVACTemplate-Always21.0',
            epjson_output['SetpointManager:Scheduled:DualSetpoint']['Only Water Loop Temp Manager'][
                'low_setpoint_schedule_name'])
        self.assertEqual(
            'HVACTemplate-Always33.0',
            epjson_output['SetpointManager:Scheduled:DualSetpoint']['Only Water Loop Temp Manager'][
                'high_setpoint_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:PlantLoop:MixedWaterLoop:"
                                              "water_pump_configuration_variable_flow")
    def test_water_pump_configuration_variable_flow(self):
        self.base_epjson['HVACTemplate:Plant:MixedWaterLoop']['Only Water Loop'][
            'water_pump_configuration'] = 'VariableFlow'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output['Pump:VariableSpeed'].get('Only Water Loop Supply Pump'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:PlantLoop:MixedWaterLoop:"
                                              "water_pump_configuration_variable_flow")
    def test_water_pump_configuration_constant_flow(self):
        self.base_epjson['HVACTemplate:Plant:MixedWaterLoop']['Only Water Loop'][
            'water_pump_configuration'] = 'ConstantFlow'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output['Pump:ConstantSpeed'].get('Only Water Loop Supply Pump'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:PlantLoop:MixedWaterLoop:"
                                              "water_pump_rated_head")
    def test_water_pump_rated_head(self):
        self.base_epjson['HVACTemplate:Plant:MixedWaterLoop']['Only Water Loop'][
            'water_pump_rated_head'] = 19000
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            19000,
            epjson_output['Pump:ConstantSpeed']['Only Water Loop Supply Pump']['design_pump_head'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:PlantLoop:MixedWaterLoop:"
                                              "water_pump_type_single_pump")
    def test_water_pump_type_single_pump(self):
        self.base_epjson['HVACTemplate:Plant:MixedWaterLoop']['Only Water Loop'][
            'water_pump_type'] = 'SinglePump'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(
            epjson_output['Pump:ConstantSpeed'].get('Only Water Loop Supply Pump'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:PlantLoop:MixedWaterLoop:"
                                              "water_pump_type_pump_per_tower_or_boiler")
    def test_water_pump_type_pump_per_tower_or_boiler(self):
        self.base_epjson['HVACTemplate:Plant:MixedWaterLoop']['Only Water Loop'][
            'water_pump_configuration'] = 'ConstantFlow'
        self.base_epjson['HVACTemplate:Plant:MixedWaterLoop']['Only Water Loop'][
            'water_pump_type'] = 'PumpPerTowerOrBoiler'
        self.base_epjson['HVACTemplate:Plant:MixedWaterLoop']['Only Water Loop'][
            'water_pump_rated_head'] = 19000
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'Main Boiler MW Branch Pump',
            epjson_output['Branch']['Main Boiler MW Branch']['components'][0]['component_name'])
        self.assertEqual(
            'Main Boiler',
            epjson_output['Branch']['Main Boiler MW Branch']['components'][1]['component_name'])
        self.assertEqual(
            'Main Tower Branch Pump',
            epjson_output['Branch']['Main Tower Branch']['components'][0]['component_name'])
        self.assertEqual(
            'Main Tower',
            epjson_output['Branch']['Main Tower Branch']['components'][1]['component_name'])
        self.assertEqual(
            19000,
            epjson_output['Pump:ConstantSpeed']['Main Tower Branch Pump']['design_pump_head'])
        self.assertEqual(
            19000,
            epjson_output['Pump:ConstantSpeed']['Main Boiler MW Branch Pump']['design_pump_head'])
        return