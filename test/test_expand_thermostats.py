import unittest

from expand_objects.expand_objects import ExpandThermostat
import expand_objects.exceptions as eoe
from test import BaseTest


class TestExpandThermostats(BaseTest, unittest.TestCase):
    def setUp(self):
        return

    def teardown(self):
        return

    def test_check_templates_are_required(self):
        with self.assertRaises(TypeError):
            ExpandThermostat()
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Thermostat:Verify valid template object")
    def test_verify_good_template(self):
        template = {
            "All Zones": {
                "heating_setpoint_schedule_name": "Htg-SetP-Sch",
                "cooling_setpoint_schedule_name": "Clg-SetP-Sch"
            }
        }
        output = ExpandThermostat(template=template)
        self.assertEqual('All Zones', list(output.template.keys())[0])
        print(vars(output))
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Thermostat:Reject bad template object")
    def test_reject_bad_template(self):
        templates = {}
        with self.assertRaises(eoe.InvalidTemplateException):
            ExpandThermostat(template=templates)
        templates = []
        with self.assertRaises(TypeError):
            ExpandThermostat(template=templates)
        return
