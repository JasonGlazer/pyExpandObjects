from pathlib import Path

from tests.simulations import BaseSimulationTest
from src.epjson_handler import EPJSON

test_dir = Path(__file__).parent.parent.parent

design_specification_objects = {
    "DesignSpecification:OutdoorAir": {
        "SPACE1-1 SZ DSOA Custom Object": {
            "outdoor_air_flow_per_zone": 0.01,
            "outdoor_air_method": "Flow/Zone"
        }
    },
    "DesignSpecification:ZoneAirDistribution": {
        "SPACE1-1 SZ DSZAD Custom Object": {}
    }
}

hot_water_loop_objects = {
    "HVACTemplate:Plant:Boiler": {
        "Main Boiler": {
            "boiler_type": "HotWaterBoiler",
            "capacity": "Autosize",
            "efficiency": 0.8,
            "fuel_type": "NaturalGas",
            "priority": "1"
        }
    },
    "HVACTemplate:Plant:HotWaterLoop": {
        "Hot Water Loop": {
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


class TestSimulationsZonePTHP(BaseSimulationTest):
    def setUp(self):
        self.ej = EPJSON()
        base_idf_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles', 'HVACTemplate-5ZonePTHP.idf')
        base_copy_file_path = self._copy_to_test_directory(base_idf_file_path)
        # read in base file, then edit inputs for alternate tests
        self.base_epjson = self.get_epjson_object_from_idf_file(base_copy_file_path)
        return

    def teardown(self):
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:PTHP:cooling_supply_air_flow_rate")
    def test_cooling_supply_air_flow_rate(self):
        # todo_eo: ZoneHVAC:EquipmentConnections and ZoneHVAC:PackagedTerminalAirConditioner cooling_supply_air_flow_rate
        #  are not set in legacy with these inputs which is causing the discrepancy.
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1']['cooling_supply_air_flow_rate'] = 0.1
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.1,
            epjson_output['ZoneHVAC:PackagedTerminalHeatPump']['SPACE1-1 PTHP']['cooling_supply_air_flow_rate'])
        self.assertEqual(
            0.1,
            epjson_output['Sizing:Zone']['SPACE1-1 Sizing Zone']['cooling_design_air_flow_rate'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:PTHP:cooling_supply_air_flow_rate")
    def test_heating_supply_air_flow_rate(self):
        # todo_eo: ZoneHVAC:EquipmentConnections and ZoneHVAC:PackagedTerminalAirConditioner heating_supply_air_flow_rate
        #  are not set in legacy with these inputs which can cause discrepancy.
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1']['heating_supply_air_flow_rate'] = 0.1
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.1,
            epjson_output['ZoneHVAC:PackagedTerminalAirConditioner']['SPACE1-1 PTHP']['heating_supply_air_flow_rate'])
        self.assertEqual(
            0.1,
            epjson_output['Sizing:Zone']['SPACE1-1 Sizing Zone']['heating_design_air_flow_rate'])
        self.assertEqual(
            0.1,
            epjson_output['ZoneHVAC:EquipmentConnections']['SPACE1-1 Equipment Connections']['heating_supply_air_flow_rate'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:PTHP:no_load_supply_air_flow_rate")
    def test_no_load_supply_air_flow_rate(self):
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1']['no_load_supply_air_flow_rate'] = 0.1
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.1,
            epjson_output['ZoneHVAC:PackagedTerminalHeatPump']['SPACE1-1 PTHP']['no_load_supply_air_flow_rate'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:PTHP:zone_heating_sizing_factor")
    def test_zone_heating_sizing_factor(self):
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1']['zone_heating_sizing_factor'] = 1.2
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            1.2,
            epjson_output['Sizing:Zone']['SPACE1-1 Sizing Zone']['zone_heating_sizing_factor'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:PTHP:zone_cooling_sizing_factor")
    def test_zone_cooling_sizing_factor(self):
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1']['zone_cooling_sizing_factor'] = 1.2
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            1.2,
            epjson_output['Sizing:Zone']['SPACE1-1 Sizing Zone']['zone_cooling_sizing_factor'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:PTHP:outdoor_air_method_flow_per_person")
    def test_outdoor_air_method_flow_per_person(self):
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1'][
            'outdoor_air_method'] = 'Flow/Person'
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1'][
            'outdoor_air_flow_rate_per_person'] = 0.01
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'Flow/Person',
            epjson_output['DesignSpecification:OutdoorAir']['SPACE1-1 SZ DSOA']['outdoor_air_method'])
        self.assertEqual(
            0.01,
            epjson_output['DesignSpecification:OutdoorAir']['SPACE1-1 SZ DSOA']['outdoor_air_flow_per_person'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:PTHP:outdoor_air_method_flow_per_area")
    def test_outdoor_air_method_flow_per_area(self):
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1'][
            'outdoor_air_method'] = 'Flow/Area'
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1'][
            'outdoor_air_flow_rate_per_zone_floor_area'] = 0.0014
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'Flow/Area',
            epjson_output['DesignSpecification:OutdoorAir']['SPACE1-1 SZ DSOA']['outdoor_air_method'])
        self.assertEqual(
            0.0014,
            epjson_output['DesignSpecification:OutdoorAir']['SPACE1-1 SZ DSOA']['outdoor_air_flow_per_zone_floor_area'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:PTHP:outdoor_air_method_flow_per_zone")
    def test_outdoor_air_method_flow_per_zone(self):
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1'][
            'outdoor_air_method'] = 'Flow/Zone'
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1'][
            'outdoor_air_flow_rate_per_zone'] = 0.01
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'Flow/Zone',
            epjson_output['DesignSpecification:OutdoorAir']['SPACE1-1 SZ DSOA']['outdoor_air_method'])
        self.assertEqual(
            0.01,
            epjson_output['DesignSpecification:OutdoorAir']['SPACE1-1 SZ DSOA']['outdoor_air_flow_per_zone'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:PTHP:outdoor_air_method_detailed_specification")
    def test_outdoor_air_method_detailed_specification(self):
        self.ej.merge_epjson(
            super_dictionary=self.base_epjson,
            object_dictionary=design_specification_objects)
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1'][
            'outdoor_air_method'] = 'DetailedSpecification'
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1'][
            'design_specification_outdoor_air_object_name'] = 'SPACE1-1 SZ DSOA Custom Object'
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1'][
            'design_specification_zone_air_distribution_object_name'] = 'SPACE1-1 SZ DSZAD Custom Object'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output['DesignSpecification:OutdoorAir'].get('SPACE1-1 SZ DSOA Custom Object'))
        self.assertIsNotNone(epjson_output['DesignSpecification:ZoneAirDistribution'].get('SPACE1-1 SZ DSZAD Custom Object'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:PTHP:system_availability_schedule_name")
    def test_system_availability_schedule_name(self):
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1']['system_availability_schedule_name'] = 'OCCUPY-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['Fan:OnOff']['SPACE1-1 Supply Fan']['availability_schedule_name'])
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['ZoneHVAC:PackagedTerminalHeatPump']['SPACE1-1 PTHP']['availability_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:PTHP:supply_fan_operating_mode_schedule_name")
    def test_supply_fan_operating_mode_schedule_name(self):
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1']['supply_fan_operating_mode_schedule_name'] = 'OCCUPY-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['ZoneHVAC:PackagedTerminalHeatPump']['SPACE1-1 PTHP']['supply_air_fan_operating_mode_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:PTHP:supply_fan_placement")
    def test_supply_fan_placement(self):
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1']['supply_fan_placement'] = 'BlowThrough'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'BlowThrough',
            epjson_output['ZoneHVAC:PackagedTerminalHeatPump']['SPACE1-1 PTHP']['fan_placement'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:PTHP:supply_fan_total_efficiency")
    def test_supply_fan_total_efficiency(self):
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1']['supply_fan_total_efficiency'] = 0.65
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.65,
            epjson_output['Fan:OnOff']['SPACE1-1 Supply Fan']['fan_total_efficiency'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:PTHP:supply_fan_delta_pressure")
    def test_supply_fan_delta_pressure(self):
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1']['supply_fan_delta_pressure'] = 80
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            80,
            epjson_output['Fan:OnOff']['SPACE1-1 Supply Fan']['pressure_rise'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:PTHP:supply_fan_motor_efficiency")
    def test_supply_fan_motor_efficiency(self):
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1']['supply_fan_motor_efficiency'] = 0.8
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.8,
            epjson_output['Fan:OnOff']['SPACE1-1 Supply Fan']['motor_efficiency'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:PTHP:cooling_coil_availability_schedule_name")
    def test_cooling_coil_availability_schedule_name(self):
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1']['cooling_coil_availability_schedule_name'] = 'OCCUPY-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['Coil:Cooling:DX:SingleSpeed']['SPACE1-1 Cooling Coil']['availability_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:PTHP:cooling_coil_gross_rated_total_capacity")
    def test_cooling_coil_gross_rated_total_capacity(self):
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1']['cooling_coil_gross_rated_total_capacity'] = 1000
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            1000,
            epjson_output['Coil:Cooling:DX:SingleSpeed']['SPACE1-1 Cooling Coil']['gross_rated_total_cooling_capacity'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:PTHP:cooling_coil_gross_rated_sensible_heat_ratio")
    def test_cooling_coil_gross_rated_sensible_heat_ratio(self):
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1']['cooling_coil_gross_rated_sensible_heat_ratio'] = 0.65
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.65,
            epjson_output['Coil:Cooling:DX:SingleSpeed']['SPACE1-1 Cooling Coil']['gross_rated_sensible_heat_ratio'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:PTHP:cooling_coil_gross_rated_cop")
    def test_cooling_coil_gross_rated_cop(self):
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1']['cooling_coil_gross_rated_cop'] = 3.3
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            3.3,
            epjson_output['Coil:Cooling:DX:SingleSpeed']['SPACE1-1 Cooling Coil']['gross_rated_cooling_cop'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:PTHP:heating_coil_availability_schedule_name")
    def test_heating_coil_availability_schedule_name(self):
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1']['heat_pump_heating_coil_availability_schedule_name'] = 'OCCUPY-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['Coil:Heating:DX:SingleSpeed']['SPACE1-1 Heating Coil']['availability_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:PTHP:heat_pump_heating_coil_gross_rated_capacity")
    def test_heat_pump_heating_coil_gross_rated_capacity(self):
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1']['heat_pump_heating_coil_gross_rated_capacity'] = 1000
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            1000,
            epjson_output['Coil:Heating:DX:SingleSpeed']['SPACE1-1 Heating Coil']['gross_rated_heating_capacity'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:PTHP:heat_pump_heating_coil_gross_rated_cop")
    def test_heat_pump_heating_coil_gross_rated_cop(self):
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1']['heat_pump_heating_coil_gross_rated_cop'] = 2.6
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            2.6,
            epjson_output['Coil:Heating:DX:SingleSpeed']['SPACE1-1 Heating Coil']['gross_rated_heating_cop'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:PTHP:heat_pump_heating_minimum_outdoor_dry_bulb_temperature")
    def test_heat_pump_heating_minimum_outdoor_dry_bulb_temperature(self):
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1']['heat_pump_heating_minimum_outdoor_dry_bulb_temperature'] = -5
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            -5,
            epjson_output['Coil:Heating:DX:SingleSpeed']['SPACE1-1 Heating Coil']['minimum_outdoor_dry_bulb_temperature_for_compressor_operation'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:PTHP:heat_pump_defrost_maximum_outdoor_dry_bulb_temperature")
    def test_heat_pump_defrost_maximum_outdoor_dry_bulb_temperature(self):
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1']['heat_pump_defrost_maximum_outdoor_dry_bulb_temperature'] = 3
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            3,
            epjson_output['Coil:Heating:DX:SingleSpeed']['SPACE1-1 Heating Coil']['maximum_outdoor_dry_bulb_temperature_for_defrost_operation'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:PTHP:heat_pump_defrost_strategy")
    def test_heat_pump_defrost_strategy(self):
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1']['heat_pump_defrost_strategy'] = 'Resistive'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'Resistive',
            epjson_output['Coil:Heating:DX:SingleSpeed']['SPACE1-1 Heating Coil']['defrost_strategy'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:PTHP:heat_pump_defrost_control")
    def test_heat_pump_defrost_control(self):
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1']['heat_pump_defrost_control'] = 'OnDemand'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'OnDemand',
            epjson_output['Coil:Heating:DX:SingleSpeed']['SPACE1-1 Heating Coil']['defrost_control'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:PTHP:heat_pump_defrost_time_period_fraction")
    def test_heat_pump_defrost_time_period_fraction(self):
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1']['heat_pump_defrost_time_period_fraction'] = 0.07
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            0.07,
            epjson_output['Coil:Heating:DX:SingleSpeed']['SPACE1-1 Heating Coil']['defrost_time_period_fraction'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:PTHP:supplemental_heating_coil_type_electric")
    def test_supplemental_heating_coil_type_electric(self):
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1']['supplemental_heating_coil_type'] = 'Electric'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output['Coil:Heating:Electric'].get('SPACE1-1 Supp Heating Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:PTHP:supplemental_heating_coil_type_gas")
    def test_supplemental_heating_coil_type_gas(self):
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1']['supplemental_heating_coil_type'] = 'Gas'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output['Coil:Heating:Fuel'].get('SPACE1-1 Supp Heating Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:PTHP:supplemental_heating_coil_type_hot_water")
    def test_supplemental_heating_coil_type_hot_water(self):
        self.ej.merge_epjson(
            super_dictionary=self.base_epjson,
            object_dictionary=hot_water_loop_objects)
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1']['supplemental_heating_coil_type'] = 'HotWater'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertIsNotNone(epjson_output['Coil:Heating:Water'].get('SPACE1-1 Supp Heating Coil'))
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Zone:PTHP:supplemental_heating_coil_availability_schedule_name")
    def test_supplemental_heating_coil_availability_schedule_name(self):
        self.base_epjson['HVACTemplate:Zone:PTHP']['HVACTemplate:Zone:PTHP 1']['supplemental_heating_coil_availability_schedule_name'] = 'OCCUPY-1'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['Coil:Heating:Electric']['SPACE1-1 Supp Heating Coil']['availability_schedule_name'])
        return

