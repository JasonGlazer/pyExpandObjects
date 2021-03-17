import re
from expand_objects.epjson_handler import EPJSON
from expand_objects.expand_objects import ExpandThermostat


class HVACTemplate(EPJSON):
    """
    Manage overall HVAC Template objects and handle
    their conversion to regular objects.

    Inheritance:
    EPJSON <- Logger

    Attributes:
        templates: HVACTemplate objects from epJSON file
        base_objects: Non-HVACTemplate objects from epJSON file
        templates_zone: HVACTemplate:Zone: objects
        templates_system: HVACTemplate:System: objects
        templates_plant_equipment: HVACTemplate:Plant equipment objects
        templates_plant_loop: HVACTemplate:Plant: loop objects
        expanded_*: List of class objects for each template type
        epjson: output epjson object
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
        self.templates_system = {}
        self.templates_zone = {}
        self.templates_plant_equipment = {}
        self.templates_plant_loop = {}
        self.templates_thermostats = {}
        self.expanded_thermostats = []
        self.epjson = {}
        return

    def hvac_template_process(self, epjson):
        """
        Organize epJSON and assign objects to specific class attributes

        :param epjson: Input epJSON object
        :return: organized epJSON template objects into templates, and templates_* as class variables..
        """
        self.logger.info('##### HVACTemplate #####')
        # Make blank dictionaries and run to do tests before saving as class attributes
        # todo_eo: add object_type check by pulling all values from schema?
        for object_type, object_structure in epjson.items():
            if re.match('^HVACTemplate:*', object_type):
                self.templates = self.merge_epjson(
                    super_dictionary=self.templates,
                    object_dictionary={object_type: object_structure},
                    unique_name_override=False
                )
            else:
                self.base_objects = self.merge_epjson(
                    super_dictionary=self.base_objects,
                    object_dictionary={object_type: object_structure},
                    unique_name_override=False
                )
            if re.match('^HVACTemplate:Thermostat', object_type):
                self.templates_thermostats = self.merge_epjson(
                    super_dictionary=self.templates_thermostats,
                    object_dictionary={object_type: object_structure},
                    unique_name_override=False
                )
            # todo_eo build out for remaining templates
        return

    def run(self, input_epjson):
        """
        Execute HVAC Template process workflow

        :param input_epjson: input epJSON file
        :return: epJSON containing expanded objects from templates
        """
        # todo_eo: the _base, _expanded, and _hvac_template files need to be created and added to the
        # output_epJSON
        # flush the stream handler
        self.logger.stream_flush
        self.epjson_process(epjson_ref=input_epjson)
        self.hvac_template_process(epjson=self.input_epjson)
        self.logger.info('##### Processing Thermostats #####')
        thermostats = self.unpack_epjson(self.templates_thermostats)
        for thermostat in thermostats:
            self.expanded_thermostats.append(
                ExpandThermostat(thermostat).run()
            )
        # Do manipulations and make output epJSON
        # Write messages logged to stream to outputPreProcessorMessage
        self.epjson = self.base_objects
        epjson_objects = [i.epjson for i in self.expanded_thermostats]
        for eo in epjson_objects:
            self.epjson = self.merge_epjson(
                super_dictionary=self.epjson,
                object_dictionary=eo
            )
        output_epjson = {
            "epJSON": self.epjson,
            'outputPreProcessorMessage': self.stream.getvalue()
        }
        return output_epjson
