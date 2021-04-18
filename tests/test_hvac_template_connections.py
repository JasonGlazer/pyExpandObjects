import copy
import unittest
from unittest.mock import MagicMock, PropertyMock

from src.hvac_template import HVACTemplate
from src.hvac_template import InvalidTemplateException
from src.expand_objects import ExpandObjects, ExpandSystem, ExpandZone
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

    def test_create_zonecontrol_thermostat_dualsetpoint(self):
        et = MagicMock()
        et_epjson = PropertyMock(return_value={
            "ThermostatSetpoint:DualSetpoint": {
                "All Zones": {
                    "cooling_setpoint_temperature_schedule_name": "Clg-SetP-Sch",
                    "heating_setpoint_temperature_schedule_name": "Htg-SetP-Sch"

                }
            }
        })
        type(et).epjson = et_epjson
        self.hvac_template.expanded_thermostats = {'All Zones': et}
        ez = ExpandZone(template={
            "HVACTemplate:Zone:VAV": {
                "HVACTemplate:Zone:VAV 1": {
                    "zone_name": "TEST ZONE",
                    'template_thermostat_name': 'All Zones'
                }
            }
        })
        self.hvac_template._create_zonecontrol_thermostat(zone_class_object=ez)
        self.assertEqual(
            'ThermostatSetpoint:DualSetpoint',
            self.hvac_template.epjson['ZoneControl:Thermostat']['TEST ZONE Thermostat']['control_1_object_type'])
        self.assertEqual(
            'HVACTemplate-Always4',
            list(self.hvac_template.epjson['Schedule:Compact'].keys())[0])
        return

    def test_create_zonecontrol_thermostat_single_heating(self):
        et = MagicMock()
        et_epjson = PropertyMock(return_value={
            "ThermostatSetpoint:SingleHeating": {
                "All Zones": {
                    "setpoint_temperature_schedule_name": "Clg-SetP-Sch",
                }
            }
        })
        type(et).epjson = et_epjson
        self.hvac_template.expanded_thermostats = {'All Zones': et}
        ez = ExpandZone(template={
            "HVACTemplate:Zone:VAV": {
                "HVACTemplate:Zone:VAV 1": {
                    "zone_name": "TEST ZONE",
                    'template_thermostat_name': 'All Zones'
                }
            }
        })
        self.hvac_template._create_zonecontrol_thermostat(zone_class_object=ez)
        self.assertEqual(
            'ThermostatSetpoint:SingleHeating',
            self.hvac_template.epjson['ZoneControl:Thermostat']['TEST ZONE Thermostat']['control_1_object_type'])
        self.assertEqual(
            'HVACTemplate-Always1',
            list(self.hvac_template.epjson['Schedule:Compact'].keys())[0])
        return

    def test_create_zonecontrol_thermostat_single_cooling(self):
        et = MagicMock()
        et_epjson = PropertyMock(return_value={
            "ThermostatSetpoint:SingleCooling": {
                "All Zones": {
                    "setpoint_temperature_schedule_name": "Clg-SetP-Sch",
                }
            }
        })
        type(et).epjson = et_epjson
        self.hvac_template.expanded_thermostats = {'All Zones': et}
        ez = ExpandZone(template={
            "HVACTemplate:Zone:VAV": {
                "HVACTemplate:Zone:VAV 1": {
                    "zone_name": "TEST ZONE",
                    'template_thermostat_name': 'All Zones'
                }
            }
        })
        self.hvac_template._create_zonecontrol_thermostat(zone_class_object=ez)
        self.assertEqual(
            'ThermostatSetpoint:SingleCooling',
            self.hvac_template.epjson['ZoneControl:Thermostat']['TEST ZONE Thermostat']['control_1_object_type'])
        self.assertEqual(
            'HVACTemplate-Always2',
            list(self.hvac_template.epjson['Schedule:Compact'].keys())[0])
        return

    def test_exception_zonecontrol_thermostat_bad_thermostat(self):
        et = MagicMock()
        et_epjson = PropertyMock(return_value={
            "ThermostatSetpoint:BadThermostat": {
                "All Zones SP Control": {
                    "setpoint_temperature_schedule_name": "Clg-SetP-Sch",
                }
            }
        })
        type(et).epjson = et_epjson
        self.hvac_template.expanded_thermostats = {'All Zones': et}
        ez = ExpandZone(template={
            "HVACTemplate:Zone:VAV": {
                "HVACTemplate:Zone:VAV 1": {
                    "zone_name": "TEST ZONE",
                    'template_thermostat_name': 'All Zones'
                }
            }
        })
        with self.assertRaises(InvalidTemplateException):
            self.hvac_template._create_zonecontrol_thermostat(zone_class_object=ez)
        return

    def test_exception_create_zonecontrol_thermostat_no_thermostat(self):
        ez = ExpandZone(template={
            "HVACTemplate:Zone:VAV": {
                "HVACTemplate:Zone:VAV 1": {
                    "zone_name": "TEST ZONE",
                    'template_thermostat_name': 'All Zones'
                }
            }
        })
        with self.assertRaises(InvalidTemplateException):
            self.hvac_template._create_zonecontrol_thermostat(zone_class_object=ez)
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
        expanded_zones = {}
        for unique_name in ['SPACE1-1', 'SPACE2-1']:
            eo.unique_name = unique_name
            mock_epjson = eo.resolve_objects(epjson=copy.deepcopy(mock_zone_epjson))
            ez = MagicMock()
            ez_epjson = PropertyMock(return_value=mock_epjson)
            type(ez).epjson = ez_epjson
            type(ez).template_vav_system_name = 'VAV Sys 1'
            type(ez).zone_name = unique_name
            type(ez).unique_name = unique_name
            expanded_zones[unique_name] = ez
        output = self.hvac_template._create_system_path_connection_objects(
            system_class_object=es,
            expanded_zones=expanded_zones)
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
        expanded_zones = {}
        for unique_name in ['SPACE1-1', 'SPACE2-1']:
            eo.unique_name = unique_name
            mock_epjson = eo.resolve_objects(epjson=copy.deepcopy(mock_zone_epjson))
            ez = MagicMock()
            ez_epjson = PropertyMock(return_value=mock_epjson)
            type(ez).epjson = ez_epjson
            type(ez).template_vav_system_name = 'VAV Sys 1'
            type(ez).zone_name = unique_name
            type(ez).unique_name = unique_name
            expanded_zones[unique_name] = ez
        output = self.hvac_template._create_system_path_connection_objects(
            system_class_object=es,
            expanded_zones=expanded_zones)
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
        expanded_zones = {}
        for unique_name in ['SPACE1-1', 'SPACE2-1']:
            eo.unique_name = unique_name
            mock_epjson = eo.resolve_objects(epjson=copy.deepcopy(mock_zone_epjson))
            ez = MagicMock()
            ez_epjson = PropertyMock(return_value=mock_epjson)
            type(ez).epjson = ez_epjson
            type(ez).template_vav_system_name = 'VAV Sys 1'
            type(ez).zone_name = unique_name
            type(ez).unique_name = unique_name
            expanded_zones[unique_name] = ez
        output = self.hvac_template._create_system_path_connection_objects(
            system_class_object=es,
            expanded_zones=expanded_zones)
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
        expanded_zones = {}
        for unique_name in ['SPACE1-1', 'SPACE2-1']:
            eo.unique_name = unique_name
            mock_epjson = eo.resolve_objects(epjson=copy.deepcopy(mock_zone_epjson))
            ez = MagicMock()
            ez_epjson = PropertyMock(return_value=mock_epjson)
            type(ez).epjson = ez_epjson
            type(ez).template_vav_system_name = 'VAV Sys 1'
            type(ez).zone_name = unique_name
            type(ez).unique_name = unique_name
            expanded_zones[unique_name] = ez
        output = self.hvac_template._create_system_path_connection_objects(
            system_class_object=es,
            expanded_zones=expanded_zones)
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
        expanded_zones = {}
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
            expanded_zones[unique_name] = ez
        with self.assertRaisesRegex(InvalidTemplateException, 'Search for zone equipment'):
            self.hvac_template._create_system_path_connection_objects(
                system_class_object=es,
                expanded_zones=expanded_zones)
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
        expanded_zones = {}
        for unique_name in ['SPACE1-1', 'SPACE2-1']:
            eo.unique_name = unique_name
            mock_epjson = eo.resolve_objects(epjson=copy.deepcopy(mock_zone_epjson))
            mock_epjson.pop('ZoneHVAC:EquipmentConnections')
            ez = MagicMock()
            ez_epjson = PropertyMock(return_value=mock_epjson)
            type(ez).epjson = ez_epjson
            ez.template_vav_system_name = 'VAV Sys 1'
            ez.zone_name = unique_name
            ez.unique_name = unique_name
            expanded_zones[unique_name] = ez
        with self.assertRaisesRegex(InvalidTemplateException, 'Search for ZoneHVAC:EquipmentConnections'):
            self.hvac_template._create_system_path_connection_objects(
                system_class_object=es,
                expanded_zones=expanded_zones)
        return

    def test_plant_equipment_creates_loop(self):
        ep = MagicMock()
        ep.template_type = 'HVACTemplate:Plant:HotWaterLoop'
        expanded_plant_loops = {'Test Hot Water': ep}
        epe = MagicMock()
        epe.template_type = 'HVACTemplate:Plant:Chiller'
        epe.condenser_type = 'WaterCooled'
        output = self.hvac_template._create_loop_from_plant_equipment(
            plant_equipment_class_object=epe,
            plant_loop_class_objects=expanded_plant_loops)
        self.assertEqual('HVACTemplate:Plant:CondenserWaterLoop', list(output.keys())[0])
        return

    def test_plant_equipment_doesnt_create_loop_if_existing(self):
        ep = MagicMock()
        ep.template_type = 'HVACTemplate:Plant:CondenserWaterLoop'
        expanded_plant_loops = {'Test Hot Water': ep}
        epe = MagicMock()
        epe.template_type = 'HVACTemplate:Plant:Chiller'
        epe.condenser_type = 'WaterCooled'
        output = self.hvac_template._create_loop_from_plant_equipment(
            plant_equipment_class_object=epe,
            plant_loop_class_objects=expanded_plant_loops)
        self.assertEqual(0, len(output.keys()))
        return
