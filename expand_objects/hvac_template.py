import re
from expand_objects.epjson_handler import EPJSON

class HVACTemplate(EPJSON):
    """
    Manage HVAC Template objects and handle their conversion to regular objects.

    Parameters
    ------
    templates_exist : boolean indicating if templates are present
    """
    def __init__(self, logger_name = None):
        super().__init__(logger_name = logger_name or 'hvac_template_logger')
        self.templates_exist = None
        self.templates = None
        return

    def check_epjson_for_templates(self, epjson_obj):
        self.templates = [{i : j} for (i, j) in epjson_obj.items() if re.match(r'^HVACTemplate:.*$', i)]
        print(self.templates)
        self.templates_exist = True if len(self.templates) > 0 else False
        return
