import re
from epjson_handler import EPJSON
from expand_objects import ExpandThermostat, ExpandObjects

from custom_exceptions import InvalidTemplateException


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
        self.expanded_thermostats = []
        self.epjson = {}
        return

    def hvac_template_preprocess(self, epjson):
        """
        Organize epJSON and assign objects to specific class attributes

        :param epjson: Input epJSON object
        :return: organized epJSON template objects into templates, and templates_* as class variables..
        """
        self.logger.info('##### HVACTemplate #####')
        for object_type, object_structure in epjson.items():
            if re.match('^HVACTemplate:*', object_type):
                if re.match('^HVACTemplate:Thermostat$', object_type):
                    self.templates_thermostats = self.merge_epjson(
                        super_dictionary=self.templates_thermostats,
                        object_dictionary={object_type: object_structure},
                        unique_name_override=False)
                elif re.match('^HVACTemplate:Zone:('
                              'IdealLoadsAirSystem|BaseboardHeat|FanCoil|PTAC|PTHP|WaterToAirHeatPump|'
                              'VRF|Unitary|VAV|VAV:FanPowered|VAVHeatAndCool|ConstantVolumn|DualDuct)$',
                              object_type):
                    self.templates_zones = self.merge_epjson(
                        super_dictionary=self.templates_zones,
                        object_dictionary={object_type: object_structure},
                        unique_name_override=False)
                elif re.match('^HVACTemplate:System:('
                              'VRF|Unitary|UnitaryHeatPump:AirToAir|UnitarySystem|VAV|PackagedVAV|'
                              'ConstantVolume|DualDuct|DedicatedOutdoorAir'
                              ')$', object_type):
                    self.templates_systems = self.merge_epjson(
                        super_dictionary=self.templates_systems,
                        object_dictionary={object_type: object_structure},
                        unique_name_override=False)
                elif re.match('^HVACTemplate:Plant:(ChilledWater|HotWater|MixedWater)Loop$', object_type):
                    self.templates_plant_loops = self.merge_epjson(
                        super_dictionary=self.templates_plant_loops,
                        object_dictionary={object_type: object_structure},
                        unique_name_override=False)
                elif re.match('^HVACTemplate:Plant:(Chiller|Tower|Boiler)(ObjectReference)*$', object_type):
                    self.templates_plant_equipment = self.merge_epjson(
                        super_dictionary=self.templates_plant_equipment,
                        object_dictionary={object_type: object_structure},
                        unique_name_override=False)
                else:
                    raise InvalidTemplateException(
                        'Template object type {} was not recognized'.format(object_type))
                # store original templates into dictionary
                self.templates = self.merge_epjson(
                    super_dictionary=self.templates,
                    object_dictionary={object_type: object_structure},
                    unique_name_override=False)
            else:
                self.base_objects = self.merge_epjson(
                    super_dictionary=self.base_objects,
                    object_dictionary={object_type: object_structure},
                    unique_name_override=False)
        return

    def get_thermostat_template_from_zone_template(self, zone_template):
        """
        Retrieve thermostat template from zone template field

        :param zone_template: HVACTemplate:Zone:.* object
        :return: HVACTemplate:Thermostat object
        """
        # zone template should be only one epJSON object
        # todo_eo: need to capture errors here.
        (template_type, object_structure), = zone_template.items()
        (_, object_fields), = object_structure.items()
        template_thermostat_name = object_fields.get('template_thermostat_name', None)
        if template_thermostat_name:
            try:
                return self.expanded_thermostats[template_thermostat_name]
            except KeyError:
                raise InvalidTemplateException("{} references invalid HVACTemplate:Thermostat: {}"
                                               .format(template_type, template_thermostat_name))
        else:
            return None

    def create_zonecontrol_thermostat(self, zone_template):
        """
        Create ZoneControl:Thermostat objects, which require a connection between
        HVACTemplate:Zone and HVACTemplate:Thermostat objects

        :return: Updated class epJSON dictionary with ThermostatSetpoint objects added.  Objects are also added
            to the class self.epsjon dictionary.
        """
        thermostat_template = self.get_thermostat_template_from_zone_template(zone_template)
        (_, zone_template_structure), = zone_template.items()
        (_, zone_template_fields), = zone_template_structure.items()
        try:
            zone_name = zone_template_fields.get('zone_name')
            (thermostat_type, thermostat_structure), = thermostat_template.epjson.items()
            (thermostat_name, _), = thermostat_structure.items()
            if thermostat_type == "ThermostatSetpoint:DualSetpoint":
                # add always_val schedule to epjson
                control_schedule = ExpandObjects().build_compact_schedule(
                    structure_hierarchy=['Schedule', 'Compact', 'ALWAYS_VAL'],
                    insert_values=[4, ])
                # todo_eo: one elif for each schedule type
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
            self.epjson = self.merge_epjson(
                super_dictionary=self.epjson,
                object_dictionary=dict(control_schedule, **zonecontrol_thermostat),
                unique_name_override=True
            )
            return dict(control_schedule, **zonecontrol_thermostat)
        except (ValueError, AttributeError, KeyError):
            raise InvalidTemplateException("HVACTemplate failed to build ZoneControl:Thermostat from zone template "
                                           "{}".format(zone_template))

    def expand_templates(self, templates, expand_class):
        """
        Run ExpandThermostat on multiple templates
        :param templates: dictionary of HVACTemplate:.* objects
        :param expand_class: ExpandObjects child class to operate on template.
        :return: dictionary of expanded objects with unique name as key
        """
        expanded_template_dictionary = {}
        templates = self.unpack_epjson(templates)
        for template in templates:
            (_, template_structure), = template.items()
            (template_name, _), = template_structure.items()
            expanded_template = expand_class(template).run()
            expanded_template_dictionary[template_name] = expanded_template
        return expanded_template_dictionary

    def run(self, input_epjson):
        """
        Execute HVAC Template process workflow

        :param input_epjson: input epJSON file
        :return: epJSON containing expanded objects from templates
        """
        # output_epJSON
        # flush the stream handler
        self.logger.stream_flush
        self.epjson_process(epjson_ref=input_epjson)
        self.hvac_template_preprocess(epjson=self.input_epjson)
        self.logger.info('##### Processing Thermostats #####')
        self.expanded_thermostats = self.expand_templates(
            templates=self.templates_thermostats,
            expand_class=ExpandThermostat)
        self.logger.info('##### Processing Zones #####')
        self.logger.info('##### Building Connections #####')
        # self.create_zonecontrol_thermostat()
        self.logger.info('##### Creating epJSON #####')
        # start by merging non-template and connector objects
        output_epjson = self.merge_epjson(
            super_dictionary=self.base_objects,
            object_dictionary=self.epjson
        )
        # merge each ExpandObjects child class created
        epjson_objects = [j.epjson for i, j in self.expanded_thermostats.items()]
        for eo in epjson_objects:
            output_epjson = self.merge_epjson(
                super_dictionary=output_epjson,
                object_dictionary=eo
            )
        # Create output format
        output_epjson = {
            "epJSON": output_epjson,
            "epJSON_base": self.base_objects,
            "epJSON_hvac_templates": self.templates,
            'outputPreProcessorMessage': self.stream.getvalue()
        }
        return output_epjson
