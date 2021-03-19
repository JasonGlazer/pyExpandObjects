import unittest

from src.hvac_template import HVACTemplate
from src.hvac_template import InvalidTemplateException
from . import BaseTest

minimum_objects_d = {
    "Building": {
        "Test Building": {}
    },
    "GlobalGeometryRules": {
        "GlobalGeometryRules 1": {
            "coordinate_system": "Relative",
            "starting_vertex_position": "UpperLeftCorner",
            "vertex_entry_direction": "Counterclockwise"
        }
    }
}


class TestHVACTemplateObject(BaseTest, unittest.TestCase):
    def setUp(self):
        self.hvac_template = HVACTemplate()
        self.hvac_template.logger.setLevel('INFO')
        self.hvac_template.load_schema()
        return

    def tearDown(self):
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Verify no input templates returns no class templates")
    def test_no_hvac_objects_returns_with_zero_templates(self):
        self.hvac_template.load_epjson({
            **minimum_objects_d,
            "Version": {
                "Version 1": {
                    "version_identifier": "9.4"
                }
            }
        })
        self.assertTrue(self.hvac_template.input_epjson_is_valid)
        self.assertEqual(0, len(self.hvac_template.templates))
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Verify non HVACTemplate objects are passed to base dictionary")
    def test_base_objects_are_stored(self):
        self.hvac_template.load_epjson({
            **minimum_objects_d,
            "HVACTemplate:Thermostat": {
                "All Zones": {
                    "heating_setpoint_schedule_name": "Htg-SetP-Sch",
                    "cooling_setpoint_schedule_name": "Clg-SetP-Sch"
                }
            }
        })
        self.hvac_template.hvac_template_process(self.hvac_template.input_epjson)
        self.assertTrue(self.hvac_template.input_epjson_is_valid)
        self.assertEqual(2, len(self.hvac_template.base_objects))
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Verify input templates returns class templates")
    def test_one_hvac_object_one_template_returns_true(self):
        self.hvac_template.load_epjson({
            **minimum_objects_d,
            "HVACTemplate:Thermostat": {
                "All Zones": {
                    "heating_setpoint_schedule_name": "Htg-SetP-Sch",
                    "cooling_setpoint_schedule_name": "Clg-SetP-Sch"
                }
            }
        })
        self.hvac_template.hvac_template_process(self.hvac_template.input_epjson)
        self.assertTrue(self.hvac_template.input_epjson_is_valid)
        self.assertEqual(len(self.hvac_template.templates.keys()), 1)
        self.assertIn(
            'HVACTemplate:Thermostat',
            self.hvac_template.templates.keys())
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Verify different templates returns "
                                    "correct class templates")
    def test_n_hvac_objects_n_templates_returns_true(self):
        self.hvac_template.load_epjson({
            **minimum_objects_d,
            "HVACTemplate:Thermostat": {
                "All Zones 1": {
                    "heating_setpoint_schedule_name": "Htg-SetP-Sch",
                    "cooling_setpoint_schedule_name": "Clg-SetP-Sch"
                },
                "All Zones 2": {
                    "heating_setpoint_schedule_name": "Htg-SetP-Sch",
                    "cooling_setpoint_schedule_name": "Clg-SetP-Sch"
                },
            },
            "HVACTemplate:Zone:IdealLoadsAirSystem": {
                "HVACTemplate:Zone:IdealLoadsAirSystem 1": {"zone_name": "Zone 1"},
                "HVACTemplate:Zone:IdealLoadsAirSystem 2": {"zone_name": "Zone 2"}
            }
        })
        self.hvac_template.hvac_template_process(self.hvac_template.input_epjson)
        self.assertTrue(self.hvac_template.input_epjson_is_valid)
        self.assertEqual(len(self.hvac_template.templates['HVACTemplate:Thermostat'].keys()), 2)
        self.assertEqual(len(self.hvac_template.templates['HVACTemplate:Zone:IdealLoadsAirSystem'].keys()), 2)
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Verify thermostat class templates created")
    def test_thermostat_templates_have_good_objects(self):
        self.hvac_template.load_epjson({
            **minimum_objects_d,
            "HVACTemplate:Thermostat": {
                "All Zones": {
                    "heating_setpoint_schedule_name": "Htg-SetP-Sch",
                    "cooling_setpoint_schedule_name": "Clg-SetP-Sch"
                },
                "All Zones 2": {
                    "heating_setpoint_schedule_name": "Htg-SetP-Sch",
                    "cooling_setpoint_schedule_name": "Clg-SetP-Sch"
                }
            }
        })
        self.hvac_template.hvac_template_process(self.hvac_template.input_epjson)
        self.assertTrue(self.hvac_template.input_epjson_is_valid)
        template_check = True
        for template_type in self.hvac_template.templates_systems.keys():
            if template_type not in ['HVACTemplate:Thermostat', ]:
                template_check = False
        self.assertTrue(template_check)
        self.assertEqual(
            "Htg-SetP-Sch",
            self.hvac_template.templates_thermostats['HVACTemplate:Thermostat']
            ["All Zones"]["heating_setpoint_schedule_name"])
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Verify thermostat class templates created")
    def test_thermostat_bad_templates_raise_error(self):
        self.hvac_template.load_epjson({
            **minimum_objects_d,
            "HVACTemplate:Thermostattttttttttttttt": {
                "All Zones": {
                    "heating_setpoint_schedule_name": "Htg-SetP-Sch",
                    "cooling_setpoint_schedule_name": "Clg-SetP-Sch"
                },
                "All Zones 2": {
                    "heating_setpoint_schedule_name": "Htg-SetP-Sch",
                    "cooling_setpoint_schedule_name": "Clg-SetP-Sch"
                }
            }
        })
        with self.assertRaises(InvalidTemplateException):
            self.hvac_template.hvac_template_process(self.hvac_template.input_epjson)
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Verify zone class templates created")
    def test_zone_templates_have_good_objects(self):
        self.hvac_template.load_epjson({
            **minimum_objects_d,
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
                },
                "HVACTemplate:Zone:VAV 2": {
                    "baseboard_heating_capacity": "Autosize",
                    "baseboard_heating_type": "None",
                    "constant_minimum_air_flow_fraction": 0.3,
                    "damper_heating_action": "Reverse",
                    "outdoor_air_flow_rate_per_person": 0.00944,
                    "outdoor_air_flow_rate_per_zone": 0.0,
                    "outdoor_air_flow_rate_per_zone_floor_area": 0.0,
                    "outdoor_air_method": "Flow/Person",
                    "reheat_coil_type": "None",
                    "supply_air_maximum_flow_rate": "Autosize",
                    "template_thermostat_name": "All Zones",
                    "template_vav_system_name": "VAV Sys 1",
                    "zone_cooling_design_supply_air_temperature_input_method": "SystemSupplyAirTemperature",
                    "zone_heating_design_supply_air_temperature": 50.0,
                    "zone_heating_design_supply_air_temperature_input_method": "SupplyAirTemperature",
                    "zone_minimum_air_flow_input_method": "Constant",
                    "zone_name": "SPACE2-1"
                }
            },
            "HVACTemplate:Zone:FanCoil": {
                "HVACTemplate:Zone:FanCoil 1": {
                    "cooling_coil_design_setpoint": 12.5,
                    "cooling_coil_type": "ChilledWater",
                    "heating_coil_design_setpoint": 50,
                    "heating_coil_type": "HotWater",
                    "outdoor_air_flow_rate_per_person": 0.00944,
                    "outdoor_air_flow_rate_per_zone": 0.0,
                    "outdoor_air_flow_rate_per_zone_floor_area": 0.0,
                    "outdoor_air_method": "Flow/Person",
                    "supply_air_maximum_flow_rate": "Autosize",
                    "supply_fan_delta_pressure": 75,
                    "supply_fan_motor_efficiency": 0.9,
                    "supply_fan_motor_in_air_stream_fraction": 1,
                    "supply_fan_total_efficiency": 0.7,
                    "system_availability_schedule_name": "FanAvailSched",
                    "template_thermostat_name": "All Zones",
                    "zone_cooling_design_supply_air_temperature_input_method": "SupplyAirTemperature",
                    "zone_heating_design_supply_air_temperature_input_method": "SupplyAirTemperature",
                    "zone_name": "SPACE1-1"
                }
            }
        })
        self.hvac_template.hvac_template_process(self.hvac_template.input_epjson)
        self.assertTrue(self.hvac_template.input_epjson_is_valid)
        template_check = True
        for template_type in self.hvac_template.templates_zones.keys():
            if template_type not in ['HVACTemplate:Zone:VAV', 'HVACTemplate:Zone:FanCoil']:
                template_check = False
        self.assertTrue(template_check)
        self.assertEqual(
            "HotWater",
            self.hvac_template.templates_zones['HVACTemplate:Zone:VAV']
            ["HVACTemplate:Zone:VAV 1"]["reheat_coil_type"])
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Verify system class templates created")
    def test_system_templates_have_good_objects(self):
        self.hvac_template.load_epjson({
            **minimum_objects_d,
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
            },
            "HVACTemplate:System:UnitarySystem": {
                "Sys 1 Furnace DX Cool SnglSpd": {
                    "control_type": "Load",
                    "control_zone_or_thermostat_location_name": "SPACE1-1",
                    "cooling_coil_type": "SingleSpeedDX",
                    "cooling_design_supply_air_temperature": 12.8,
                    "cooling_supply_air_flow_rate": "Autosize",
                    "dehumidification_control_type": "None",
                    "dehumidification_relative_humidity_setpoint": 60,
                    "dx_cooling_coil_gross_rated_cop": 3,
                    "dx_cooling_coil_gross_rated_sensible_heat_ratio": "Autosize",
                    "dx_cooling_coil_gross_rated_total_capacity": "Autosize",
                    "economizer_lockout": "LockoutWithCompressor",
                    "economizer_maximum_limit_dry_bulb_temperature": 20,
                    "economizer_type": "DifferentialDryBulb",
                    "gas_heating_coil_efficiency": 0.8,
                    "heat_pump_defrost_maximum_outdoor_dry_bulb_temperature": 5,
                    "heat_pump_heating_coil_gross_rated_cop": 2.75,
                    "heat_pump_heating_minimum_outdoor_dry_bulb_temperature": -8,
                    "heat_recovery_frost_control_type": "None",
                    "heat_recovery_heat_exchanger_type": "Plate",
                    "heat_recovery_type": "None",
                    "heating_coil_gross_rated_capacity": "Autosize",
                    "heating_coil_type": "Gas",
                    "heating_design_supply_air_temperature": 50,
                    "heating_supply_air_flow_rate": "Autosize",
                    "humidifier_rated_capacity": 1e-06,
                    "humidifier_rated_electric_power": "Autosize",
                    "humidifier_relative_humidity_setpoint": 30,
                    "humidifier_type": "None",
                    "latent_heat_recovery_effectiveness": 0.65,
                    "maximum_outdoor_air_flow_rate": "Autosize",
                    "minimum_outdoor_air_flow_rate": "Autosize",
                    "minimum_outdoor_air_schedule_name": "Min OA Sched",
                    "no_load_supply_air_flow_rate": "Autosize",
                    "number_of_speeds_for_cooling": 1,
                    "number_of_speeds_or_stages_for_heating": 1,
                    "return_fan": "No",
                    "return_fan_delta_pressure": 300,
                    "return_fan_motor_efficiency": 0.9,
                    "return_fan_motor_in_air_stream_fraction": 1,
                    "return_fan_total_efficiency": 0.7,
                    "sensible_heat_recovery_effectiveness": 0.7,
                    "sizing_option": "NonCoincident",
                    "supplemental_gas_heating_or_reheat_coil_efficiency": 0.8,
                    "supplemental_heating_or_reheat_coil_capacity": "Autosize",
                    "supplemental_heating_or_reheat_coil_maximum_outdoor_dry_bulb_temperature": 21,
                    "supplemental_heating_or_reheat_coil_type": "None",
                    "supply_fan_delta_pressure": 600,
                    "supply_fan_motor_efficiency": 0.9,
                    "supply_fan_motor_in_air_stream_fraction": 1,
                    "supply_fan_operating_mode_schedule_name": "FanAvailSched",
                    "supply_fan_placement": "BlowThrough",
                    "supply_fan_total_efficiency": 0.7
                }
            }
        })
        self.hvac_template.hvac_template_process(self.hvac_template.input_epjson)
        self.assertTrue(self.hvac_template.input_epjson_is_valid)
        template_check = True
        for template_type in self.hvac_template.templates_systems.keys():
            if template_type not in ['HVACTemplate:System:VAV', 'HVACTemplate:System:UnitarySystem']:
                template_check = False
        self.assertTrue(template_check)
        self.assertEqual(
            12.8,
            self.hvac_template.templates_systems['HVACTemplate:System:VAV']
            ["VAV Sys 1"]["cooling_coil_design_setpoint"])
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Verify plant loop class templates created")
    def test_plant_loop_templates_have_good_objects(self):
        self.hvac_template.load_epjson({
            **minimum_objects_d,
            "HVACTemplate:Plant:HotWaterLoop": {
                "HW Heating Loop": {
                    "demand_side_bypass_pipe": "Yes",
                    "fluid_type": "Water",
                    "hot_water_design_setpoint": 82,
                    "hot_water_plant_operation_scheme_type": "Default",
                    "hot_water_pump_configuration": "ConstantFlow",
                    "hot_water_pump_rated_head": 179352,
                    "hot_water_pump_type": "SinglePump",
                    "hot_water_reset_outdoor_dry_bulb_high": 10,
                    "hot_water_reset_outdoor_dry_bulb_low": -6.7,
                    "hot_water_setpoint_at_outdoor_dry_bulb_high": 65.6,
                    "hot_water_setpoint_at_outdoor_dry_bulb_low": 82.2,
                    "hot_water_setpoint_reset_type": "None",
                    "load_distribution_scheme": "SequentialLoad",
                    "loop_design_delta_temperature": 11,
                    "pump_control_type": "Intermittent",
                    "supply_side_bypass_pipe": "Yes"
                }
            },
            "HVACTemplate:Plant:ChilledWaterLoop": {
                "ChW Cooling Loop": {
                    "chilled_water_demand_side_bypass_pipe": "Yes",
                    "chilled_water_design_setpoint": 7.22,
                    "chilled_water_load_distribution_scheme": "SequentialLoad",
                    "chilled_water_primary_pump_type": "SinglePump",
                    "chilled_water_pump_configuration": "ConstantPrimaryNoSecondary",
                    "chilled_water_reset_outdoor_dry_bulb_high": 26.7,
                    "chilled_water_reset_outdoor_dry_bulb_low": 15.6,
                    "chilled_water_secondary_pump_type": "SinglePump",
                    "chilled_water_setpoint_at_outdoor_dry_bulb_high": 6.7,
                    "chilled_water_setpoint_at_outdoor_dry_bulb_low": 12.2,
                    "chilled_water_setpoint_reset_type": "None",
                    "chilled_water_supply_side_bypass_pipe": "Yes",
                    "chiller_plant_operation_scheme_type": "Default",
                    "condenser_plant_operation_scheme_type": "Default",
                    "condenser_water_demand_side_bypass_pipe": "Yes",
                    "condenser_water_design_setpoint": 29.4,
                    "condenser_water_load_distribution_scheme": "SequentialLoad",
                    "condenser_water_pump_rated_head": 179352,
                    "condenser_water_pump_type": "SinglePump",
                    "condenser_water_supply_side_bypass_pipe": "Yes",
                    "fluid_type": "Water",
                    "loop_design_delta_temperature": 6.67,
                    "primary_chilled_water_pump_rated_head": 179352,
                    "pump_control_type": "Intermittent",
                    "secondary_chilled_water_pump_rated_head": 179352
                }
            },
            "HVACTemplate:Plant:Boiler": {
                "Hot Water Loop Boiler": {
                    "boiler_type": "CondensingHotWaterBoiler",
                    "capacity": "Autosize",
                    "efficiency": 0.8,
                    "fuel_type": "NaturalGas",
                    "maximum_part_load_ratio": 1.1,
                    "optimum_part_load_ratio": 1,
                    "sizing_factor": 1,
                    "template_plant_loop_type": "HotWater",
                    "water_outlet_upper_temperature_limit": 100
                }
            },
            "HVACTemplate:Plant:Chiller": {
                "ChW Loop Chiller": {
                    "capacity": "Autosize",
                    "chiller_type": "ElectricReciprocatingChiller",
                    "condenser_type": "AirCooled",
                    "leaving_chilled_water_lower_temperature_limit": 5,
                    "maximum_part_load_ratio": 1,
                    "minimum_unloading_ratio": 0.25,
                    "nominal_cop": 3,
                    "optimum_part_load_ratio": 1,
                    "sizing_factor": 1
                }
            }
        })
        self.hvac_template.hvac_template_process(self.hvac_template.input_epjson)
        self.assertTrue(self.hvac_template.input_epjson_is_valid)
        template_check = True
        for template_type in self.hvac_template.templates_plant_loops.keys():
            if template_type not in ['HVACTemplate:Plant:HotWaterLoop', 'HVACTemplate:Plant:ChilledWaterLoop']:
                template_check = False
        self.assertTrue(template_check)
        self.assertEqual(
            7.22,
            self.hvac_template.templates_plant_loops['HVACTemplate:Plant:ChilledWaterLoop']
            ["ChW Cooling Loop"]["chilled_water_design_setpoint"])
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Verify plant equipment class templates created")
    def test_plant_equipment_templates_have_good_objects(self):
        self.hvac_template.load_epjson({
            **minimum_objects_d,
            "HVACTemplate:Plant:HotWaterLoop": {
                "HW Heating Loop": {
                    "demand_side_bypass_pipe": "Yes",
                    "fluid_type": "Water",
                    "hot_water_design_setpoint": 82,
                    "hot_water_plant_operation_scheme_type": "Default",
                    "hot_water_pump_configuration": "ConstantFlow",
                    "hot_water_pump_rated_head": 179352,
                    "hot_water_pump_type": "SinglePump",
                    "hot_water_reset_outdoor_dry_bulb_high": 10,
                    "hot_water_reset_outdoor_dry_bulb_low": -6.7,
                    "hot_water_setpoint_at_outdoor_dry_bulb_high": 65.6,
                    "hot_water_setpoint_at_outdoor_dry_bulb_low": 82.2,
                    "hot_water_setpoint_reset_type": "None",
                    "load_distribution_scheme": "SequentialLoad",
                    "loop_design_delta_temperature": 11,
                    "pump_control_type": "Intermittent",
                    "supply_side_bypass_pipe": "Yes"
                }
            },
            "HVACTemplate:Plant:ChilledWaterLoop": {
                "ChW Cooling Loop": {
                    "chilled_water_demand_side_bypass_pipe": "Yes",
                    "chilled_water_design_setpoint": 7.22,
                    "chilled_water_load_distribution_scheme": "SequentialLoad",
                    "chilled_water_primary_pump_type": "SinglePump",
                    "chilled_water_pump_configuration": "ConstantPrimaryNoSecondary",
                    "chilled_water_reset_outdoor_dry_bulb_high": 26.7,
                    "chilled_water_reset_outdoor_dry_bulb_low": 15.6,
                    "chilled_water_secondary_pump_type": "SinglePump",
                    "chilled_water_setpoint_at_outdoor_dry_bulb_high": 6.7,
                    "chilled_water_setpoint_at_outdoor_dry_bulb_low": 12.2,
                    "chilled_water_setpoint_reset_type": "None",
                    "chilled_water_supply_side_bypass_pipe": "Yes",
                    "chiller_plant_operation_scheme_type": "Default",
                    "condenser_plant_operation_scheme_type": "Default",
                    "condenser_water_demand_side_bypass_pipe": "Yes",
                    "condenser_water_design_setpoint": 29.4,
                    "condenser_water_load_distribution_scheme": "SequentialLoad",
                    "condenser_water_pump_rated_head": 179352,
                    "condenser_water_pump_type": "SinglePump",
                    "condenser_water_supply_side_bypass_pipe": "Yes",
                    "fluid_type": "Water",
                    "loop_design_delta_temperature": 6.67,
                    "primary_chilled_water_pump_rated_head": 179352,
                    "pump_control_type": "Intermittent",
                    "secondary_chilled_water_pump_rated_head": 179352
                }
            },
            "HVACTemplate:Plant:Boiler": {
                "Hot Water Loop Boiler": {
                    "boiler_type": "CondensingHotWaterBoiler",
                    "capacity": "Autosize",
                    "efficiency": 0.8,
                    "fuel_type": "NaturalGas",
                    "maximum_part_load_ratio": 1.1,
                    "optimum_part_load_ratio": 1,
                    "sizing_factor": 1,
                    "template_plant_loop_type": "HotWater",
                    "water_outlet_upper_temperature_limit": 100
                }
            },
            "HVACTemplate:Plant:Chiller": {
                "ChW Loop Chiller": {
                    "capacity": "Autosize",
                    "chiller_type": "ElectricReciprocatingChiller",
                    "condenser_type": "AirCooled",
                    "leaving_chilled_water_lower_temperature_limit": 5,
                    "maximum_part_load_ratio": 1,
                    "minimum_unloading_ratio": 0.25,
                    "nominal_cop": 3,
                    "optimum_part_load_ratio": 1,
                    "sizing_factor": 1
                }
            }
        })
        self.hvac_template.hvac_template_process(self.hvac_template.input_epjson)
        self.assertTrue(self.hvac_template.input_epjson_is_valid)
        template_check = True
        for template_type in self.hvac_template.templates_plant_equipment.keys():
            if template_type not in ['HVACTemplate:Plant:Chiller', 'HVACTemplate:Plant:Boiler']:
                template_check = False
        self.assertTrue(template_check)
        self.assertEqual(
            5,
            self.hvac_template.templates_plant_equipment['HVACTemplate:Plant:Chiller']
            ["ChW Loop Chiller"]["leaving_chilled_water_lower_temperature_limit"])
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Validate Thermostat template processing")
    def test_thermostat_processing(self):
        self.hvac_template.load_epjson({
            **minimum_objects_d,
            "HVACTemplate:Thermostat": {
                "All Zones": {
                    "heating_setpoint_schedule_name": "Htg-SetP-Sch",
                    "cooling_setpoint_schedule_name": "Clg-SetP-Sch"
                },
                "All Zones 2": {
                    "heating_setpoint_schedule_name": "Htg-SetP-Sch",
                    "cooling_setpoint_schedule_name": "Clg-SetP-Sch"
                }
            }
        })
        epjson = self.hvac_template.run(self.hvac_template.input_epjson)
        name_check = True
        object_check = True
        outputs = self.hvac_template.unpack_epjson(epjson['epJSON'])
        if len([i for i in outputs]) == 0:
            name_check = False
            object_check = False
        for output in outputs:
            (name, _), = output.items()
            if name not in ['All Zones SP Control', 'All Zones 2 SP Control',
                            'Test Building', 'GlobalGeometryRules 1']:
                name_check = False
        self.assertTrue(name_check)
        for object_type in epjson.keys():
            if object_type not in ['HVACTemplate:Thermostat', 'Building',
                                   'GlobalGeometryRules', 'outputPreProcessorMessage', 'epJSON']:
                object_check = False
        self.assertTrue(object_check)
        return