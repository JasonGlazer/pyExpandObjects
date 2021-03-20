import re
from epjson_handler import EPJSON
from expand_objects import ExpandThermostat

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

    def create_zonecontrol_thermostat(self):
        """
        Create ZoneControl:Thermostat objects, which require a connection between
        HVACTemplate:Zone and HVACTemplate:Thermostat objects

        :return: Updated class epJSON dictionary with ThermostatSetpoint objects added.
        """
        # Iterate over expanded_zones (ExpandZone objects)
        # Get HVACTemplate:Thermostat name from template input (class attribute - template_thermostat_name)
        # Retrieve ExpandedThermostat object from expanded_thermostats [list(ExpandThermostat)]
        # with same name in attributes (template_name)
        # Get ThermostatSetpoint object from that object's epJSON attribute
        # Make zone control thermostat based on returned objects attributes
        # Store ZoneControl:Thermostat to HVACTemplate epJSON attribute
        return

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
        thermostats = self.unpack_epjson(self.templates_thermostats)
        for thermostat in thermostats:
            self.expanded_thermostats.append(
                ExpandThermostat(thermostat).run()
            )
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
        epjson_objects = [i.epjson for i in self.expanded_thermostats]
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
