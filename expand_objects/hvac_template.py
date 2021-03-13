import re
from expand_objects.epjson_handler import EPJSON


class HVACTemplate(EPJSON):
    """
    Manage overall HVAC Template objects and handle
    their conversion to regular objects.

    Inheritance:
    EPJSON <- Logger

    Attributes:
    templates: HVACTemplate objects from epJSON file
    templates_thermostat: HVACTemplate:Thermostat objects
    templates_zone: HVACTemplate:Zone: objects
    templates_system: HVACTemplate:System: objects
    templates_plant_equipment: HVACTemplate:Plant equipment objects
    templates_plant_loop: HVACTemplate:Plant: loop objects
    """

    def __init__(
            self,
            no_schema=True):
        """
        :param no_schema: Boolean flag for skipping schema validation
        """
        super().__init__(no_schema=no_schema)
        self.templates = {}
        self.templates_system = {}
        self.templates_zone = {}
        self.templates_plant_equipment = {}
        self.templates_plant_loop = {}
        self.templates_thermostats = {}
        return

    def pre_process(self, epjson):
        """
        Organize epJSON and assign objects to specific class attributes

        :param epjson: Input epJSON object
        :return: organized epJSON template objects into templates, and templates_* class variables..
        """
        # Make blank dictionaries and run to do tests before saving as class attributes
        templates = {}
        # todo_eo: add object_type check by pulling all values from schema?
        for object_type, object_structure in epjson.items():
            if re.match('^HVACTemplate:*', object_type):
                self.templates = self.merge_epjson(
                    super_dictionary=templates,
                    object_dictionary={object_type: object_structure},
                    unique_name_override=False
                )
            if re.match('^HVACTemplate:Thermostat', object_type):
                self.templates_thermostats = self.merge_epjson(
                    super_dictionary=self.templates_thermostats,
                    object_dictionary={object_type: object_structure},
                    unique_name_override=False
                )
        return

    def run(self, input_epjson):
        """
        Execute HVAC Template process workflow

        :param input_epjson: input epJSON file
        :return: epJSON containing expanded objects from templates
        """
        # todo_eo: the _base, _expanded, and _hvac_template files need to be created and added to the
        # output_epJSON
        self.load_schema()
        self.load_epjson(epjson_ref=input_epjson)
        self.pre_process(self.input_epjson)
        # Do manipulations and make output epJSON
        output_epjson = {"epJSON": input_epjson}
        return output_epjson
