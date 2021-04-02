import unittest

from src.expand_objects import ExpandSystem
from . import BaseTest

mock_template = template = {
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

mock_build_path = [
    {
        'OutdoorAir:Mixer': {
            'Fields': {
                'name': '{} OA Mixing Box',
                'mixed_air_node_name': '{} Mixed Air Outlet',
                'outdoor_air_stream_node_name': '{} Outside Air Inlet',
                'relief_air_stream_node_name': '{} Relief Air Outlet',
                'return_air_stream_node_name': '{} Air Loop Inlet'
            },
            'Connectors': {
                'AirLoop': {
                    'Inlet': 'outdoor_air_stream_node_name',
                    'Outlet': 'mixed_air_node_name'
                }
            }
        }
    },
    {
        'Fan:VariableVolume': {
            'Fields': {
                'name': '{} Supply Fan',
                'air_inlet_node_name': '{} Supply Fan Inlet',
                'air_outlet_node_name': '{} Supply Fan Outlet'
            },
            'Connectors': {
                'AirLoop': {
                    'Inlet': 'air_inlet_node_name',
                    'Outlet': 'air_outlet_node_name'
                }
            }
        }
    }
]


class TestExpandSystem(BaseTest, unittest.TestCase):
    def setUp(self):
        return

    def teardown(self):
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:System:Input Template Required")
    def test_check_templates_are_required(self):
        with self.assertRaises(TypeError):
            ExpandSystem()
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:System:Verify valid template object")
    def test_verify_good_template(self):
        output = ExpandSystem(template=mock_template)
        self.assertEqual('VAV Sys 1', list(output.template.keys())[0])
        return

    def test_create_water_controller_list_from_epjson(self):
        es = ExpandSystem(template=mock_template)
        controllerlist = es._create_controller_list_from_epjson(epjson={
            'Controller:WaterCoil': {
                'test cooling water coil': {
                    'sensor_node_name': {
                        '^Coil:Cooling:Water': 'air_outlet_node_name'
                    },
                    'actuator_node_name': {
                        '^Coil:Cooling:Water': 'water_inlet_node_name'
                    }
                },
                'test heating water coil': {
                    'sensor_node_name': {
                        '^Coil:Heating:Water': 'air_outlet_node_name'
                    },
                    'actuator_node_name': {
                        '^Coil:Heating:Water': 'water_inlet_node_name'
                    }
                }
            }
        })
        self.assertEqual('AirLoopHVAC:ControllerList', list(controllerlist.keys())[0])
        self.assertEqual(
            'test cooling water coil',
            controllerlist['AirLoopHVAC:ControllerList']['VAV Sys 1 Controllers']['controller_1_name'])
        self.assertEqual(
            'test heating water coil',
            controllerlist['AirLoopHVAC:ControllerList']['VAV Sys 1 Controllers']['controller_2_name'])
        return

    # todo_eo: system objects to create: Controller:WaterCoil, Controller:OutdoorAir,
    #  AirLoopHVAC:OutdoorAirSystem:EquipmentList, SupplyPath, ReturnPath

    # todo_eo: system objects need to have objects resolved, or _resolve_objects needs to be called later.