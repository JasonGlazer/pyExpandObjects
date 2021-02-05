import re
from expand_objects.epjson_handler import EPJSON


class HVACTemplate(EPJSON):
    """
    Manage overall HVAC Template objects and handle
    their conversion to regular objects.

    Inheritance
    -----
    EPJSON <- Logger

    Parameters:
    -----
    templates_exist : boolean indicating if templates are present
    templates : list of HVACTemplate objects from epJSON file
    """

    def __init__(self):
        super().__init__()
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

    def get_object_from_schema(self, object_type):
        """
        Create object from schema to ensure keys are valid

        object_type : schema key value for EnergyPlus object
        """
        # return none with warning if no schema is loaded
        if not self.schema_is_valid or\
                not self.schema_validated:
            self.logger.error("No schema loaded. Unable to retrieve objcet")
            return None
        # get all values from patternProperties key.
        param_list = list(
            self.schema["properties"][object_type]["patternProperties"]
                .values()
        )
        # for each set of values, extract the keys and make them keys of the object
        object_d = {
            j: None for i in param_list
            for (j, k) in i['properties'].items()
            if i.get('properties')}
        return object_d

    def populate_object_from_object(self, source_objects, target_object_name, transitions, name_append):
        """
        fill target object with source object based on keys

        source_objects : EnergyPlus objects used to populate target
        target_object : EnergyPlus object to be populated
        transitions : dictionary of keys to transition source values to target
        name_append : value to append to source name for target
        """
        target_object = self.get_object_from_schema(target_object_name)
        # return if input types are incorrect
        if not isinstance(source_objects, dict)\
            or not isinstance(target_object, dict)\
            or not isinstance(transitions, dict)\
            or not isinstance(name_append, str)\
                or not target_object:
            # make this more specifc
            self.logger.error('populate_object failed')
            return None
        output_object = {}
        # iterate over source object keys and populate target.
        for obj in source_objects.keys():
            tmp_obj = target_object
            for k, v in source_objects[obj].items():
                # if source_object field name [k] provided to transitions is not
                # in transitions or target object field name (transitions[k])
                # is not in target_object, then issue an error and let program
                # fail
                if k not in transitions or transitions[k] not in tmp_obj:
                    self.logger.error('bad input key used for object population: '
                                      'key: %s, transition dictionary: %s, object: %s', k, transitions, tmp_obj)
                tmp_obj[transitions[k]] = v
            # append text to make new name.  remove whitespace for type safety.
            output_object[
                '_'.join(
                    [obj.replace(' ', '_'), name_append]
                )
            ] = tmp_obj
        return output_object
