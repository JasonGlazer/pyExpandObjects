import re
import copy
from epjson_handler import EPJSON
from expand_objects import ExpandObjects, ExpandThermostat, ExpandZone, ExpandSystem, ExpandPlantLoop, \
    ExpandPlantEquipment
from custom_exceptions import InvalidTemplateException, InvalidEpJSONException, PyExpandObjectsYamlStructureException


class HVACTemplate(EPJSON):
    """
    Handle HVACTemplate conversion process and connect created objects together.

    Inheritance:
    EPJSON <- Logger

    Attributes:
        templates: HVACTemplate objects from epJSON file
        base_objects: Non-HVACTemplate objects from epJSON file
        templates_zones: HVACTemplate:Zone: objects
        templates_systems: HVACTemplate:System: objects
        templates_plant_equipment: HVACTemplate:Plant equipment objects
        templates_plant_loops: HVACTemplate:Plant: loop objects
        expanded_*: List of class objects for each template type
        epjson: epJSON used to store connection objects
    """

    def __init__(
            self,
            no_schema=False):
        """
        :param no_schema: Boolean flag for skipping schema validation
        """
        super().__init__(no_schema=no_schema)
        self.templates = {}
        self.base_objects = {}
        self.templates_systems = {}
        self.templates_zones = {}
        self.templates_plant_equipment = {}
        self.templates_plant_loops = {}
        self.templates_thermostats = {}
        self.expanded_thermostats = {}
        self.expanded_zones = {}
        self.expanded_systems = {}
        self.expanded_plant_loops = {}
        self.expanded_plant_equipment = {}
        self.epjson = {}
        return

    def _hvac_template_preprocess(self, epjson):
        """
        Organize epJSON and assign template objects to specific class attributes

        :param epjson: Input epJSON object
        :return: organized epJSON template objects into templates, and templates_* as class attributes
        """
        self.logger.info('##### HVACTemplate #####')
        for object_type, object_structure in epjson.items():
            if re.match('^HVACTemplate:*', object_type):
                if re.match('^HVACTemplate:Thermostat$', object_type):
                    self.merge_epjson(
                        super_dictionary=self.templates_thermostats,
                        object_dictionary={object_type: object_structure},
                        unique_name_override=False)
                elif re.match('^HVACTemplate:Zone:('
                              'ConstantVolume|BaseboardHeat|FanCoil|IdealLoadsAirSystem|PTAC|PTHP|WaterToAirHeatPump|'
                              'VRF|Unitary|VAV|VAV:FanPowered|VAV:HeatAndCool|ConstantVolumn|DualDuct)$',
                              object_type):
                    self.merge_epjson(
                        super_dictionary=self.templates_zones,
                        object_dictionary={object_type: object_structure},
                        unique_name_override=False)
                elif re.match('^HVACTemplate:System:('
                              'VRF|Unitary|UnitaryHeatPump:AirToAir|UnitarySystem|VAV|PackagedVAV|'
                              'ConstantVolume|DualDuct|DedicatedOutdoorAir'
                              ')$', object_type):
                    self.merge_epjson(
                        super_dictionary=self.templates_systems,
                        object_dictionary={object_type: object_structure},
                        unique_name_override=False)
                elif re.match('^HVACTemplate:Plant:(ChilledWater|HotWater|MixedWater)Loop$', object_type):
                    self.merge_epjson(
                        super_dictionary=self.templates_plant_loops,
                        object_dictionary={object_type: object_structure},
                        unique_name_override=False)
                elif re.match('^HVACTemplate:Plant:(Chiller|Tower|Boiler)(:ObjectReference)*$', object_type):
                    # for plant equipment object references, add the referenced object to epjson for complex input resolution
                    #  later on.  For chiller objects, also identify condenser type and make it a template attribute.
                    if object_type == 'HVACTemplate:Plant:Chiller:ObjectReference':
                        try:
                            (object_name, object_fields), = object_structure.items()
                            reference_object_structure = epjson[object_fields['chiller_object_type']]
                            for reference_object_name, reference_object_fields in reference_object_structure.items():
                                if reference_object_name == object_fields['chiller_name']:
                                    try:
                                        object_structure[object_name]['condenser_type'] = reference_object_fields['condenser_type']
                                    except (KeyError, AttributeError):
                                        object_structure['condenser_type'] = 'WaterCooled'
                                    object_structure[object_name]['epjson'] = {object_fields['chiller_object_type']: reference_object_structure}
                                    break
                        except (KeyError, AttributeError):
                            raise InvalidTemplateException('HVACTemplate:Plant:Chiller:ObjectReference object is incorrectly formatted '
                                                           '{}'.format(object_structure))
                    elif object_type == 'HVACTemplate:Plant:Boiler:ObjectReference':
                        try:
                            (object_name, object_fields), = object_structure.items()
                            reference_object_structure = epjson[object_fields['boiler_object_type']]
                            for reference_object_name, reference_object_fields in reference_object_structure.items():
                                if reference_object_name == object_fields['boiler_name']:
                                    object_structure[object_name]['epjson'] = {object_fields['boiler_object_type']: reference_object_structure}
                                    break
                        except (KeyError, AttributeError):
                            raise InvalidTemplateException('HVACTemplate:Plant:Boiler:ObjectReference object is incorrectly formatted '
                                                           '{}'.format(object_structure))
                    elif object_type == 'HVACTemplate:Plant:Tower:ObjectReference':
                        try:
                            (object_name, object_fields), = object_structure.items()
                            reference_object_structure = epjson[object_fields['cooling_tower_object_type']]
                            for reference_object_name, reference_object_fields in reference_object_structure.items():
                                if reference_object_name == object_fields['cooling_tower_name']:
                                    object_structure[object_name]['epjson'] = {object_fields['cooling_tower_object_type']: reference_object_structure}
                                    break
                        except (KeyError, AttributeError):
                            raise InvalidTemplateException('HVACTemplate:Plant:Tower:ObjectReference object is incorrectly formatted '
                                                           '{}'.format(object_structure))
                    self.merge_epjson(
                        super_dictionary=self.templates_plant_equipment,
                        object_dictionary={object_type: object_structure},
                        unique_name_override=False)
                else:
                    raise InvalidTemplateException(
                        'Template object type {} was not recognized'.format(object_type))
                # store original templates into dictionary
                self.merge_epjson(
                    super_dictionary=self.templates,
                    object_dictionary={object_type: object_structure},
                    unique_name_override=False)
            else:
                # store all non-template objects into a base epjson object.
                self.merge_epjson(
                    super_dictionary=self.base_objects,
                    object_dictionary={object_type: object_structure},
                    unique_name_override=False)
        return

    def _expand_templates(self, templates, expand_class, **kwargs):
        """
        Run Expand operations on multiple templates
        :param templates: dictionary of HVACTemplate:.* objects
        :param expand_class: ExpandObjects child class to operate on template (e.g. ExpandZone).
        :return: dictionary of expanded objects with unique name as key
        """
        expanded_template_dictionary = {}
        templates = self.epjson_genexp(templates)
        for template in templates:
            (_, template_structure), = template.items()
            (template_name, template_fields), = template_structure.items()
            external_epjson_objects = template_fields.pop('epjson', None)
            expanded_template = expand_class(template=template, epjson=external_epjson_objects, **kwargs).run()
            expanded_template_dictionary[template_name] = expanded_template
        return expanded_template_dictionary

    def _create_zonecontrol_thermostat(self, zone_class_object):
        """
        Create ZoneControl:Thermostat objects.  This operations is performed outside of ExpandObjects because it
        requires cross-referencing between HVACTemplate:Zone and HVACTemplate:Thermostat objects

        :param zone_class_object: ExpandZone object
        :return: Updated class epJSON dictionary with ThermostatSetpoint objects added.  Objects are also added
            to the class self.epsjon dictionary.
        """
        # Retreive the thermostat object
        try:
            thermostat_template_name = getattr(zone_class_object, 'template_thermostat_name')
            thermostat_object = self.expanded_thermostats[thermostat_template_name]
        except AttributeError:
            self.logger.warning('Zone template does not reference a thermostat class object: {}'
                                .format(zone_class_object.unique_name))
            return
        except (ValueError, KeyError):
            raise InvalidTemplateException('Zone template is improperly formatted: {}'
                                           .format(zone_class_object.unique_name))
        # Evaluate the thermostat type in the thermostat object and format the output object accordingly
        try:
            zone_name = getattr(zone_class_object, 'zone_name')
            (thermostat_type, thermostat_structure), = thermostat_object.epjson.items()
            (thermostat_name, _), = thermostat_structure.items()
            # create control schedule based on thermostat type
            if thermostat_type == "ThermostatSetpoint:SingleHeating":
                control_schedule = ExpandObjects().build_compact_schedule(
                    structure_hierarchy=['Objects', 'Common', 'Objects', 'Schedule', 'Compact', 'ALWAYS_VAL'],
                    insert_values=[1, ])
            elif thermostat_type == "ThermostatSetpoint:SingleCooling":
                control_schedule = ExpandObjects().build_compact_schedule(
                    structure_hierarchy=['Objects', 'Common', 'Objects', 'Schedule', 'Compact', 'ALWAYS_VAL'],
                    insert_values=[2, ])
            elif thermostat_type == "ThermostatSetpoint:DualSetpoint":
                control_schedule = ExpandObjects().build_compact_schedule(
                    structure_hierarchy=['Objects', 'Common', 'Objects', 'Schedule', 'Compact', 'ALWAYS_VAL'],
                    insert_values=[4, ])
            else:
                raise InvalidTemplateException("Invalid thermostat type set in ExpandThermostat {}"
                                               .format(thermostat_object.unique_name))
            # create zonecontrol object
            (_, schedule_structure), = control_schedule.items()
            (schedule_name, _), = schedule_structure.items()
            zonecontrol_thermostat = {
                "ZoneControl:Thermostat": {
                    "{} Thermostat".format(zone_name): {
                        "control_1_name": thermostat_name,
                        "control_1_object_type": thermostat_type,
                        "control_type_schedule_name": schedule_name,
                        "zone_or_zonelist_name": "{}".format(zone_name)
                    }
                }
            }
            self.merge_epjson(
                super_dictionary=self.epjson,
                object_dictionary=dict(control_schedule, **zonecontrol_thermostat),
                unique_name_override=True
            )
            return dict(control_schedule, **zonecontrol_thermostat)
        except (ValueError, AttributeError, KeyError):
            raise InvalidTemplateException("HVACTemplate failed to build ZoneControl:Thermostat from zone template "
                                           "{}".format(zone_class_object.unique_name))  # pragma: no cover - catchall

    @staticmethod
    def _get_zone_template_field_from_system_type(template_type):
        """
        Retrieve the corresponding zone field name for a system template type
        :param template_type: HVACTemplate:System object type
        :return: zone field name
        """
        # get the zone field_name that will identify the system template name
        if re.match(r'HVACTemplate:System:ConstantVolume', template_type):
            zone_system_template_field_name = 'template_constant_volume_system_name'
        elif re.match(r'HVACTemplate:System:DedicatedOutdoorAir', template_type):
            zone_system_template_field_name = 'dedicated_outdoor_air_system_name'
        elif re.match(r'HVACTemplate:System:DualDuct', template_type):
            zone_system_template_field_name = 'template_dual_duct_system_name'
        elif re.match(r'HVACTemplate:System:Unitary.*', template_type):
            zone_system_template_field_name = 'template_unitary_system_name'
        elif re.match(r'HVACTemplate:System:.*VAV$', template_type):
            zone_system_template_field_name = 'template_vav_system_name'
        elif re.match(r'HVACTemplate:System:VRF', template_type):
            zone_system_template_field_name = 'template_vrf_system_name'
        else:
            raise InvalidTemplateException("Invalid system type passed to supply path creation function: {}"
                                           .format(template_type))
        return zone_system_template_field_name

    def _create_system_path_connection_objects(self, system_class_object, expanded_zones):
        """
        Create objects connecting system supply air to zone objects.  An AirLoopHVAC:SupplyPath object is created with
        either an AirLoopHVAC:SupplyPlenum or an AirLoopHVAC:ZoneSplitter object.  The same is true for
        AirLoopHVAC:ReturnPath and AirLoopHVAC:ReturnPlenum/AirLoopHVAC:ZoneMixer.

        :param system_class_object: Expanded HVACTemplate:System:.* class object
        :param expanded_zones: dictionary of ExpandZone objects
        :return: system supply air connection objects.  AirLoopHVAC:SupplyPath object and either
            AirLoopHVAC:SupplyPlenum or AirLoopHVAC:ZoneSplitter object as well ass AirLoopHVAC:ReturnPath and either
            AirLoopHVAC:ReturnPlenum or AirLoopHVAC:ZoneMixer.
        """
        zone_system_template_field_name = \
            self._get_zone_template_field_from_system_type(template_type=system_class_object.template_type)
        # iterate over inlet node name types.  For DualDuct, this is two entries (hot/cold).  For all other systems,
        # this is a single value
        if system_class_object.template_type == 'HVACTemplate:System:DualDuct':
            inlet_nodes = ['cold_air_inlet_node_name', 'hot_air_inlet_node_name']
        else:
            inlet_nodes = ['air_inlet_node_name', ]
        # create ExpandObjects class object to use some yaml and epjson functions
        eo = ExpandObjects()
        eo.unique_name = getattr(system_class_object, 'template_name')
        # iterate over expanded zones and if the system reference field exists, and is for the referenced system,
        # append them in the splitter and mixer lists
        zone_return_plenums = []
        zone_induced_air_nodes = []
        for node_idx, inlet_node in enumerate(inlet_nodes):
            zone_splitters = []
            zone_mixers = []
            zone_supply_plenums = []
            for _, ez in expanded_zones.items():
                if getattr(ez, zone_system_template_field_name, None) == system_class_object.template_name:
                    if getattr(ez, 'flow_type', None) in ['SeriesFromPlenum', 'ParallelFromPlenum']:
                        zone_induced_air_node = ez.unique_name
                    else:
                        zone_induced_air_node = None
                    if getattr(ez, 'supply_plenum_name', None) or (
                            getattr(ez, 'cold_supply_plenum_name', None) and inlet_node == 'cold_air_inlet_node_name') or (
                            getattr(ez, 'hot_supply_plenum_name', None) and inlet_node == 'hot_air_inlet_node_name'):
                        try:
                            zone_supply_equipment = {'AirLoopHVAC:SupplyPlenum': ez.epjson['AirLoopHVAC:SupplyPlenum']}
                        except (KeyError, AttributeError):
                            raise InvalidTemplateException('supply_plenum_name indicated for zone template {} but '
                                                           'AirLoopHVAC:SupplyPlenum was not created'.format(ez.unique_name))
                    else:
                        zone_supply_equipment = self.get_epjson_objects(
                            epjson=ez.epjson,
                            object_type_regexp=r'^AirTerminal:.*')
                    try:
                        (zone_supply_equipment_type, zone_supply_equipment_structure), = zone_supply_equipment.items()
                        (zone_supply_equipment_name, zone_supply_equipment_fields), = zone_supply_equipment_structure.items()

                        if zone_supply_equipment_type == 'AirLoopHVAC:SupplyPlenum':
                            outlet_node_name = zone_supply_equipment_fields['inlet_node_name']
                            zone_supply_plenums.append({
                                'component_name': zone_supply_equipment_name,
                                'component_object_type': zone_supply_equipment_type
                            })
                        elif zone_supply_equipment_type in ['AirTerminal:SingleDuct:SeriesPIU:Reheat',
                                                            'AirTerminal:SingleDuct:ParallelPIU:Reheat']:
                            # Raise error if inlet node name is overridden for multi-inlet node systems (DualDuct)
                            if len(inlet_nodes) > 1:
                                raise InvalidTemplateException('Series or Parallel PIU is being referenced '
                                                               'by an invalid system {}'.format(system_class_object.template_type))
                            outlet_node_name = zone_supply_equipment_fields['supply_air_inlet_node_name']
                        else:
                            outlet_node_name = zone_supply_equipment_fields[inlet_node]
                    except (KeyError, AttributeError, ValueError):
                        raise InvalidTemplateException('Search for zone equipment from Supply Path creation failed for '
                                                       'outlet node.  system {}, zone {}, zone equipment {}'
                                                       .format(system_class_object.template_name, ez.unique_name,
                                                               zone_supply_equipment))
                    if getattr(ez, 'return_plenum_name', None):
                        try:
                            zone_return_equipment = {'AirLoopHVAC:ReturnPlenum': ez.epjson['AirLoopHVAC:ReturnPlenum']}
                        except (KeyError, AttributeError):
                            raise InvalidTemplateException('return_plenum_name indicated for zone template {} but '
                                                           'AirLoopHVAC:ReturnPlenum was not created'.format(ez.unique_name))
                    else:
                        try:
                            zone_return_equipment = {'ZoneHVAC:EquipmentConnections': ez.epjson['ZoneHVAC:EquipmentConnections']}
                        except (KeyError, AttributeError, ValueError):
                            raise InvalidTemplateException('Search for ZoneHVAC:EquipmentConnections object from Supply '
                                                           'Path creation failed for inlet node.  system {}, zone {}'
                                                           .format(system_class_object.template_name, ez.unique_name))
                    try:
                        (zone_return_equipment_type, zone_return_equipment_structure), = zone_return_equipment.items()
                        (zone_return_equipment_name, zone_return_equipment_fields), = zone_return_equipment_structure.items()
                        if zone_return_equipment_type == 'AirLoopHVAC:ReturnPlenum':
                            inlet_node_name = zone_return_equipment_fields['outlet_node_name']
                            # use node_idx to prevent multiple zone_return_plenum objects from being created in dualduct zones
                            if node_idx == 0:
                                zone_return_plenums.append({
                                    'component_name': zone_return_equipment_name,
                                    'component_object_type': zone_return_equipment_type
                                })
                        else:
                            inlet_node_name = zone_return_equipment_fields['zone_return_air_node_or_nodelist_name']
                    except (KeyError, AttributeError, ValueError):
                        raise InvalidTemplateException('Search for zone equipment from Return Path creation failed for '
                                                       'inlet node.  system {}, zone {}, zone equipment {}'
                                                       .format(system_class_object.template_name, ez.unique_name,
                                                               zone_return_equipment))
                    zone_splitters.append(
                        {
                            "outlet_node_name": outlet_node_name
                        }
                    )
                    zone_mixers.append(
                        {
                            "inlet_node_name": inlet_node_name
                        }
                    )
                    if zone_induced_air_node:
                        # This is for PIU objects that use SeriesFromPlenum or ParallelFromPlenum
                        zone_induced_air_nodes.append(
                            {
                                "node_name": '{} Return'.format(zone_induced_air_node)
                            }
                        )
            # create plenums or spliters/mixers, depending on template inputs
            supply_plenum_name = getattr(system_class_object, 'supply_plenum_name', None)
            if supply_plenum_name:
                # set return plenum name attribute for transition and mapping processing
                eo.supply_plenum_name = supply_plenum_name
                supply_object = eo.get_structure(structure_hierarchy=[
                    'AutoCreated', 'System', 'AirLoopHVAC', 'SupplyPlenum', 'Base'])
                supply_object['nodes'] = zone_splitters
                supply_object = {'AirLoopHVAC:SupplyPlenum': supply_object}
            else:
                supply_object = eo.get_structure(structure_hierarchy=[
                    'AutoCreated', 'System', 'AirLoopHVAC', 'ZoneSplitter', 'Base'])
                supply_object['nodes'] = zone_splitters
                supply_object = {'AirLoopHVAC:ZoneSplitter': supply_object}
            # Add Path objects
            supply_path_object = {'AirLoopHVAC:SupplyPath':
                                  eo.get_structure(structure_hierarchy=[
                                      'AutoCreated', 'System', 'AirLoopHVAC', 'SupplyPath', 'Base'])}
            # add zone supply plenums if they were created
            if zone_supply_plenums:
                (_, supply_path_object_fields), = supply_path_object.items()
                supply_path_object_fields['components'].extend(zone_supply_plenums)
            # Rename objects if multi-inlet node system is used
            # todo_eo: this can possibly be removed it the unique name is changed on object creations
            if system_class_object.template_type == 'HVACTemplate:System:DualDuct':
                (_, supply_object_fields), = supply_object.items()
                (_, supply_path_object_fields), = supply_path_object.items()
                if inlet_node.startswith('cold_air'):
                    supply_object_fields['name'] = supply_object_fields['name'].replace('{}', '{} Cold')
                    supply_object_fields['inlet_node_name'] = supply_object_fields['inlet_node_name'].replace('{}', '{} Cold')
                    supply_path_object_fields['name'] = supply_path_object_fields['name'].replace('{}', '{} Cold')
                if inlet_node.startswith('hot_air'):
                    supply_object_fields['name'] = supply_object_fields['name'].replace('{}', '{} Hot')
                    supply_object_fields['inlet_node_name'] = supply_object_fields['inlet_node_name'].replace('{}', '{} Hot')
                    supply_path_object_fields['name'] = supply_path_object_fields['name'].replace('{}', '{} Hot')
            path_dictionary = eo.yaml_list_to_epjson_dictionaries(
                yaml_list=[supply_object, supply_path_object])
            resolved_path_dictionary = eo.resolve_objects(epjson=path_dictionary)
            # save output to class epsjon
            self.merge_epjson(
                super_dictionary=self.epjson,
                object_dictionary=resolved_path_dictionary)
        # Create return objects
        return_plenum_name = getattr(system_class_object, 'return_plenum_name', None)
        return_nodelist = {}
        if return_plenum_name:
            # set return plenum name attribute for transition and mapping processing
            eo.return_plenum_name = return_plenum_name
            return_object = eo.get_structure(structure_hierarchy=[
                'AutoCreated', 'System', 'AirLoopHVAC', 'ReturnPlenum', 'Base'])
            return_object['nodes'] = zone_mixers
            return_object = {'AirLoopHVAC:ReturnPlenum': return_object}
            if zone_induced_air_nodes:
                return_object['AirLoopHVAC:ReturnPlenum']['induced_air_outlet_node_or_nodelist_name'] = \
                    '{} Induced Air Nodes'.format(system_class_object.template_name)
                return_nodelist = {
                    'NodeList': {
                        'name': '{} Induced Air Nodes'.format(system_class_object.template_name),
                        "nodes": zone_induced_air_nodes
                    }
                }
        else:
            return_object = eo.get_structure(structure_hierarchy=[
                'AutoCreated', 'System', 'AirLoopHVAC', 'ZoneMixer', 'Base'])
            return_object['nodes'] = zone_mixers
            return_object = {'AirLoopHVAC:ZoneMixer': return_object}
        # Add Path objects
        return_path_object = {
            'AirLoopHVAC:ReturnPath':
            eo.get_structure(structure_hierarchy=[
                'AutoCreated', 'System', 'AirLoopHVAC', 'ReturnPath', 'Base'])}
        # add zone return plenums if they were created
        if zone_return_plenums:
            (_, return_path_object_fields), = return_path_object.items()
            # only take the first item, subsequent items are only duplicates from dualduct zone templates
            return_path_object_fields['components'] = zone_return_plenums + return_path_object_fields['components']
        path_dictionary = eo.yaml_list_to_epjson_dictionaries(
            yaml_list=[return_object, return_path_object, return_nodelist])
        resolved_path_dictionary = eo.resolve_objects(epjson=path_dictionary)
        # save output to class epsjon
        self.merge_epjson(
            super_dictionary=self.epjson,
            object_dictionary=resolved_path_dictionary)
        return resolved_path_dictionary

    def _create_system_vrf_path_connection_objects(self, system_class_object, expanded_zones):
        """
        Create objects connecting VRF system to zone objects.

        :param system_class_object: Expanded HVACTemplate:System:.* class object
        :param expanded_zones: dictionary of ExpandZone objects
        :return: system supply air connection objects.  AirLoopHVAC:SupplyPath object and either
            AirLoopHVAC:SupplyPlenum or AirLoopHVAC:ZoneSplitter object as well ass AirLoopHVAC:ReturnPath and either
            AirLoopHVAC:ReturnPlenum or AirLoopHVAC:ZoneMixer.
        """
        # create ExpandObjects class object to use some yaml and epjson functions
        eo = ExpandObjects()
        eo.unique_name = getattr(system_class_object, 'template_name')
        vrf_object_name_list = []
        zone_system_template_field_name = \
            self._get_zone_template_field_from_system_type(template_type=system_class_object.template_type)
        for _, ez in expanded_zones.items():
            if getattr(ez, zone_system_template_field_name, None) == system_class_object.template_name:
                try:
                    vrf_object = ez.epjson['ZoneHVAC:TerminalUnit:VariableRefrigerantFlow']
                    (vrf_object_name, _), = vrf_object.items()
                except (KeyError, AttributeError):
                    raise InvalidTemplateException("VRF zone template {} expanded with no "
                                                   "ZoneHVAC:TerminalUnit:VariableRefrigerantFlow object".format(ez.unique_name))
                except ValueError:
                    raise InvalidTemplateException('ZoneHVAC:TerminalUnit:VariableRefrigerantFlow '
                                                   'object incorrectly formatted: {}'
                                                   .format(ez.epjson.get('ZoneHVAC:TerminalUnit:VariableRefrigerantFlow', 'None')))
                vrf_object_name_list.append({'zone_terminal_unit_name': vrf_object_name})
        if vrf_object_name_list:
            vrf_terminal_object = eo.get_structure(structure_hierarchy=[
                'AutoCreated', 'System', 'ZoneTerminalUnitList', 'Base'])
            vrf_terminal_object['terminal_units'] = vrf_object_name_list
            path_dictionary = eo.yaml_list_to_epjson_dictionaries(
                yaml_list=[{'ZoneTerminalUnitList': vrf_terminal_object}, ])
            resolved_path_dictionary = eo.resolve_objects(epjson=path_dictionary)
            # save output to class epsjon
            self.merge_epjson(
                super_dictionary=self.epjson,
                object_dictionary=resolved_path_dictionary)
        else:
            raise InvalidTemplateException('Failed to create VRF terminal unit list for {}'.format(system_class_object.template_name))
        return

    def _create_templates_from_plant_equipment(self, plant_equipment_class_object, expanded_plant_loops):
        """
        Create plant and platn equipment loop templates from ExpandPlantEquipment object attributes.
        These outputs will be used as inputs to the initialize new ExpandPlantLoop and ExpandPlantLoopEquipment classes.
        This process must be performed because ExpandPlantLoop must be
        run before ExpandPlantEquipment.  However, certain equipment inputs can cause for new loops to be created.

        :param plant_equipment_class_object: ExpandPlantEquipment class object
        :param expanded_plant_loops: ExpandPlantLoop objects
        :return: Array of Dictionary of HVAC:Template:Plant template objects to create an ExpandPlantLoop object
        """
        # create dictionary to store plant loops
        plant_loop_dictionary = {}
        plant_equipment_dictionary = {}
        # get each loop type specified in the existing plant loop class objects
        plant_loops = [getattr(pl, 'template_type').lower() for pl in expanded_plant_loops.values()]
        # create condenser water loop for water cooled condensers
        if getattr(plant_equipment_class_object, 'template_type', None).lower() in \
                ['hvactemplate:plant:chiller', 'hvactemplate:plant:chiller:objectreference'] \
                and getattr(plant_equipment_class_object, 'condenser_type', None).lower() == 'watercooled' \
                and 'hvactemplate:plant:condenserwaterloop' not in plant_loops:
            # try to get the chilled water loop attributes to transition to condenser water
            chw_loop = [
                pl for pl
                in expanded_plant_loops.values()
                if getattr(pl, 'template_type').lower() == 'hvactemplate:plant:chilledwaterloop']
            cndw_attributes = {}
            if chw_loop:
                for cndw_attribute, chw_attribute in zip(
                        ['condenser_water_pump_rated_head', 'condenser_water_design_setpoint',
                         'condenser_plant_operation_scheme_type'],
                        ['primary_chilled_water_pump_rated_head', 'condenser_water_design_setpoint',
                         'condenser_plant_operation_scheme_type']):
                    try:
                        cndw_attributes[cndw_attribute] = getattr(chw_loop[0], chw_attribute)
                    except AttributeError:
                        self.logger.info('Chilled water attribute {} not set by user, using default for '
                                         'condenser water'.format(chw_attribute))
            cndw_attributes['template_plant_loop_type'] = 'CondenserWaterLoop'
            self.merge_epjson(
                super_dictionary=plant_loop_dictionary,
                object_dictionary={
                    'HVACTemplate:Plant:CondenserWaterLoop': {
                        'Condenser Water Loop': cndw_attributes
                    }
                })
            # append plant loop to list to prevent another one being added.
            plant_loops.append('hvactemplate:plant:condenserwaterloop')
        return plant_loop_dictionary, plant_equipment_dictionary

    def _create_additional_plant_loops_and_equipment_from_equipment(
            self,
            expanded_plant_equipment,
            expanded_plant_loops):
        """
        Create additional HVACTemplate:Plant:.*Loops based on HVACTemplate:Plant:(Chiller|Tower|Boiler) inputs

        :param expanded_plant_equipment: ExpandPlantEquipment objects
        :param expanded_plant_loops: ExpandPlantLoop objects
        :return: Additional plant loop and equipment templates and objects added to expanded classes attributes
        """
        # create deepcopy to iterate over because the expanded_plant_equipment object may change size during iteration
        epe = copy.deepcopy(expanded_plant_equipment)
        for epl_name, epl in epe.items():
            plant_loop_template, plant_equipment_template = self._create_templates_from_plant_equipment(
                plant_equipment_class_object=epl,
                expanded_plant_loops=expanded_plant_loops)
            # If a plant loop was created, reprocess it here.
            if plant_loop_template:
                # add new plant loop to the templates
                for tmpl in [self.templates, self.templates_plant_loops]:
                    self.merge_epjson(
                        super_dictionary=tmpl,
                        object_dictionary=plant_loop_template
                    )
                # Expand new plant loop and add to the class objects
                additional_plant_loops = self._expand_templates(
                    templates=plant_loop_template,
                    expand_class=ExpandPlantLoop
                )
                try:
                    for expanded_name, expanded_object in additional_plant_loops.items():
                        if expanded_name not in expanded_plant_loops.keys():
                            expanded_plant_loops[expanded_name] = expanded_object
                except (AttributeError, ValueError):
                    InvalidTemplateException('A Plant loop was specified to be created from a plant equipment object '
                                             '{}, but the process failed to attach the create objects'
                                             .format(epl_name))
            # if a plant equipment template was created, process it here
            if plant_equipment_template:
                # add new plant equipment to the templates
                for tmpl in [self.templates, self.templates_plant_equipment]:
                    self.merge_epjson(
                        super_dictionary=tmpl,
                        object_dictionary=plant_equipment_template
                    )
                # Expand new plant equipment and add to the class objects
                # pass updated expanded_plant_loops to the class initialization as well.
                additional_plant_equipment = self._expand_templates(
                    templates=plant_equipment_template,
                    expand_class=ExpandPlantEquipment,
                    plant_loop_class_objects=expanded_plant_loops
                )
                try:
                    for expanded_name, expanded_object in additional_plant_equipment.items():
                        if expanded_name not in expanded_plant_loops.keys():
                            expanded_plant_equipment[expanded_name] = expanded_object
                except (AttributeError, ValueError):
                    raise InvalidTemplateException('A Plant equipment was specified to be created from a plant '
                                                   'equipment object {}, but the process failed to attach the create '
                                                   'objects'.format(epl_name))
        return

    @staticmethod
    def _get_plant_equipment_waterloop_branches_by_loop_type(
            plant_loop_class_object,
            expanded_plant_equipment):
        """
        Extract plant equipment branches by loop type and store in epJSON formatted dictionary

        :param plant_loop_class_object: ExpandPlantLoop object
        :param expanded_plant_equipment: dictionary of ExpandPlantEquipment objects
        :return: epJSON formatted dictionary of branch objects for loop connections
        """
        branch_dictionary = {}
        for pe in expanded_plant_equipment.values():
            branch_objects = copy.deepcopy(pe.epjson.get('Branch', {}))
            # Special handling for chillers with condenser water and chilled water branches
            # todo_eo: find a better way to separate the branches instead of searching for chw or cnd in the branch
            #  names.  It may be unreliable with future user inputs.
            if pe.template_type in ['HVACTemplate:Plant:Chiller', 'HVACTemplate:Plant:Chiller:ObjectReference'] \
                    and getattr(pe, 'condenser_type', None) == 'WaterCooled':
                for branch_name, branch_structure in branch_objects.items():
                    if 'chilledwater' in plant_loop_class_object.template_type.lower() and 'chw' in branch_name.lower():
                        branch_dictionary.update({branch_name: branch_objects[branch_name]})
                    if 'condenserwater' in plant_loop_class_object.template_type.lower() and 'cnd' in branch_name.lower():
                        branch_dictionary.update({branch_name: branch_objects[branch_name]})
            # typical handling when all plant equipment branches belong in one loop
            elif pe.template_plant_loop_type in plant_loop_class_object.template_type:
                branch_dictionary.update(branch_objects)
        if branch_dictionary:
            return {'Branch': branch_dictionary}
        else:
            return None

    @staticmethod
    def _get_zone_system_waterloop_branches_by_loop_type(
            plant_loop_class_object,
            expanded_zones,
            expanded_systems):
        """
        Extract zone and system branch objects by loop type and store in epJSON formatted dictionary

        :param plant_loop_class_object: ExpandPlantLoop class object
        :param expanded_zones: ExpandZone objects
        :param expanded_systems: ExpandSystem objects
        :return: epJSON formatted dictionary of branch objects
        """
        # create list of regex matches for the given loop
        # todo_eo: object searching regex need to be expanded and/or optimized
        if 'chilledwater' in plant_loop_class_object.template_type.lower():
            branch_rgx = ['^Coil:Cooling:Water($|:DetailedGeometry)+', ]
        elif 'hotwater' in plant_loop_class_object.template_type.lower():
            branch_rgx = ['^Coil:Heating:Water($|:DetailedGeometry)+', '^ZoneHVAC:Baseboard.*Water']
        elif 'mixedwater' in plant_loop_class_object.template_type.lower():
            branch_rgx = ['^Coil:.*HeatPump.*', '^AirConditioner:VariableRefrigerantFlow$']
        elif 'condenserwater' in plant_loop_class_object.template_type.lower():
            return None
        else:
            InvalidTemplateException('an invalid loop type was specified when creating plant loop connections: {}'
                                     .format(plant_loop_class_object.template_type))
        branch_dictionary = {}
        object_list = [expanded_zones or {}, expanded_systems or {}]
        for class_object in object_list:
            for co in class_object.values():
                branch_objects = copy.deepcopy(co.epjson.get('Branch', {}))
                for branch_name, branch_structure in branch_objects.items():
                    # the regex check for 'main branch' is to avoid DualDuct main branches from accidentally being
                    # included since they have coil objects in them as well.  They typical main branch is never accidentally
                    # caught because the coil objects are never in the 0th position.
                    for br in branch_rgx:
                        if re.match(br, branch_structure['components'][0]['component_object_type']) and not \
                                re.match('.*main branch$', branch_name.lower()):
                            branch_dictionary.update({branch_name: branch_objects[branch_name]})
        if branch_dictionary:
            return {'Branch': branch_dictionary}
        else:
            return None

    def _split_supply_and_demand_side_branches(
            self,
            plant_loop_class_object,
            expanded_plant_equipment,
            expanded_systems,
            expanded_zones):
        """
        Separate plant equipment, zone, and system branches into supply and demand sides for a given ExpandPlantLoop
        object.

        :param plant_loop_class_object: ExpandPlantLoop class object
        :param expanded_plant_equipment: expanded dictionary of ExpandPlantEquipment objects
        :param expanded_systems: expanded dictionary of ExpandSystem objects
        :param expanded_zones: expanded dictionary of ExpandZone objects
        :return: tuple of demand and supply side branches for processing
        """
        # Get plant equipment, zone, and system branches
        plant_equipment_branch_dictionary = self._get_plant_equipment_waterloop_branches_by_loop_type(
            plant_loop_class_object=plant_loop_class_object,
            expanded_plant_equipment=expanded_plant_equipment
        )
        zone_system_branch_dictionary = self._get_zone_system_waterloop_branches_by_loop_type(
            plant_loop_class_object=plant_loop_class_object,
            expanded_zones=expanded_zones,
            expanded_systems=expanded_systems
        )
        # get branches in the loop
        demand_branches = {}
        # Special handling for condenser water loop where the chiller objects are the demand side.
        if 'condenserwater' in plant_loop_class_object.template_type.lower():
            pebd = copy.deepcopy(plant_equipment_branch_dictionary)
            for object_name, object_structure in plant_equipment_branch_dictionary['Branch'].items():
                try:
                    if re.match(r'Chiller:.*', object_structure['components'][0]['component_object_type']):
                        demand_branches.update({object_name: pebd['Branch'].pop(object_name)})
                except (AttributeError, KeyError):
                    raise InvalidTemplateException('Branch object is incorrectly formatted: {}'
                                                   .format(plant_equipment_branch_dictionary))
            supply_branches = pebd['Branch']
        else:
            demand_branches = zone_system_branch_dictionary.get('Branch') if zone_system_branch_dictionary else None
            supply_branches = plant_equipment_branch_dictionary.get('Branch') \
                if plant_equipment_branch_dictionary else None
        return demand_branches, supply_branches

    def _create_water_loop_connectors_and_nodelist(
            self,
            plant_loop_class_object,
            expanded_plant_equipment,
            expanded_zones=None,
            expanded_systems=None):
        """
        Create Branchlist, Connector, ConnectorList, and supply NodeLists objects that connect the PlantLoop to supply
        and demand water objects.  This operation is performed outside of ExpandObjects because it requires outputs
        from ExpandPlantEquipment, ExpandZone, and ExpandSystem objects.

        :param plant_loop_class_object: ExpandPlantLoop class object
        :param expanded_plant_equipment: expanded dictionary of ExpandPlantEquipment objects
        :param expanded_systems: expanded dictionary of ExpandSystem objects
        :param expanded_zones: expanded dictionary of ExpandZone objects
        :return: Updated class epjson attribute with Branchlist, Connector, and ConnectorList objects.
        """
        # Get plant equipment, zone, and system branches.  Split them into demand and supply sides
        demand_branches, supply_branches = self._split_supply_and_demand_side_branches(
            plant_loop_class_object=plant_loop_class_object,
            expanded_plant_equipment=expanded_plant_equipment,
            expanded_systems=expanded_systems,
            expanded_zones=expanded_zones
        )
        # check to make sure loops aren't empty
        if not demand_branches or not supply_branches:
            raise InvalidTemplateException('Demand or supply branches are empty for water loop connectors: Demand: {}, '
                                           'Supply: {}, Loop {}'.format(demand_branches, supply_branches,
                                                                        plant_loop_class_object.template_type))
        # Use ExpandObjects class for helper functions
        eo = ExpandObjects()
        eo.unique_name = getattr(plant_loop_class_object, 'template_name')
        # create branchlists
        demand_branchlist = eo.get_structure(
            structure_hierarchy=['AutoCreated', 'PlantLoop', 'BranchList', 'Demand'])
        supply_branchlist = eo.get_structure(
            structure_hierarchy=['AutoCreated', 'PlantLoop', 'BranchList', 'Supply'])
        # create connector objects
        connector_demand_splitter = eo.get_structure(
            structure_hierarchy=['AutoCreated', 'PlantLoop', 'Connector', 'Splitter', 'Demand'])
        connector_demand_mixer = eo.get_structure(
            structure_hierarchy=['AutoCreated', 'PlantLoop', 'Connector', 'Mixer', 'Demand'])
        connector_supply_splitter = eo.get_structure(
            structure_hierarchy=['AutoCreated', 'PlantLoop', 'Connector', 'Splitter', 'Supply'])
        connector_supply_mixer = eo.get_structure(
            structure_hierarchy=['AutoCreated', 'PlantLoop', 'Connector', 'Mixer', 'Supply'])
        # create supply nodelist
        supply_nodelist = eo.get_structure(
            structure_hierarchy=['AutoCreated', 'PlantLoop', 'NodeList', 'Supply'])
        # apply branches
        try:
            for branch in demand_branches:
                demand_branchlist['branches'].insert(1, {'branch_name': branch})
                connector_demand_splitter['branches'].insert(0, {'outlet_branch_name': branch})
                connector_demand_mixer['branches'].insert(0, {'inlet_branch_name': branch})
            for branch in supply_branches:
                supply_branchlist['branches'].insert(1, {'branch_name': branch})
                connector_supply_splitter['branches'].insert(0, {'outlet_branch_name': branch})
                connector_supply_mixer['branches'].insert(0, {'inlet_branch_name': branch})
                supply_nodelist['nodes'].insert(
                    0,
                    {'node_name': supply_branches[branch]['components'][0]['component_outlet_node_name']})
        except (KeyError, AttributeError):
            raise PyExpandObjectsYamlStructureException('AutoCreated PlantLoop Connector YAML object was '
                                                        'improperly formatted')
        # add connector list
        demand_connectorlist = eo.get_structure(
            structure_hierarchy=['AutoCreated', 'PlantLoop', 'ConnectorList', 'Demand']
        )
        supply_connectorlist = eo.get_structure(
            structure_hierarchy=['AutoCreated', 'PlantLoop', 'ConnectorList', 'Supply']
        )
        # format yaml objects into epJSON dictionaries, resolve, and output
        connector_dictionary = eo.yaml_list_to_epjson_dictionaries(
            yaml_list=[
                {'BranchList': demand_branchlist},
                {'BranchList': supply_branchlist},
                {'Connector:Splitter': connector_demand_splitter},
                {'Connector:Splitter': connector_supply_splitter},
                {'Connector:Mixer': connector_demand_mixer},
                {'Connector:Mixer': connector_supply_mixer},
                {'ConnectorList': demand_connectorlist},
                {'ConnectorList': supply_connectorlist},
                {'NodeList': supply_nodelist}
            ])
        resolved_path_dictionary = eo.resolve_objects(epjson=connector_dictionary)
        # save output to class epsjon
        self.merge_epjson(
            super_dictionary=self.epjson,
            object_dictionary=resolved_path_dictionary
        )
        return

    def _create_plant_equipment_lists(
            self,
            plant_loop_class_object,
            expanded_plant_equipment):
        """
        Create PlantEquipmentList and CondenserEquipmentList for a given ExpandPlantLoop class object.
        This operation is performed outside of ExpandObjects because it requires outputs from
        ExpandPlantEquipment objects.

        :param plant_loop_class_object: ExpandPlantLoop class object
        :param expanded_plant_equipment: expanded dictionary of ExpandPlantEquipment objects
        :return: Updated class epjson attribute with PlantEquipmentList or CondenserEquipmentlist.
        """
        # Get plant equipment, zone, and system branches.  Split them into demand and supply sides
        _, supply_branches = self._split_supply_and_demand_side_branches(
            plant_loop_class_object=plant_loop_class_object,
            expanded_plant_equipment=expanded_plant_equipment,
            expanded_systems=None,
            expanded_zones=None
        )
        equipment = []
        # Extract priority from each equipment object referenced by the branch and use it to order the equipment list
        supply_branches_with_priority = []
        for sb in supply_branches.values():
            for equipment_name, equipment_objects in expanded_plant_equipment.items():
                if equipment_objects.template_type == 'HVACTemplate:Plant:Boiler:ObjectReference':
                    equipment_name = equipment_objects.boiler_name
                elif equipment_objects.template_type == 'HVACTemplate:Plant:Chiller:ObjectReference':
                    equipment_name = equipment_objects.chiller_name
                elif equipment_objects.template_type == 'HVACTemplate:Plant:Tower:ObjectReference':
                    equipment_name = equipment_objects.cooling_tower_name
                if sb['components'][0]['component_name'] == equipment_name:
                    equipment_epjson = equipment_objects.epjson[
                        sb['components'][0]['component_object_type']][sb['components'][0]['component_name']]
                    # make tuple of (object, priority)
                    # if priority isn't set, use infinity to push it to the end when sorted
                    supply_branches_with_priority.append((sb, equipment_epjson.get('priority', float('inf'))))
        supply_branches_ordered = [
            branch for branch, priority
            in sorted(supply_branches_with_priority, key=lambda s: s[1])]
        for sb in supply_branches_ordered:
            equipment.append({
                'equipment_name': sb['components'][0]['component_name'],
                'equipment_object_type': sb['components'][0]['component_object_type']
            })
        # use ExpandObjects functions
        eo = ExpandObjects()
        eo.unique_name = getattr(plant_loop_class_object, 'template_name')
        if 'hotwater' in plant_loop_class_object.template_type.lower() or \
                'chilledwater' in plant_loop_class_object.template_type.lower():
            list_dictionary = \
                eo.get_structure(structure_hierarchy=['AutoCreated', 'PlantLoop', 'PlantEquipmentList'])
            list_dictionary['equipment'] = equipment
            equipment_list_dictionary = [{'PlantEquipmentList': list_dictionary}, ]
        elif 'mixedwater' in plant_loop_class_object.template_type.lower():
            heating_equipment = [i for i in equipment if re.match(r'Boiler:.*', i['equipment_object_type'])]
            heating_list_dictionary = \
                eo.get_structure(structure_hierarchy=['AutoCreated', 'PlantLoop', 'PlantEquipmentListMixedWaterHeating'])
            heating_list_dictionary['equipment'] = heating_equipment
            cooling_equipment = [i for i in equipment if re.match(r'CoolingTower:.*', i['equipment_object_type'])]
            cooling_list_dictionary = \
                eo.get_structure(structure_hierarchy=['AutoCreated', 'PlantLoop', 'PlantEquipmentListMixedWaterCooling'])
            cooling_list_dictionary['equipment'] = cooling_equipment
            equipment_list_dictionary = [
                {'PlantEquipmentList': cooling_list_dictionary},
                {'PlantEquipmentList': heating_list_dictionary}]
        elif 'condenserwater' in plant_loop_class_object.template_type.lower():
            list_dictionary = \
                eo.get_structure(structure_hierarchy=['AutoCreated', 'PlantLoop', 'CondenserEquipmentList'])
            list_dictionary['equipment'] = equipment
            equipment_list_dictionary = [{'CondenserEquipmentList': list_dictionary}, ]
        else:
            raise InvalidTemplateException('an invalid loop type was specified when creating plant loop connections: {}'
                                           .format(plant_loop_class_object.template_type))
        equipment_list_formatted_dictionary = eo.yaml_list_to_epjson_dictionaries(
            yaml_list=equipment_list_dictionary)
        resolved_path_dictionary = eo.resolve_objects(epjson=equipment_list_formatted_dictionary)
        # save output to class epsjon
        self.merge_epjson(
            super_dictionary=self.epjson,
            object_dictionary=resolved_path_dictionary)
        return

    def _apply_system_fields_to_zone_template(self, template_fields, system_templates):
        """
        Set zone attributes based on system templates where appropriate
        :param template_fields: HVACTemplate:Zone fields
        :param system_templates: dictionary of HVACTemplate:System objects
        :return: None.  the zone template is updated in the class attributes
        """
        # make a tuple of fields that identify the system
        system_identifiers = (
            'template_constant_volume_system_name',
            'dedicated_outdoor_air_system_name',
            'template_dual_duct_system_name',
            'template_unitary_system_name',
            'template_vav_system_name',
            'template_vrf_system_name')
        # get system to zone mapping structure
        eo = ExpandObjects()
        mapping_indicators = eo.get_structure(structure_hierarchy=['SystemToZoneMappings'])
        # retrieve system from zone template
        reference_system_name = None
        for si in system_identifiers:
            reference_system_name = template_fields.get(si, None)
            if reference_system_name:
                break
        if not reference_system_name:
            return
        try:
            # iterate over systems
            for system_template in system_templates.values():
                for system_name, system_fields in system_template.items():
                    # if a match is found, apply the map
                    if reference_system_name == system_name:
                        for mi in mapping_indicators:
                            for zone_field, mapping_instructions in mi.items():
                                for val, value_map in mapping_instructions.items():
                                    if template_fields.get(zone_field, None) == val:
                                        if value_map.get('system_field') and system_fields.get(value_map['system_field']):
                                            try:
                                                template_fields[value_map['zone_field']] = \
                                                    system_fields[value_map['system_field']]
                                                if val == 'SystemSupplyAirTemperature':
                                                    template_fields[zone_field] = 'SupplyAirTemperature'
                                            except (ValueError, KeyError):
                                                self.logger.info('Zone field {} does not exist for mapping'
                                                                 'values: {}'.format(value_map['zone_field'], value_map))
        except ValueError:
            raise InvalidTemplateException("Mapping of system to zone variables failed. zone_template: {}, "
                                           "system template: {}".format(template_fields, system_templates))
        return

    def run(self, input_epjson=None):
        """
        Execute HVAC Template process workflow

        :param input_epjson: input epJSON file
        :return: epJSON containing expanded objects from templates
        """
        # output_epJSON
        # flush the stream handler
        # self.logger.stream_flush
        if not input_epjson:
            if self.input_epjson:
                input_epjson = self.input_epjson
            else:
                raise InvalidEpJSONException("No epJSON file loaded or provided to HVACTemplate processor")
        self.epjson_process(epjson_ref=input_epjson)
        self.logger.info('##### PreProcessing Data #####')
        self._hvac_template_preprocess(epjson=self.input_epjson)
        for zone_templates in self.templates_zones.values():
            for template_fields in zone_templates.values():
                self._apply_system_fields_to_zone_template(
                    template_fields=template_fields,
                    system_templates=self.templates_systems)
        self.logger.info('##### Processing Thermostats #####')
        self.expanded_thermostats = self._expand_templates(
            templates=self.templates_thermostats,
            expand_class=ExpandThermostat)
        self.logger.info('##### Processing Zones #####')
        self.expanded_zones = self._expand_templates(
            templates=self.templates_zones,
            expand_class=ExpandZone)
        self.logger.info('##### Processing Systems #####')
        self.expanded_systems = self._expand_templates(
            templates=self.templates_systems,
            expand_class=ExpandSystem)
        self.logger.info('##### Building Zone-Thermostat Connections #####')
        for _, zone_class_object in self.expanded_zones.items():
            self._create_zonecontrol_thermostat(zone_class_object=zone_class_object)
        self.logger.info('##### Building System-Zone Connections #####')
        for _, system_class_object in self.expanded_systems.items():
            # VRF systems do not connect via air paths, and need a separate function.
            if system_class_object.template_type == 'HVACTemplate:System:VRF':
                self._create_system_vrf_path_connection_objects(
                    system_class_object=system_class_object,
                    expanded_zones=self.expanded_zones)
            else:
                self._create_system_path_connection_objects(
                    system_class_object=system_class_object,
                    expanded_zones=self.expanded_zones)
        self.logger.info('##### Processing Plant Loops #####')
        self.expanded_plant_loops = self._expand_templates(
            templates=self.templates_plant_loops,
            expand_class=ExpandPlantLoop)
        self.logger.info('##### Processing Plant Equipment #####')
        self.expanded_plant_equipment = self._expand_templates(
            templates=self.templates_plant_equipment,
            expand_class=ExpandPlantEquipment,
            plant_loop_class_objects=self.expanded_plant_loops)
        # Pass through expanded plant equipment objects to create additional plant loops and equipment if necessary
        self._create_additional_plant_loops_and_equipment_from_equipment(
            expanded_plant_equipment=self.expanded_plant_equipment,
            expanded_plant_loops=self.expanded_plant_loops
        )
        self.logger.info('##### Building Plant-Plant Equipment Connections #####')
        for expanded_pl in self.expanded_plant_loops.values():
            self._create_water_loop_connectors_and_nodelist(
                plant_loop_class_object=expanded_pl,
                expanded_plant_equipment=self.expanded_plant_equipment,
                expanded_systems=self.expanded_systems,
                expanded_zones=self.expanded_zones)
            self._create_plant_equipment_lists(
                plant_loop_class_object=expanded_pl,
                expanded_plant_equipment=self.expanded_plant_equipment)
        self.logger.info('##### Creating epJSON #####')
        # Merge each set of epJSON dictionaries
        merge_list = [
            self.epjson,
            self.base_objects,
            *[j.epjson for i, j in self.expanded_thermostats.items()],
            *[j.epjson for i, j in self.expanded_zones.items()],
            *[j.epjson for i, j in self.expanded_systems.items()],
            *[j.epjson for i, j in self.expanded_plant_loops.items()],
            *[j.epjson for i, j in self.expanded_plant_equipment.items()]]
        output_epjson = {}
        for merge_dictionary in merge_list:
            self.merge_epjson(
                super_dictionary=output_epjson,
                object_dictionary=merge_dictionary)
        # Use this for file debugging
        # import json
        # with open('test.epJSON', 'w') as base_file:
        #     json.dump(output_epjson, base_file, indent=4, sort_keys=True)
        # Create output format
        output_epjson = {
            "epJSON": output_epjson,
            "epJSON_base": self.base_objects,
            "epJSON_hvac_templates": self.templates,
            'outputPreProcessorMessage': self.stream.getvalue()
        }
        return output_epjson
