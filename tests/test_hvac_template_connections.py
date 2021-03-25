import unittest
from unittest.mock import MagicMock

from src.hvac_template import HVACTemplate
from src.hvac_template import InvalidTemplateException
from src.expand_objects import ExpandThermostat
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


class TestHVACTemplateObjectConnections(BaseTest, unittest.TestCase):
    """
    Methods and functions that connect HVACTemplate outputs
    """
    def setUp(self):
        self.hvac_template = HVACTemplate()
        self.hvac_template.logger.setLevel('INFO')
        self.hvac_template.load_schema()
        return

    def tearDown(self):
        return

    def test_retrieve_thermostat_template_from_zone_field(self):
        self.hvac_template.expanded_thermostats = self.hvac_template.expand_templates(
            templates={
                "HVACTemplate:Thermostat": {
                    "All Zones": {
                        "heating_setpoint_schedule_name": "Htg-SetP-Sch",
                        "cooling_setpoint_schedule_name": "Clg-SetP-Sch"
                    }
                }
            },
            expand_class=ExpandThermostat)
        thermostat_template = self.hvac_template.get_thermostat_template_from_zone_template(zone_template={
            "HVACTemplate:Zone:VAV": {
                "HVACTemplate:Zone:VAV 1": {
                    "template_thermostat_name": "All Zones"
                }
            }
        })
        self.assertEqual('All Zones', thermostat_template.template_name)
        return

    def test_return_none_thermostat_template_from_from_zone_when_field_missing(self):
        self.hvac_template.expanded_thermostats = self.hvac_template.expand_templates(
            templates={
                "HVACTemplate:Thermostat": {
                    "All Zones": {
                        "heating_setpoint_schedule_name": "Htg-SetP-Sch",
                        "cooling_setpoint_schedule_name": "Clg-SetP-Sch"
                    }
                }
            },
            expand_class=ExpandThermostat)
        thermostat_template = self.hvac_template.get_thermostat_template_from_zone_template(zone_template={
            "HVACTemplate:Zone:VAV": {
                "HVACTemplate:Zone:VAV 1": {
                    "field_1": "value_1"
                }
            }
        })
        self.assertIsNone(thermostat_template)
        return

    def test_thermostat_template_from_zone_field_reject_bad_input(self):
        self.hvac_template.expanded_thermostats = self.hvac_template.expand_templates(
            templates={
                "HVACTemplate:Thermostat": {
                    "All Zones": {
                        "heating_setpoint_schedule_name": "Htg-SetP-Sch",
                        "cooling_setpoint_schedule_name": "Clg-SetP-Sch"
                    }
                }
            },
            expand_class=ExpandThermostat)
        with self.assertRaises(InvalidTemplateException):
            self.hvac_template.get_thermostat_template_from_zone_template(zone_template={
                "HVACTemplate:Zone:VAV": {
                    "HVACTemplate:Zone:VAV 1": {
                        "template_thermostat_name": "Bad Name"
                    }
                }
            })
        return

    def test_create_zonecontrol_thermostat_dualsetpoint(self):
        self.hvac_template.get_thermostat_template_from_zone_template = MagicMock()
        self.hvac_template.get_thermostat_template_from_zone_template.return_value.epjson = {
            "ThermostatSetpoint:DualSetpoint": {
                "All Zones SP Control": {
                    "cooling_setpoint_temperature_schedule_name": "Clg-SetP-Sch",
                    "heating_setpoint_temperature_schedule_name": "Htg-SetP-Sch"
                }
            }
        }
        self.hvac_template.create_zonecontrol_thermostat(zone_template={
            "HVACTemplate:Zone:VAV": {
                "HVACTemplate:Zone:VAV 1": {
                    "zone_name": "TEST ZONE"
                }
            }
        })
        self.assertEqual(
            'ThermostatSetpoint:DualSetpoint',
            self.hvac_template.epjson['ZoneControl:Thermostat']['TEST ZONE Thermostat']['control_1_object_type'])
        self.assertEqual(
            'HVACTemplate-Always4',
            list(self.hvac_template.epjson['Schedule:Compact'].keys())[0])
        return

    def test_create_zonecontrol_thermostat_single_heating(self):
        self.hvac_template.get_thermostat_template_from_zone_template = MagicMock()
        self.hvac_template.get_thermostat_template_from_zone_template.return_value.epjson = {
            "ThermostatSetpoint:SingleHeating": {
                "All Zones SP Control": {
                    "setpoint_temperature_schedule_name": "Clg-SetP-Sch",
                }
            }
        }
        self.hvac_template.create_zonecontrol_thermostat(zone_template={
            "HVACTemplate:Zone:VAV": {
                "HVACTemplate:Zone:VAV 1": {
                    "zone_name": "TEST ZONE"
                }
            }
        })
        self.assertEqual(
            'ThermostatSetpoint:SingleHeating',
            self.hvac_template.epjson['ZoneControl:Thermostat']['TEST ZONE Thermostat']['control_1_object_type'])
        self.assertEqual(
            'HVACTemplate-Always1',
            list(self.hvac_template.epjson['Schedule:Compact'].keys())[0])
        return

    def test_create_zonecontrol_thermostat_single_cooling(self):
        self.hvac_template.get_thermostat_template_from_zone_template = MagicMock()
        self.hvac_template.get_thermostat_template_from_zone_template.return_value.epjson = {
            "ThermostatSetpoint:SingleCooling": {
                "All Zones SP Control": {
                    "setpoint_temperature_schedule_name": "Clg-SetP-Sch",
                }
            }
        }
        self.hvac_template.create_zonecontrol_thermostat(zone_template={
            "HVACTemplate:Zone:VAV": {
                "HVACTemplate:Zone:VAV 1": {
                    "zone_name": "TEST ZONE"
                }
            }
        })
        self.assertEqual(
            'ThermostatSetpoint:SingleCooling',
            self.hvac_template.epjson['ZoneControl:Thermostat']['TEST ZONE Thermostat']['control_1_object_type'])
        self.assertEqual(
            'HVACTemplate-Always2',
            list(self.hvac_template.epjson['Schedule:Compact'].keys())[0])
        return

    def test_exception_zonecontrol_thermostat_bad_thermostat(self):
        self.hvac_template.get_thermostat_template_from_zone_template = MagicMock()
        self.hvac_template.get_thermostat_template_from_zone_template.return_value.epjson = {
            "ThermostatSetpoint:BadThermostat": {
                "All Zones SP Control": {
                    "setpoint_temperature_schedule_name": "Clg-SetP-Sch",
                }
            }
        }
        with self.assertRaises(InvalidTemplateException):
            self.hvac_template.create_zonecontrol_thermostat(zone_template={
                "HVACTemplate:Zone:VAV": {
                    "HVACTemplate:Zone:VAV 1": {
                        "zone_name": "TEST ZONE"
                    }
                }
            })
        return

    def test_exception_create_zonecontrol_thermostat_no_thermostat(self):
        self.hvac_template.get_thermostat_template_from_zone_template = MagicMock()
        self.hvac_template.get_thermostat_template_from_zone_template.return_value.epjson = {}
        with self.assertRaises(InvalidTemplateException):
            self.hvac_template.create_zonecontrol_thermostat(zone_template={
                "HVACTemplate:Zone:VAV": {
                    "HVACTemplate:Zone:VAV 1": {
                        "zone_name": "TEST ZONE"
                    }
                }
            })
        return
