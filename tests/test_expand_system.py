import unittest

from src.expand_objects import ExpandSystem
from . import BaseTest


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
        template = {
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
        output = ExpandSystem(template=template)
        self.assertEqual('VAV Sys 1', list(output.template.keys())[0])
        return
