import re
from epjson_handler import EPJSON
from expand_objects import ExpandObjects, ExpandThermostat, ExpandZone, ExpandSystem

from custom_exceptions import InvalidTemplateException, InvalidEpJSONException


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
        self.expanded_plant_equipment = {}
        self.expanded_plant_loops = {}
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
                              'IdealLoadsAirSystem|BaseboardHeat|FanCoil|PTAC|PTHP|WaterToAirHeatPump|'
                              'VRF|Unitary|VAV|VAV:FanPowered|VAVHeatAndCool|ConstantVolumn|DualDuct)$',
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
                elif re.match('^HVACTemplate:Plant:(Chiller|Tower|Boiler)(ObjectReference)*$', object_type):
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

    def _expand_templates(self, templates, expand_class):
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
            (template_name, _), = template_structure.items()
            expanded_template = expand_class(template).run()
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
                    structure_hierarchy=['Schedule', 'Compact', 'ALWAYS_VAL'],
                    insert_values=[1, ])
            elif thermostat_type == "ThermostatSetpoint:SingleCooling":
                control_schedule = ExpandObjects().build_compact_schedule(
                    structure_hierarchy=['Schedule', 'Compact', 'ALWAYS_VAL'],
                    insert_values=[2, ])
            elif thermostat_type == "ThermostatSetpoint:DualSetpoint":
                control_schedule = ExpandObjects().build_compact_schedule(
                    structure_hierarchy=['Schedule', 'Compact', 'ALWAYS_VAL'],
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
                                           "{}".format(zone_class_object.unique_name))

    @staticmethod
    def _get_zone_template_field_from_system_type(template_type):
        """
        Retrieve the corresponding zone field name for a system template type
        :param template_type: HVACTemplate object type
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
        :param expanded_zones: list of ExpandZone objects
        :return: system supply air connection objects.  AirLoopHVAC:SupplyPath object and either
            AirLoopHVAC:SupplyPlenum or AirLoopHVAC:ZoneSplitter object as well ass AirLoopHVAC:ReturnPath and either
            AirLoopHVAC:ReturnPlenum or AirLoopHVAC:ZoneMixer.
        """
        zone_system_template_field_name = \
            self._get_zone_template_field_from_system_type(template_type=system_class_object.template_type)
        zone_splitters = []
        zone_mixers = []
        # iterate over expanded zones and if the system reference field exists, and is for the referenced system,
        # append them in the splitter and mixer lists
        for _, ez in expanded_zones.items():
            if getattr(ez, zone_system_template_field_name, None) == system_class_object.template_name:
                # todo_eo: Only AirTerminal has been used for this test when all zone equipment objects should be
                #  included.
                zone_equipment = self.get_epjson_objects(
                    epjson=ez.epjson,
                    object_type_regexp=r'^AirTerminal:.*'
                )
                try:
                    (zone_equipment_type, zone_equipment_structure), = zone_equipment.items()
                    (zone_equipment_name, zone_equipment_fields), = zone_equipment_structure.items()
                    outlet_node_name = zone_equipment_fields['air_inlet_node_name']
                except (KeyError, AttributeError, ValueError):
                    raise InvalidTemplateException('Search for zone equipment from Supply Path creation failed for '
                                                   'outlet node.  system {}, zone {}, zone equipment {}'
                                                   .format(system_class_object.template_name, ez.unique_name,
                                                           zone_equipment))
                try:
                    (zone_equipment_connection_name, zone_equipment_connection_fields), = \
                        ez.epjson['ZoneHVAC:EquipmentConnections'].items()
                    inlet_node_name = zone_equipment_connection_fields['zone_return_air_node_or_nodelist_name']
                except (KeyError, AttributeError, ValueError):
                    raise InvalidTemplateException('Search for ZoneHVAC:EquipmentConnections object from Supply '
                                                   'Path creation failed for inlet node.  system {}, zone {}'
                                                   .format(system_class_object.template_name, ez.unique_name))
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
        # create plenums or spliters/mixers, depending on template inputs
        # create ExpandObjects class object to use some yaml and epjson functions
        eo = ExpandObjects()
        eo.unique_name = getattr(system_class_object, 'template_name')
        supply_plenum_name = getattr(system_class_object, 'supply_plenum_name', None)
        if supply_plenum_name:
            # set return plenum name attribute for transition and mapping processing
            eo.supply_plenum_name = supply_plenum_name
            supply_object = eo.get_structure(structure_hierarchy=['AirLoopHVAC', 'SupplyPlenum', 'Base'])
            supply_object['nodes'] = zone_splitters
            supply_object = {'AirLoopHVAC:SupplyPlenum': supply_object}
        else:
            supply_object = eo.get_structure(structure_hierarchy=['AirLoopHVAC', 'ZoneSplitter', 'Base'])
            supply_object['nodes'] = zone_splitters
            supply_object = {'AirLoopHVAC:ZoneSplitter': supply_object}
        return_plenum_name = getattr(system_class_object, 'return_plenum_name', None)
        if return_plenum_name:
            # set return plenum name attribute for transition and mapping processing
            eo.return_plenum_name = return_plenum_name
            return_object = eo.get_structure(structure_hierarchy=['AirLoopHVAC', 'ReturnPlenum', 'Base'])
            return_object['nodes'] = zone_mixers
            return_object = {'AirLoopHVAC:ReturnPlenum': return_object}
        else:
            return_object = eo.get_structure(structure_hierarchy=['AirLoopHVAC', 'ZoneMixer', 'Base'])
            return_object['nodes'] = zone_mixers
            return_object = {'AirLoopHVAC:ZoneMixer': return_object}
        # Add Path objects
        supply_path_object = {'AirLoopHVAC:SupplyPath':
                              eo.get_structure(structure_hierarchy=['AirLoopHVAC', 'SupplyPath', 'Base'])}
        return_path_object = {'AirLoopHVAC:ReturnPath':
                              eo.get_structure(structure_hierarchy=['AirLoopHVAC', 'ReturnPath', 'Base'])}
        path_dictionary = eo.yaml_list_to_epjson_dictionaries(
            yaml_list=[supply_object, return_object, supply_path_object, return_path_object])
        resolved_path_dictionary = eo.resolve_objects(epjson=path_dictionary)
        # save output to class epsjon
        self.merge_epjson(
            super_dictionary=self.epjson,
            object_dictionary=resolved_path_dictionary
        )
        return resolved_path_dictionary

    def _create_loop_from_plant_equipment(self, plant_equipment_class_object, plant_loop_class_objects):
        """
        Create plant loop templates from ExpandPlantEquipment object attributes.  These outputs will be used as inputs
        to the intialize a new ExpandPlantLoop class.

        :param plant_equipment_class_object: ExpandPlantEquipment object
        :param plant_loop_class_objects: ExpandPlantLoop objects
        :return: Dictionary of HVAC:Template:Plant template objects to create an ExpandPlantLoop object
        """
        # create dictionary to store plant loops
        plant_loop_dictionary = {}
        # get each loop type specified in the existing plant loop class objects
        plant_loops = [getattr(pl, 'template_type').lower() for pl in plant_loop_class_objects.values()]
        # create condenser water loop for water cooled condensers
        if getattr(plant_equipment_class_object, 'template_type', None).lower() == 'hvactemplate:plant:chiller' \
                and getattr(plant_equipment_class_object, 'condenser_type', None).lower() == 'watercooled' \
                and 'hvactemplate:plant:condenserwaterloop' not in plant_loops:
            self.merge_epjson(
                super_dictionary=plant_loop_dictionary,
                object_dictionary={
                    'HVACTemplate:Plant:CondenserWaterLoop': {
                        'Condenser Water Loop': {
                            'template_plant_loop_type': 'CondenserWaterLoop'
                        }
                    }
                })
            # append plant loop to list to prevent another one being added.
            plant_loops.append('hvactemplate:plant:condenserwaterloop')
        return plant_loop_dictionary

    def run(self, input_epjson=None):
        """
        Execute HVAC Template process workflow

        :param input_epjson: input epJSON file
        :return: epJSON containing expanded objects from templates
        """
        # output_epJSON
        # flush the stream handler
        self.logger.stream_flush
        if not input_epjson:
            if self.input_epjson:
                input_epjson = self.input_epjson
            else:
                raise InvalidEpJSONException("No epJSON file loaded or provided to HVACTemplate processor")
        self.epjson_process(epjson_ref=input_epjson)
        self._hvac_template_preprocess(epjson=self.input_epjson)
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
            self._create_system_path_connection_objects(
                system_class_object=system_class_object,
                expanded_zones=self.expanded_zones)
        self.logger.info('##### Processing Plant Loops #####')
        self.logger.info('##### Processing Plant Equipment #####')
        self.logger.info('##### Building Plant-Plant Equipment Connections #####')
        # todo_eo: ExpandPlantEquipment class has plant_loop_type attribute which is a priority list of loops to
        #  attach the equipment.  Use that for the connections.
        self.logger.info('##### Building Plant-Demand equipment Connections #####')
        # get water loop branches from class objects
        self.logger.info('##### Creating epJSON #####')
        # Merge each set of epJSON dictionaries
        merge_list = [
            self.epjson,
            self.base_objects,
            *[j.epjson for i, j in self.expanded_thermostats.items()],
            *[j.epjson for i, j in self.expanded_zones.items()],
            *[j.epjson for i, j in self.expanded_systems.items()]
        ]
        output_epjson = {}
        for merge_dictionary in merge_list:
            self.merge_epjson(
                super_dictionary=output_epjson,
                object_dictionary=merge_dictionary
            )
        # Create output format
        output_epjson = {
            "epJSON": output_epjson,
            "epJSON_base": self.base_objects,
            "epJSON_hvac_templates": self.templates,
            'outputPreProcessorMessage': self.stream.getvalue()
        }
        return output_epjson
