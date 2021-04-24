import re
import copy
from epjson_handler import EPJSON
from expand_objects import ExpandObjects, ExpandThermostat, ExpandZone, ExpandSystem, ExpandPlantLoop, \
    ExpandPlantEquipment
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
            (template_name, _), = template_structure.items()
            expanded_template = expand_class(template=template, **kwargs).run()
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
                    structure_hierarchy=['CommonObjects', 'Schedule', 'Compact', 'ALWAYS_VAL'],
                    insert_values=[1, ])
            elif thermostat_type == "ThermostatSetpoint:SingleCooling":
                control_schedule = ExpandObjects().build_compact_schedule(
                    structure_hierarchy=['CommonObjects', 'Schedule', 'Compact', 'ALWAYS_VAL'],
                    insert_values=[2, ])
            elif thermostat_type == "ThermostatSetpoint:DualSetpoint":
                control_schedule = ExpandObjects().build_compact_schedule(
                    structure_hierarchy=['CommonObjects', 'Schedule', 'Compact', 'ALWAYS_VAL'],
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
            supply_object = eo.get_structure(structure_hierarchy=[
                'AutoCreated', 'System', 'AirLoopHVAC', 'SupplyPlenum', 'Base'])
            supply_object['nodes'] = zone_splitters
            supply_object = {'AirLoopHVAC:SupplyPlenum': supply_object}
        else:
            supply_object = eo.get_structure(structure_hierarchy=[
                'AutoCreated', 'System', 'AirLoopHVAC', 'ZoneSplitter', 'Base'])
            supply_object['nodes'] = zone_splitters
            supply_object = {'AirLoopHVAC:ZoneSplitter': supply_object}
        return_plenum_name = getattr(system_class_object, 'return_plenum_name', None)
        if return_plenum_name:
            # set return plenum name attribute for transition and mapping processing
            eo.return_plenum_name = return_plenum_name
            return_object = eo.get_structure(structure_hierarchy=[
                'AutoCreated', 'System', 'AirLoopHVAC', 'ReturnPlenum', 'Base'])
            return_object['nodes'] = zone_mixers
            return_object = {'AirLoopHVAC:ReturnPlenum': return_object}
        else:
            return_object = eo.get_structure(structure_hierarchy=[
                'AutoCreated', 'System', 'AirLoopHVAC', 'ZoneMixer', 'Base'])
            return_object['nodes'] = zone_mixers
            return_object = {'AirLoopHVAC:ZoneMixer': return_object}
        # Add Path objects
        supply_path_object = {'AirLoopHVAC:SupplyPath':
                              eo.get_structure(structure_hierarchy=[
                                  'AutoCreated', 'System', 'AirLoopHVAC', 'SupplyPath', 'Base'])}
        return_path_object = {'AirLoopHVAC:ReturnPath':
                              eo.get_structure(structure_hierarchy=[
                                  'AutoCreated', 'System', 'AirLoopHVAC', 'ReturnPath', 'Base'])}
        path_dictionary = eo.yaml_list_to_epjson_dictionaries(
            yaml_list=[supply_object, return_object, supply_path_object, return_path_object])
        resolved_path_dictionary = eo.resolve_objects(epjson=path_dictionary)
        # save output to class epsjon
        self.merge_epjson(
            super_dictionary=self.epjson,
            object_dictionary=resolved_path_dictionary
        )
        return resolved_path_dictionary

    def _create_loop_template_from_plant_equipment(self, plant_equipment_class_object, plant_loop_class_objects):
        """
        Create plant loop templates from ExpandPlantEquipment object attributes.  These outputs will be used as inputs
        to the initialize a new ExpandPlantLoop class.  This process must be performed because ExpandPlantLoop must be
        run before ExpandPlantEquipment.  However, certain equipment inputs can cause for new loops to be created.

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
            # try to get the chilled water loop attributes to transition to condneser water
            chw_loop = [
                pl for pl
                in plant_loop_class_objects.values()
                if getattr(pl, 'template_type').lower() == 'hvactemplate:plant:chilledwaterloop']
            cndw_attributes = {}
            if chw_loop:
                for cndw_attribute, chw_attribute in zip(
                        ['condenser_water_pump_rated_head'],
                        ['primary_chilled_water_pump_rated_head']):
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
        return plant_loop_dictionary

    def _create_additional_plant_loops_from_equipment(
            self,
            plant_equipment_class_objects,
            plant_loop_class_objects):
        """
        Create additional HVACTemplate:Plant:.*Loops based on HVACTemplate:Plant:(Chiller|Tower|Boiler) inputs

        :param plant_equipment_class_objects: ExpandPlantEquipment objects
        :param plant_loop_class_objects: ExpandPlantLoop objects
        :return: Additional plant loop templates and objects added to the class attributes
        """
        for epl_name, epl in plant_equipment_class_objects.items():
            plant_loop_template = self._create_loop_template_from_plant_equipment(
                plant_equipment_class_object=epl,
                plant_loop_class_objects=plant_loop_class_objects)
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
                        if expanded_name not in plant_loop_class_objects.keys():
                            plant_loop_class_objects[expanded_name] = expanded_object
                except (AttributeError, ValueError):
                    InvalidTemplateException('A Plant loop was specified to be created from a plant equipment object '
                                             '{}, but the process failed to attach the create objects'
                                             .format(epl_name))
        return

    @staticmethod
    def _get_plant_equipment_waterloop_branches_by_loop_type(loop_type, plant_equipment_class_objects):
        """
        Extract plant equipment branches by loop type and store in epJSON formatted dictionary

        :param loop_type: loop template type (HVACTemplate:Plant:.*Loop) format
        :param plant_equipment_class_objects: dictionary of ExpandPlantEquipment objects
        :return: epJSON formatted dictionary of branch objects for loop connections
        """
        branch_dictionary = {}
        for pe in plant_equipment_class_objects.values():
            branch_objects = copy.deepcopy(pe.epjson.get('Branch', {}))
            # Special handling for chillers with condenser water and chilled water branches
            if pe.template_type == 'HVACTemplate:Plant:Chiller' and getattr(pe, 'condenser_type', None) == 'WaterCooled':
                for branch_name, branch_structure in branch_objects.items():
                    if 'chilledwater' in loop_type.lower() and 'chw' in branch_name.lower():
                        branch_dictionary.update({branch_name: branch_objects[branch_name]})
                    if 'condenserwater' in loop_type.lower() and 'cnd' in branch_name.lower():
                        branch_dictionary.update({branch_name: branch_objects[branch_name]})
            # typical handling when all plant equipment branches belong in one loop
            elif pe.template_plant_loop_type in loop_type:
                branch_dictionary.update(branch_objects)
        if branch_dictionary:
            return {'Branch': branch_dictionary}
        else:
            return None

    @staticmethod
    def _get_zone_system_waterloop_branches_by_loop_type(loop_type, zone_class_objects, system_class_objects):
        """
        Extract zone and system branch objects by loop type and store in epJSON formatted dictionary

        :param loop_type: loop template type (HVACTemplate:Plant:.*Loop) format
        :param zone_class_objects: ExpandZone objects
        :param system_class_objects: ExpandSystem objects
        :return: epJSON formatted dictionary of branch objects
        """
        # create list of regex matches for the given loop
        if 'chilledwater' in loop_type.lower():
            branch_rgx = ['^Coil:Cooling:Water.*', ]
        elif 'hotwater' in loop_type.lower():
            branch_rgx = ['^Coil:Heating:Water.*', '^ZoneHVAC:Baseboard.*Water']
        elif 'mixedwater' in loop_type.lower():
            branch_rgx = ['^Coil:.*HeatPump.*']
        else:
            InvalidTemplateException('an invalid loop type was specified when creating plant loop connections: {}'
                                     .format(loop_type))
        branch_dictionary = {}
        object_list = [zone_class_objects, system_class_objects]
        for class_object in object_list:
            for co in class_object.values():
                branch_objects = copy.deepcopy(co.epjson.get('Branch', {}))
                for branch_name, branch_structure in branch_objects.items():
                    for br in branch_rgx:
                        if re.match(br, branch_structure['components'][0]['component_object_type']):
                            branch_dictionary.update({branch_name: branch_objects[branch_name]})
        if branch_dictionary:
            return {'Branch': branch_dictionary}
        else:
            return None

    # @staticmethod
    # def _create_water_loop_connectors(
    #         loop_type,
    #         plant_equipment_branch_dictionary,
    #         zone_system_branch_dictionary={}):
    #     connector_objects = {
    #         'BranchList': {},
    #         'Connector:Mixer': {},
    #         'Connector:Splitter': {},
    #         'ConnectorList': {}
    #     }
    #     demand_branches = {}
    #     supply_branches = {}
    #     # Special handling for chilled water loop
    #     if 'condenserwater' in loop_type.lower():
    #         pebd = copy.deepcopy(plant_equipment_branch_dictionary)
    #         for object_name, object_structure in plant_equipment_branch_dictionary['Branch'].items():
    #             if re.match(r'Chiller:.*', object_structure['components'][0]['component_object_type']):
    #                 demand_branches.update({object_name: pebd['Branch'].pop(object_name)})
    #         supply_branches = pebd['Branch']
    #     else:
    #         demand_branches = zone_system_branch_dictionary
    #         supply_branches = plant_equipment_branch_dictionary
    #     # check to make sure loops aren't empty
    #     if not demand_branches or not supply_branches:
    #         raise InvalidTemplateException('Demand or supply branches are empty for water loop connectors: Demand: {}, '
    #                                        'Supply: {}, Loop {}'.format(demand_branches, supply_branches, loop_type))
    #     formatted_demand_branchlist = [{"branch_name": i} for i in demand_branches.keys()]
    #     formatted_supply_branchlist = [{"branch_name": i} for i in supply_branches.keys()]
    #     print(formatted_demand_branchlist)
    #     print(formatted_supply_branchlist)
    #     # todo_eo: build objects from formatted lists
    #     return

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
        self.expanded_plant_loops = self._expand_templates(
            templates=self.templates_plant_loops,
            expand_class=ExpandPlantLoop)
        self.logger.info('##### Processing Plant Equipment #####')
        self.expanded_plant_equipment = self._expand_templates(
            templates=self.templates_plant_equipment,
            expand_class=ExpandPlantEquipment,
            plant_loop_class_objects=self.expanded_plant_loops)
        # Pass through expanded plant equipment objects to create additional plant loops if necessary
        self._create_additional_plant_loops_from_equipment(
            plant_equipment_class_objects=self.expanded_plant_equipment,
            plant_loop_class_objects=self.expanded_plant_loops
        )
        self.logger.info('##### Building Plant-Plant Equipment Connections #####')

        # todo_eo: ExpandPlantEquipment class has template_plant_loop_type attribute which indicates which loop to
        #  attach to.  Use that for the connections.
        self.logger.info('##### Building Plant-Demand equipment Connections #####')
        # get water loop branches from class objects
        self.logger.info('##### Creating epJSON #####')
        # Merge each set of epJSON dictionaries
        merge_list = [
            self.epjson,
            self.base_objects,
            *[j.epjson for i, j in self.expanded_thermostats.items()],
            *[j.epjson for i, j in self.expanded_zones.items()],
            *[j.epjson for i, j in self.expanded_systems.items()],
            *[j.epjson for i, j in self.expanded_plant_loops.items()]
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
