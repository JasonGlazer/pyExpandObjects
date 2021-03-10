import unittest
import os
from functools import wraps

from expand_objects.hvac_template import HVACTemplate
from expand_objects.logger import Logger

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
        self.doc_text = None
        self.func_name = None
        self.func_status = None
        self.hvac_template = HVACTemplate()
        self.hvac_template.logger.setLevel('ERROR')
        self.hvac_template.load_schema()
        self.testing_logger = Logger(logger_name='testing_logger').logger
        return

    def tearDown(self):
        # write csv formatted output for processing
        if self.doc_text and self.func_name:
            try:
                self.testing_logger.info(
                    '%s, %s, %s, %s',
                    self.doc_text,
                    os.path.basename(__file__),
                    self.func_name,
                    self.func_status)
            except AttributeError:
                pass

    def _test_logger(doc_text="General"):
        """
        Wrapper that sets class variables for csv output
        :param doc_text: section for documentation file

        :return: class variable status indicators
            doc_text: section for documentation file
            func_name: name of function called
            func_status: boolean of function return
        """
        def _test_logger_wrapper(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                self.doc_text = doc_text
                self.func_name = func.__name__
                self.func_status = True
                # change func_status to false if an assertion was raised
                try:
                    return func(self, *args, **kwargs)
                except AssertionError as e:
                    self.assertEqual(e, e)
                    self.func_status = False
                    return func(self, *args, **kwargs)
            # make output the called function for unittest to work
            _test_logger_wrapper.__wrapped__ = func
            return wrapper
        return _test_logger_wrapper

    @_test_logger(doc_text="HVACTemplate:Base:NoTemplatesReturnFlag")
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
        self.assertFalse(self.hvac_template.templates_exist)
        self.assertIsNone(self.hvac_template.templates)
        return

    @_test_logger()
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
        self.hvac_template.check_epjson_for_templates(self.hvac_template.input_epjson)
        self.assertTrue(self.hvac_template.input_epjson_is_valid)
        self.assertTrue(self.hvac_template.templates_exist)
        self.assertEqual(len(self.hvac_template.templates.keys()), 1)
        return

    def test_n_hvac_objects_one_template_returns_true(self):
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
        self.hvac_template.check_epjson_for_templates(self.hvac_template.input_epjson)
        self.assertTrue(self.hvac_template.input_epjson_is_valid)
        self.assertTrue(self.hvac_template.templates_exist)
        self.assertEqual(len(self.hvac_template.templates['HVACTemplate:Thermostat'].keys()), 2)
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
        self.hvac_template.check_epjson_for_templates(self.hvac_template.input_epjson)
        self.assertTrue(self.hvac_template.input_epjson_is_valid)
        self.assertTrue(self.hvac_template.templates_exist)
        self.assertEqual(len(self.hvac_template.templates['HVACTemplate:Thermostat'].keys()), 2)
        self.assertEqual(len(self.hvac_template.templates['HVACTemplate:Thermostat'].keys()), 2)
        return

    def test_thermostat_template_object_created(self):
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
            }
        })
        self.hvac_template.check_epjson_for_templates(self.hvac_template.input_epjson)
        self.assertEqual(len(self.hvac_template.templates_thermostat.keys()), 2)
        return

    def test_return_object_from_schema(self):
        epjson_obj = self.hvac_template.get_object_from_schema("ThermostatSetpoint:DualSetpoint")
        self.assertIn('heating_setpoint_temperature_schedule_name', epjson_obj.keys())
        self.assertIn('cooling_setpoint_temperature_schedule_name', epjson_obj.keys())
        return

    def test_build_good_object_returns_valid_epjson(self):
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
            }
        })
        self.hvac_template.check_epjson_for_templates(self.hvac_template.input_epjson)
        target_object = self.hvac_template.populate_object_from_object(
            source_objects=self.hvac_template.templates_thermostat,
            target_object_name="ThermostatSetpoint:DualSetpoint",
            transitions={
                "heating_setpoint_schedule_name": "heating_setpoint_temperature_schedule_name",
                "cooling_setpoint_schedule_name": "cooling_setpoint_temperature_schedule_name"
            },
            name_append='thermostat'
        )
        valid_epjson = self.hvac_template._validate_epjson({
            **minimum_objects_d,
            **{"ThermostatSetpoint:DualSetpoint": target_object}
        })
        self.assertTrue(valid_epjson)
        return

    def test_build_bad_object_returns_invalid(self):
        # make test where these keys are wrong
        # transitions={
        #     "wrong_heating_setpoint_schedule_name": "heating_setpoint_temperature_schedule_name",
        #     "wrong_cooling_setpoint_schedule_name": "cooling_setpoint_temperature_schedule_name"}

        # also, populate_object_from_object sets the keys without checking they exist, which should
        # not be allowed
        return
