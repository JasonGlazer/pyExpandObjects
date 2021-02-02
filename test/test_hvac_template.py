
import unittest as ut

from expand_objects.hvac_template import HVACTemplate

minimum_objects_d = {
    "Building": {
        "Ref Bldg Medium Office New2004_v1.3_5.0": {
            "loads_convergence_tolerance_value": 0.04,
            "maximum_number_of_warmup_days": 25,
            "minimum_number_of_warmup_days": 6,
            "north_axis": 0.0,
            "solar_distribution": "FullInteriorAndExterior",
            "temperature_convergence_tolerance_value": 0.2,
            "terrain": "City"
        }
    },
    "GlobalGeometryRules": {
        "GlobalGeometryRules 1": {
            "coordinate_system": "Relative",
            "daylighting_reference_point_coordinate_system": "Relative",
            "starting_vertex_position": "UpperLeftCorner",
            "vertex_entry_direction": "Counterclockwise"

        }
    }
}

class TestHVACTemplateObject(ut.TestCase):
    def setUp(self):
        self.logger_name = 'console_logger'
        self.hvac_template = HVACTemplate(logger_name = self.logger_name)
        self.hvac_template.logger.setLevel('ERROR')
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
        self.assertTrue(self.hvac_template.epjson_is_valid)
        self.assertFalse(self.hvac_template.templates_exist)
        self.assertIsNone(self.hvac_template.templates)
        return

    def test_one_hvac_object_one_template_returns_true(self):
        self.hvac_template.load_epjson({
            **minimum_objects_d,
            "HVACTemplate:Thermostat": {
                "All Zones": {
                    "heating_setpoint_schedule_name":"Htg-SetP-Sch",
                    "cooling_setpoint_schedule_name":"Clg-SetP-Sch"
                }
            }
        })
        self.hvac_template.check_epjson_for_templates(self.hvac_template.input_epjson)
        self.assertTrue(self.hvac_template.epjson_is_valid)
        self.assertTrue(self.hvac_template.templates_exist)
        self.assertEqual(len(self.hvac_template.templates[0]['HVACTemplate:Thermostat'].keys()), 1)
        return

    def test_n_hvac_objects_one_template_returns_true(self):
        self.hvac_template.load_epjson({
            **minimum_objects_d,
            "HVACTemplate:Thermostat": {
                "All Zones": {
                    "heating_setpoint_schedule_name":"Htg-SetP-Sch",
                    "cooling_setpoint_schedule_name":"Clg-SetP-Sch"
                },
                "All Zones 2": {
                    "heating_setpoint_schedule_name":"Htg-SetP-Sch",
                    "cooling_setpoint_schedule_name":"Clg-SetP-Sch"
                }
            }
        })
        self.hvac_template.check_epjson_for_templates(self.hvac_template.input_epjson)
        self.assertTrue(self.hvac_template.epjson_is_valid)
        self.assertTrue(self.hvac_template.templates_exist)
        self.assertEqual(len(self.hvac_template.templates[0]['HVACTemplate:Thermostat'].keys()), 2)
        return

    def test_n_hvac_objects_n_templates_returns_true(self):
        # Consult on how to properaly build HVACTemplate:zone:IdealLoadsAirSystem
        # the keys were created to make it work with epjson but do not exist in
        # the idf or schema definition.
        self.hvac_template.load_epjson({
            **minimum_objects_d,
            "HVACTemplate:Thermostat": {
                "All Zones": {
                    "heating_setpoint_schedule_name":"Htg-SetP-Sch",
                    "cooling_setpoint_schedule_name":"Clg-SetP-Sch"
                },
                "All Zones 2": {
                    "heating_setpoint_schedule_name":"Htg-SetP-Sch",
                    "cooling_setpoint_schedule_name":"Clg-SetP-Sch"
                },
            },
            "HVACTemplate:Zone:IdealLoadsAirSystem" : {
                "first_zone" : {"zone_name" : "Zone 1"},
                "second_zone" : {"zone_name" : "Zone 2"}
            }
        })
        self.hvac_template.check_epjson_for_templates(self.hvac_template.input_epjson)
        self.assertTrue(self.hvac_template.epjson_is_valid)
        self.assertTrue(self.hvac_template.templates_exist)
        # Can't reference by order for this test [0].  Rework
        #self.assertEqual(len(self.hvac_template.templates[0]['HVACTemplate:Thermostat'].keys()), 2)
        return
