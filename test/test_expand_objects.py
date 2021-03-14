import unittest

from expand_objects.expand_objects import ExpandThermostats, InvalidTemplateException
from test import BaseTest


class TestExpandObjects(BaseTest, unittest.TestCase):
    def setUp(self):
        return

    def teardown(self):
        return

    def test_check_templates_are_required(self):
        with self.assertRaises(TypeError):
            ExpandThermostats()
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Thermostat:Verify valid template object")
    def test_verify_good_template(self):
        templates = {
            "HVACTemplate:Thermostat": {
                "All Zones": {
                    "heating_setpoint_schedule_name": "Htg-SetP-Sch",
                    "cooling_setpoint_schedule_name": "Clg-SetP-Sch"
                }
            }
        }
        output = ExpandThermostats(templates=templates)
        self.assertEqual('HVACTemplate:Thermostat', list(output.templates.keys())[0])
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Thermostat:Reject bad template object")
    def test_reject_bad_template(self):
        templates = {
            "HVACTemplate:Thermostatttttt": {
                "All Zones": {
                    "heating_setpoint_schedule_name": "Htg-SetP-Sch",
                    "cooling_setpoint_schedule_name": "Clg-SetP-Sch"
                }
            }
        }
        with self.assertRaises(InvalidTemplateException):
            ExpandThermostats(templates=templates)
        return

    def test_dictionary_required(self):
        templates = []
        with self.assertRaises(TypeError):
            ExpandThermostats(templates=templates)
        return
