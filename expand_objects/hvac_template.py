import re
from expand_objects.epjson_handler import EPJSON


class HVACTemplate(EPJSON):
    """
    Manage overall HVAC Template objects and handle
    their conversion to regular objects.

    Inheritance:
    EPJSON <- Logger

    Parameters:
    templates_exist : boolean indicating if templates are present
    templates : list of HVACTemplate objects from epJSON file
    """

    def __init__(
            self,
            no_schema=True):
        super().__init__(no_schema=no_schema)
        self.templates_exist = None
        self.templates = None
        self.templates_thermostat = None
        return

    def check_epjson_for_templates(self, epjson_obj):
        """
        Extract and organize hvac template objects

        templates : all HVACTemplate objects
        templates_exist : boolean indicating if any HVACTemplates are in the file
        templates_thermostat : All HVACTemplate:Thermostat objects
        """
        self.templates = {
            i: j
            for (i, j) in epjson_obj.items()
            if re.match(r'^HVACTemplate:.*$', i)
        }
        self.templates_exist = True if len(self.templates.keys()) > 0 else False
        self.templates_thermostat = {
            k: l
            for i, j in self.templates.items()
            for k, l in j.items()
            if re.match(r'^HVACTemplate:Thermostat$', i)
        }
        return

    def run(self, input_epjson):
        """
        Execute HVAC Template process workflow
        """
        self.load_schema()
        self.load_epjson(epjson_ref=input_epjson)
        self.check_epjson_for_templates(self.input_epjson)
        # Do manipulations and make output epjson
        output_epjson = input_epjson
        return output_epjson
