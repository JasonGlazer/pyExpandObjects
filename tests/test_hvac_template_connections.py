import copy
import unittest
from unittest.mock import MagicMock, PropertyMock

from src.hvac_template import HVACTemplate
from src.hvac_template import InvalidTemplateException
from src.expand_objects import ExpandThermostat, ExpandSystem, ExpandObjects
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

mock_zone_epjson = {
    "AirTerminal:SingleDuct:VAV:Reheat": {
        "SPACE1-1 VAV Reheat": {
            "air_inlet_node_name": "SPACE1-1 Zone Equip Inlet",
            "air_outlet_node_name": "SPACE1-1 Supply Inlet"
        }
    },
    "ZoneHVAC:EquipmentConnections": {
        "ZoneHVAC:EquipmentConnections 1": {
            "zone_air_inlet_node_or_nodelist_name": "{} Supply Inlet",
            "zone_air_node_name": "{} Zone Air Node",
            "zone_conditioning_equipment_list_name": "{} Equipment",
            "zone_name": "{}",
            "zone_return_air_node_or_nodelist_name": "{} Return Outlet"
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
        self.hvac_template._load_schema()
        return

    def tearDown(self):
        return

    def test_retrieve_thermostat_template_from_zone_field(self):
        self.hvac_template.expanded_thermostats = self.hvac_template._expand_templates(
            templates={
                "HVACTemplate:Thermostat": {
                    "All Zones": {
                        "heating_setpoint_schedule_name": "Htg-SetP-Sch",
                        "cooling_setpoint_schedule_name": "Clg-SetP-Sch"
                    }
                }
            },
            expand_class=ExpandThermostat)
        thermostat_template = self.hvac_template._get_thermostat_template_from_zone_template(zone_template={
            "HVACTemplate:Zone:VAV": {
                "HVACTemplate:Zone:VAV 1": {
                    "template_thermostat_name": "All Zones"
                }
            }
        })
        self.assertEqual('All Zones', thermostat_template.template_name)
        return

    def test_return_none_thermostat_template_from_from_zone_when_field_missing(self):
        self.hvac_template.expanded_thermostats = self.hvac_template._expand_templates(
            templates={
                "HVACTemplate:Thermostat": {
                    "All Zones": {
                        "heating_setpoint_schedule_name": "Htg-SetP-Sch",
                        "cooling_setpoint_schedule_name": "Clg-SetP-Sch"
                    }
                }
            },
            expand_class=ExpandThermostat)
        thermostat_template = self.hvac_template._get_thermostat_template_from_zone_template(zone_template={
            "HVACTemplate:Zone:VAV": {
                "HVACTemplate:Zone:VAV 1": {
                    "field_1": "value_1"
                }
            }
        })
        self.assertIsNone(thermostat_template)
        return

    def test_thermostat_template_from_zone_field_reject_bad_input(self):
        self.hvac_template.expanded_thermostats = self.hvac_template._expand_templates(
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
            self.hvac_template._get_thermostat_template_from_zone_template(zone_template={
                "HVACTemplate:Zone:VAV": {
                    "HVACTemplate:Zone:VAV 1": {
                        "template_thermostat_name": "Bad Name"
                    }
                }
            })
        return

    def test_create_zonecontrol_thermostat_dualsetpoint(self):
        self.hvac_template._get_thermostat_template_from_zone_template = MagicMock()
        self.hvac_template._get_thermostat_template_from_zone_template.return_value.epjson = {
            "ThermostatSetpoint:DualSetpoint": {
                "All Zones SP Control": {
                    "cooling_setpoint_temperature_schedule_name": "Clg-SetP-Sch",
                    "heating_setpoint_temperature_schedule_name": "Htg-SetP-Sch"
                }
            }
        }
        self.hvac_template._create_zonecontrol_thermostat(zone_template={
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
        self.hvac_template._get_thermostat_template_from_zone_template = MagicMock()
        self.hvac_template._get_thermostat_template_from_zone_template.return_value.epjson = {
            "ThermostatSetpoint:SingleHeating": {
                "All Zones SP Control": {
                    "setpoint_temperature_schedule_name": "Clg-SetP-Sch",
                }
            }
        }
        self.hvac_template._create_zonecontrol_thermostat(zone_template={
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
        self.hvac_template._get_thermostat_template_from_zone_template = MagicMock()
        self.hvac_template._get_thermostat_template_from_zone_template.return_value.epjson = {
            "ThermostatSetpoint:SingleCooling": {
                "All Zones SP Control": {
                    "setpoint_temperature_schedule_name": "Clg-SetP-Sch",
                }
            }
        }
        self.hvac_template._create_zonecontrol_thermostat(zone_template={
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
        self.hvac_template._get_thermostat_template_from_zone_template = MagicMock()
        self.hvac_template._get_thermostat_template_from_zone_template.return_value.epjson = {
            "ThermostatSetpoint:BadThermostat": {
                "All Zones SP Control": {
                    "setpoint_temperature_schedule_name": "Clg-SetP-Sch",
                }
            }
        }
        with self.assertRaises(InvalidTemplateException):
            self.hvac_template._create_zonecontrol_thermostat(zone_template={
                "HVACTemplate:Zone:VAV": {
                    "HVACTemplate:Zone:VAV 1": {
                        "zone_name": "TEST ZONE"
                    }
                }
            })
        return

    def test_exception_create_zonecontrol_thermostat_no_thermostat(self):
        self.hvac_template._get_thermostat_template_from_zone_template = MagicMock()
        self.hvac_template._get_thermostat_template_from_zone_template.return_value.epjson = {}
        with self.assertRaises(InvalidTemplateException):
            self.hvac_template._create_zonecontrol_thermostat(zone_template={
                "HVACTemplate:Zone:VAV": {
                    "HVACTemplate:Zone:VAV 1": {
                        "zone_name": "TEST ZONE"
                    }
                }
            })
        return

    def test_zone_field_name_from_system_template_type(self):
        output = self.hvac_template._get_zone_template_field_from_system_type(
            template_type='HVACTemplate:System:ConstantVolume')
        self.assertEqual('template_constant_volume_system_name', output)
        output = self.hvac_template._get_zone_template_field_from_system_type(
            template_type='HVACTemplate:System:DedicatedOutdoorAir')
        self.assertEqual('dedicated_outdoor_air_system_name', output)
        output = self.hvac_template._get_zone_template_field_from_system_type(
            template_type='HVACTemplate:System:DualDuct')
        self.assertEqual('template_dual_duct_system_name', output)
        output = self.hvac_template._get_zone_template_field_from_system_type(
            template_type='HVACTemplate:System:Unitary')
        self.assertEqual('template_unitary_system_name', output)
        output = self.hvac_template._get_zone_template_field_from_system_type(
            template_type='HVACTemplate:System:VAV')
        self.assertEqual('template_vav_system_name', output)
        output = self.hvac_template._get_zone_template_field_from_system_type(
            template_type='HVACTemplate:System:VRF')
        self.assertEqual('template_vrf_system_name', output)
        return

    def test_reject_zone_field_name_from_system_template_type_bad_input(self):
        with self.assertRaisesRegex(InvalidTemplateException, 'Invalid system'):
            self.hvac_template._get_zone_template_field_from_system_type(
                template_type='HVACTemplate:System:BadSystem')
        return

    def test_system_path_objects_no_plenum(self):
        eo = ExpandObjects()
        es = ExpandSystem(template={
            "HVACTemplate:System:VAV": {
                "VAV Sys 1": {
                }
            }
        })
        ez_l = []
        for unique_name in ['SPACE1-1', 'SPACE2-1']:
            eo.unique_name = unique_name
            mock_epjson = eo.resolve_objects(epjson=copy.deepcopy(mock_zone_epjson))
            ez = MagicMock()
            ez_epjson = PropertyMock(return_value=mock_epjson)
            type(ez).epjson = ez_epjson
            type(ez).template_vav_system_name = 'VAV Sys 1'
            type(ez).zone_name = unique_name
            type(ez).unique_name = unique_name
            ez_l.append(ez)
        output = self.hvac_template._create_system_path_connection_objects(system_class_object=es, expanded_zones=ez_l)
        self.assertEqual(
            {'AirLoopHVAC:ZoneSplitter': 1, 'AirLoopHVAC:ZoneMixer': 1,
             'AirLoopHVAC:SupplyPath': 1, 'AirLoopHVAC:ReturnPath': 1},
            eo.summarize_epjson(output)
        )
        return

    def test_system_path_objects_supply_plenum(self):
        eo = ExpandObjects()
        es = ExpandSystem(template={
            "HVACTemplate:System:VAV": {
                "VAV Sys 1": {
                    'supply_plenum_name': 'test plenum'
                }
            }
        })
        ez_l = []
        for unique_name in ['SPACE1-1', 'SPACE2-1']:
            eo.unique_name = unique_name
            mock_epjson = eo.resolve_objects(epjson=copy.deepcopy(mock_zone_epjson))
            ez = MagicMock()
            ez_epjson = PropertyMock(return_value=mock_epjson)
            type(ez).epjson = ez_epjson
            type(ez).template_vav_system_name = 'VAV Sys 1'
            type(ez).zone_name = unique_name
            type(ez).unique_name = unique_name
            ez_l.append(ez)
        output = self.hvac_template._create_system_path_connection_objects(system_class_object=es, expanded_zones=ez_l)
        self.assertEqual(
            {'AirLoopHVAC:SupplyPlenum': 1, 'AirLoopHVAC:ZoneMixer': 1,
             'AirLoopHVAC:SupplyPath': 1, 'AirLoopHVAC:ReturnPath': 1},
            eo.summarize_epjson(output)
        )
        return

    def test_system_path_objects_return_plenum(self):
        eo = ExpandObjects()
        es = ExpandSystem(template={
            "HVACTemplate:System:VAV": {
                "VAV Sys 1": {
                    'return_plenum_name': 'test plenum'
                }
            }
        })
        ez_l = []
        for unique_name in ['SPACE1-1', 'SPACE2-1']:
            eo.unique_name = unique_name
            mock_epjson = eo.resolve_objects(epjson=copy.deepcopy(mock_zone_epjson))
            ez = MagicMock()
            ez_epjson = PropertyMock(return_value=mock_epjson)
            type(ez).epjson = ez_epjson
            type(ez).template_vav_system_name = 'VAV Sys 1'
            type(ez).zone_name = unique_name
            type(ez).unique_name = unique_name
            ez_l.append(ez)
        output = self.hvac_template._create_system_path_connection_objects(system_class_object=es, expanded_zones=ez_l)
        self.assertEqual(
            {'AirLoopHVAC:ZoneSplitter': 1, 'AirLoopHVAC:ReturnPlenum': 1,
             'AirLoopHVAC:SupplyPath': 1, 'AirLoopHVAC:ReturnPath': 1},
            eo.summarize_epjson(output)
        )
        return

    def test_system_path_objects_both_plenum(self):
        eo = ExpandObjects()
        es = ExpandSystem(template={
            "HVACTemplate:System:VAV": {
                "VAV Sys 1": {
                    'supply_plenum_name': 'test supply plenum',
                    'return_plenum_name': 'test return plenum'
                }
            }
        })
        ez_l = []
        for unique_name in ['SPACE1-1', 'SPACE2-1']:
            eo.unique_name = unique_name
            mock_epjson = eo.resolve_objects(epjson=copy.deepcopy(mock_zone_epjson))
            ez = MagicMock()
            ez_epjson = PropertyMock(return_value=mock_epjson)
            type(ez).epjson = ez_epjson
            type(ez).template_vav_system_name = 'VAV Sys 1'
            type(ez).zone_name = unique_name
            type(ez).unique_name = unique_name
            ez_l.append(ez)
        output = self.hvac_template._create_system_path_connection_objects(system_class_object=es, expanded_zones=ez_l)
        self.assertEqual(
            {'AirLoopHVAC:SupplyPlenum': 1, 'AirLoopHVAC:ReturnPlenum': 1,
             'AirLoopHVAC:SupplyPath': 1, 'AirLoopHVAC:ReturnPath': 1},
            eo.summarize_epjson(output)
        )
        return

    def test_reject_system_path_objects_no_zone_equipment(self):
        eo = ExpandObjects()
        es = ExpandSystem(template={
            "HVACTemplate:System:VAV": {
                "VAV Sys 1": {
                    'supply_plenum_name': 'test supply plenum',
                    'return_plenum_name': 'test return plenum'
                }
            }
        })
        ez_l = []
        for unique_name in ['SPACE1-1', 'SPACE2-1']:
            eo.unique_name = unique_name
            mock_epjson = eo.resolve_objects(epjson=copy.deepcopy(mock_zone_epjson))
            mock_epjson.pop('AirTerminal:SingleDuct:VAV:Reheat')
            ez = MagicMock()
            ez_epjson = PropertyMock(return_value=mock_epjson)
            type(ez).epjson = ez_epjson
            type(ez).template_vav_system_name = 'VAV Sys 1'
            type(ez).zone_name = unique_name
            type(ez).unique_name = unique_name
            ez_l.append(ez)
        with self.assertRaisesRegex(InvalidTemplateException, 'Search for zone equipment'):
            self.hvac_template._create_system_path_connection_objects(system_class_object=es, expanded_zones=ez_l)
        return

    def test_reject_system_path_objects_no_zone_connection_equipment(self):
        eo = ExpandObjects()
        es = ExpandSystem(template={
            "HVACTemplate:System:VAV": {
                "VAV Sys 1": {
                    'supply_plenum_name': 'test supply plenum',
                    'return_plenum_name': 'test return plenum'
                }
            }
        })
        ez_l = []
        for unique_name in ['SPACE1-1', 'SPACE2-1']:
            eo.unique_name = unique_name
            mock_epjson = eo.resolve_objects(epjson=copy.deepcopy(mock_zone_epjson))
            mock_epjson.pop('ZoneHVAC:EquipmentConnections')
            ez = MagicMock()
            ez_epjson = PropertyMock(return_value=mock_epjson)
            type(ez).epjson = ez_epjson
            type(ez).template_vav_system_name = 'VAV Sys 1'
            type(ez).zone_name = unique_name
            type(ez).unique_name = unique_name
            ez_l.append(ez)
        with self.assertRaisesRegex(InvalidTemplateException, 'Search for ZoneHVAC:EquipmentConnections'):
            self.hvac_template._create_system_path_connection_objects(system_class_object=es, expanded_zones=ez_l)
        return
