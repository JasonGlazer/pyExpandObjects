import unittest

from expand_objects.hvac_template import HVACTemplate

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


class TestHVACTemplateObject(unittest.TestCase):
    def setUp(self):
        self.hvac_template = HVACTemplate()
        self.hvac_template.logger.setLevel('INFO')
        self.hvac_template.load_schema()
        return

    def tearDown(self):
        return

    def test_no_hvac_objects_returns_false(self):
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
        self.hvac_template.pre_process(self.hvac_template.input_epjson)
        self.assertTrue(self.hvac_template.input_epjson_is_valid)
        self.assertEqual(len(self.hvac_template.templates.keys()), 1)
        self.assertIn(
            'HVACTemplate:Thermostat',
            self.hvac_template.templates.keys())
        return

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
        self.hvac_template.pre_process(self.hvac_template.input_epjson)
        self.assertTrue(self.hvac_template.input_epjson_is_valid)
        self.assertEqual(len(self.hvac_template.templates['HVACTemplate:Thermostat'].keys()), 2)
        self.assertEqual(len(self.hvac_template.templates['HVACTemplate:Zone:IdealLoadsAirSystem'].keys()), 2)
        return

    def test_templates_thermostat_attribute_created(self):
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
        self.hvac_template.pre_process(self.hvac_template.input_epjson)
        self.assertTrue(self.hvac_template.input_epjson_is_valid)
        self.assertEqual(
            len(self.hvac_template.templates_thermostats['HVACTemplate:Thermostat'].keys()),
            2)
        return

    # todo_eo One test for each template type
