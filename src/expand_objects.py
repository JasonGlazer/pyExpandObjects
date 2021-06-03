import copy
import yaml
import re
from pathlib import Path
import numbers
import typing

from custom_exceptions import PyExpandObjectsTypeError, InvalidTemplateException, \
    PyExpandObjectsYamlError, PyExpandObjectsFileNotFoundError, PyExpandObjectsYamlStructureException, \
    PyExpandObjectsException
from epjson_handler import EPJSON

source_dir = Path(__file__).parent


class ExpansionStructureLocation:
    """
    Verify expansion structure file location or object
    """
    def __get__(self, obj, owner):
        return obj._expansion_structure

    def __set__(self, obj, value):
        if isinstance(value, dict):
            parsed_value = value
        elif isinstance(value, str):
            value_is_path = Path(value)
            if value_is_path.is_file():
                if not value.endswith(('.yaml', '.yml')):
                    raise PyExpandObjectsTypeError('File extension does not match yaml type: {}'.format(value))
                else:
                    with open(value, 'r') as f:
                        # todo_eo: discuss tradeoff of safety vs functionality of SafeLoader/FullLoader.
                        #   With FullLoader there would be more functionality but might not be necessary.
                        parsed_value = yaml.load(f, Loader=yaml.SafeLoader)
            else:
                try:
                    # if the string is not a file, then try to load it directly with SafeLoader.
                    parsed_value = yaml.load(value, Loader=yaml.SafeLoader)
                    # if the parsed value is the same as the input value, it's probably a bad file path
                    if parsed_value == value:
                        raise PyExpandObjectsFileNotFoundError('File does not exist: {}'.format(value))
                except yaml.YAMLError as exc:
                    if hasattr(exc, 'problem_mark'):
                        mark = exc.problem_mark
                        raise PyExpandObjectsYamlError("Problem loading yaml at ({}, {})".format(
                            mark.line + 1, mark.column + 1))
                    else:  # pragma: no cover
                        raise PyExpandObjectsYamlError()
        else:
            raise PyExpandObjectsTypeError(
                'Template expansion structure reference is not a file path or dictionary: {}'.format(value))
        obj._expansion_structure = parsed_value
        return


class VerifyTemplate:
    """
    Verify if template dictionary is a valid type and structure
    """
    def __init__(self):
        super().__init__()

    def __get__(self, obj, owner):
        template = obj._template
        return template

    def __set__(self, obj, value):
        if value:
            if not isinstance(value, dict):
                raise PyExpandObjectsTypeError('Template must be a dictionary: {}'.format(value))
            try:
                # template dictionary should have one template_ype, one key (unique name)
                # and one object as a value (field/value dict)
                # this assignment below will fail if that is not the case.
                (template_type, template_structure), = value.items()
                (_, object_structure), = template_structure.items()
                # ensure object is dictionary
                if not isinstance(object_structure, dict):
                    raise InvalidTemplateException(
                        'An invalid object {} was passed as an {} object'.format(value, getattr(self, 'template_type')))
                obj._template = template_structure
            except (ValueError, AttributeError):
                raise InvalidTemplateException(
                    'An invalid object {} failed verification'.format(value))
        else:
            obj._template = None
        return


class ExpandObjects(EPJSON):
    """
    Class to contain general expansion functions as well as methods to connect template outputs.

    Attributes:
        expansion_structure: file or dictionary of expansion structure details (from YAML)
        template: epJSON dictionary containing HVACTemplate to expand
        template_type: HVACTemplate object type
        template_name: HVACTemplate unique name
        epjson: dictionary of epSJON objects to write to file
        unique_name: unique string used to modify to epJSON object names within the class
        HVACTemplate fields are stored as class attributes
    """

    template = VerifyTemplate()
    expansion_structure = ExpansionStructureLocation()

    def __init__(
            self,
            template=None,
            expansion_structure=str(source_dir / 'resources' / 'template_expansion_structures.yaml')):
        super().__init__()
        self.expansion_structure = expansion_structure
        self.template = template
        if self.template:
            try:
                (hvac_template_type, hvac_template_structure), = template.items()
                (template_name, template_structure), = hvac_template_structure.items()
            except ValueError:
                raise InvalidTemplateException(
                    'An Invalid object {} failed verification'.format(template))
            self.template_type = hvac_template_type
            self.template_name = template_name
            # apply template name and fields as class attributes
            for template_field in template_structure.keys():
                # If the value can be a numeric, then format it, otherwise save as a string.
                template_string_value = str(template_structure[template_field])
                num_rgx = re.match(r'^[-\d\.]+$', template_string_value)
                if num_rgx:
                    try:
                        if '.' in template_string_value:
                            setattr(self, template_field, float(template_structure[template_field]))
                        else:
                            setattr(self, template_field, int(template_structure[template_field]))
                    except ValueError:
                        setattr(self, template_field, template_structure[template_field])
                else:
                    setattr(self, template_field, template_structure[template_field])
        else:
            self.template_type = None
            self.template_name = None
        self.unique_name = None
        self.epjson = {}
        return

    def rename_attribute(self, old_attribute, new_attribute):
        """
        Change attribute name to commonize variables

        :param old_attribute: old attribute name
        :param new_attribute: new attribute name
        :return: None.  Old attribute is deleted and new attribute created in class
        """
        if hasattr(self, old_attribute):
            self.logger.info('{} renamed to {}'.format(old_attribute, new_attribute))
            setattr(self, new_attribute, getattr(self, old_attribute))
            # Possibly make this optional
            delattr(self, old_attribute)
        return

    def _flatten_list(
            self,
            nested_list: list,
            flat_list: list = [],
            clear: bool = True) -> list:
        """
        Flattens list of lists to one list of items.

        :param nested_list: list of nested dictionary objects
        :param flat_list: list used to store recursive addition of objects
        :param clear: Option to empty the recursive list
        :return: flattened list of objects
        """
        if clear:
            flat_list = []
        for i in nested_list:
            if isinstance(i, list):
                self._flatten_list(i, flat_list, clear=False)
            else:
                flat_list.append(i)
        return flat_list

    def get_structure(
            self,
            structure_hierarchy: list,
            structure=None) -> dict:
        """
        Retrieve structure from YAML loaded object.  When retrieving TemplateObjects, the last item in the hierarchy
        will be matched via regex instead of a direct key call for TemplateObjects.  This is done to allow for
        multiple template options in a single mapping.

        :param structure_hierarchy: list representing structure hierarchy
        :param structure: YAML loaded dictionary, default is loaded yaml loaded object
        :return: structured object as dictionary
        """
        try:
            structure = copy.deepcopy(structure or self.expansion_structure)
            if not isinstance(structure_hierarchy, list):
                raise PyExpandObjectsTypeError("Input must be a list of structure keys: {}".format(structure_hierarchy))
            # iterate over structure hierarchy list. For each item, call the key to the YAML object.  When looking up
            #   TemplateObjects, For the last item get the YAML object's keys and try a regex match.
            for idx, key in enumerate(structure_hierarchy):
                if structure_hierarchy[0] != 'TemplateObjects' or not idx == len(structure_hierarchy) - 1:
                    structure = structure[key]
                else:
                    structure_key_list = list(structure.keys())
                    for skl in structure_key_list:
                        if skl == 'AnyValue':
                            if re.match(r'\w+', str(key)) and str(key) != 'None':
                                structure = structure['AnyValue']
                        else:
                            if skl == str(key):
                                structure = structure[skl]
        except KeyError:
            raise PyExpandObjectsTypeError('YAML structure does not exist for hierarchy: {}'.format(
                structure_hierarchy))
        return structure

    def _get_option_tree(
            self,
            structure_hierarchy: list) -> dict:
        """
        Retrieve structure from YAML loaded object and verify it is correctly formatted for an option tree
        :param structure_hierarchy: list representing structure hierarchy
        :return: structured object as dictionary
        """
        try:
            if not isinstance(structure_hierarchy, list):
                raise PyExpandObjectsTypeError("Input must be a list of structure keys: {}".format(structure_hierarchy))
            if structure_hierarchy[0] != 'OptionTree':
                structure_hierarchy.insert(0, 'OptionTree')
        except TypeError:
            raise PyExpandObjectsTypeError(
                "Call to YAML object was not a list of structure keys: {}".format(structure_hierarchy))
        structure = self.get_structure(structure_hierarchy=structure_hierarchy)
        # todo_eo: this restriction is temporarily commented out.  It might not be necessary and too strict
        # Check structure keys.  Return error if there is an unexpected value
        # for key in structure:
        #     if key not in ['BuildPath', 'InsertObject', 'ReplaceObject', 'RemoveObject',
        #                    'BaseObjects', 'TemplateObjects']:
        #         raise PyExpandObjectsYamlStructureException(
        #             "YAML object is incorrectly formatted: {}, bad key: {}".format(structure, key))
        return structure

    def _get_option_tree_objects(
            self,
            structure_hierarchy: list) -> dict:
        """
        Return objects from option tree leaves.

        :return: epJSON dictionary with unresolved complex inputs
        """
        self.logger.info('Processing option tree: {}'.format(structure_hierarchy))
        option_tree = self._get_option_tree(structure_hierarchy=structure_hierarchy)
        options = option_tree.keys()
        option_tree_dictionary = {}
        # todo_eo: this requirement is temporarily commented out, may be too strict
        # if not set(list(options)).issubset({'BaseObjects', 'TemplateObjects', 'BuildPath'}):
        #     raise PyExpandObjectsYamlError("Invalid OptionTree leaf type provided in YAML: {}"
        #                                    .format(options))
        if "BuildPath" in options:
            object_list = self._process_build_path(option_tree=option_tree['BuildPath'])
            self.merge_epjson(
                super_dictionary=option_tree_dictionary,
                object_dictionary=self.yaml_list_to_epjson_dictionaries(object_list))
        if 'BaseObjects' in options:
            option_tree_leaf = self._get_option_tree_leaf(
                option_tree=option_tree,
                leaf_path=['BaseObjects', ])
            object_list = self._apply_transitions(option_tree_leaf=option_tree_leaf)
            self.merge_epjson(
                super_dictionary=option_tree_dictionary,
                object_dictionary=self.yaml_list_to_epjson_dictionaries(object_list))
        if 'TemplateObjects' in options and option_tree['TemplateObjects']:
            try:
                template_applied = None
                template_field_processing = None
                for template_field, template_tree in option_tree['TemplateObjects'].items():
                    template_field_processing = template_field
                    for field_option, objects in template_tree.items():
                        # check if field option is 'None' and if object doesn't exist in the class, or if
                        #   the fields match
                        if (field_option == 'None' and getattr(self, template_field, 'None') == 'None') or \
                                (getattr(self, template_field, None) and (
                                    field_option == str(getattr(self, template_field)) or (
                                        field_option == 'AnyValue' and re.match(r'\w+', str(getattr(self, template_field)))))):
                            option_tree_leaf = self._get_option_tree_leaf(
                                option_tree=option_tree,
                                leaf_path=['TemplateObjects', template_field, getattr(self, template_field, 'None')])
                            object_list = self._apply_transitions(option_tree_leaf=option_tree_leaf)
                            self.merge_epjson(
                                super_dictionary=option_tree_dictionary,
                                object_dictionary=self.yaml_list_to_epjson_dictionaries(object_list))
                            # Only one field option should be applied, so break after it is successful
                            template_applied = True
                            break
            except (AttributeError, KeyError):
                raise PyExpandObjectsYamlStructureException('TemplateObjects section for system type {} is invalid in '
                                                            'yaml file.'.format(self.template_type))
            if not template_applied:
                raise PyExpandObjectsYamlStructureException('A template option was not applied for template field {} '
                                                            'and option {}: {}'.format(
                                                                template_field_processing,
                                                                getattr(self, template_field_processing, None),
                                                                option_tree['TemplateObjects']))
        return option_tree_dictionary

    def _get_option_tree_leaf(
            self,
            option_tree: dict,
            leaf_path: list) -> dict:
        """
        Return leaf from OptionTree with alternative options formatted in dictionary

        :param option_tree: Yaml object holding HVACTemplate option tree
        :param leaf_path: path to leaf node of option tree
        :return: Formatted dictionary with objects and alternative options to be applied.
        """
        # todo_eo: check needs to be made that the right format is returned (e.g. dictionary with correct keys to pop)
        option_leaf = self.get_structure(structure_hierarchy=leaf_path, structure=option_tree)
        if option_leaf:
            transitions = option_leaf.pop('Transitions', None)
            mappings = option_leaf.pop('Mappings', None)
            # flatten object list in case it was nested due to yaml formatting
            try:
                objects = self._flatten_list(option_leaf['Objects'])
            except KeyError:
                raise PyExpandObjectsTypeError("Invalid or missing Objects location: {}".format(option_tree))
            return {
                'Objects': objects,
                'Transitions': transitions,
                'Mappings': mappings
            }
        else:
            # If no objects found, return blank dictionary
            return {}

    def _apply_transitions(
            self,
            option_tree_leaf: dict) -> list:
        """
        Set object field values in an OptionTree leaf, which consist of a 'Objects', 'Transitions', and 'Mappings' keys
        using a supplied Transitions dictionary.

        Transitions translates template input values to fields in Objects.  A more direct method of transitioning
        template inputs to object values can be done using field name formatting (e.g. field_name: {template_field})
        in the yaml file.  This method of application is used to override default values if template
        inputs are provided.

        Mappings maps values from templates to objects.  This is necessary when the template input is not a direct
        transition to an object value.

        :param option_tree_leaf: YAML loaded option tree end node with three keys: objects, transitions, mappings
        :return: list of dictionary objects with transitions and mappings applied
        """
        # if a dictionary without an objects key is provided, then return a blank dictionary because no transitions
        #   or mappings will be performed either.
        if not option_tree_leaf.get('Objects'):
            return {}
        option_tree_transitions = option_tree_leaf.pop('Transitions', None)
        option_tree_mappings = option_tree_leaf.pop('Mappings', None)
        # for each transition instruction, iterate over the objects and apply if the object_type matches the reference
        if option_tree_transitions:
            # flatten list if it is nested due to yaml structuring
            option_tree_transitions = self._flatten_list(option_tree_transitions)
            # iterate over the transitions instructions
            # Note, this method may be deprecated due to the more direct option of specifying the class attribute
            # directly in the yaml text field (e.g. field_name: {class_variable}).  However, this code has not been
            # removed in case it proves useful during development.
            for opt in option_tree_transitions:
                for object_type_reference, transition_structure in opt.items():
                    for template_field, object_field in transition_structure.items():
                        # Ensure there is only one object_key and it is 'Objects'
                        (object_key, tree_objects), = option_tree_leaf.items()
                        if not object_key == 'Objects':
                            raise PyExpandObjectsYamlError(
                                "Objects key missing from OptionTree leaf: {}".format(option_tree_leaf))
                        # iterate over each object from 'Objects' dictionary
                        for tree_object in tree_objects:
                            for object_type, _ in tree_object.items():
                                # if the object reference matches the object, apply the transition
                                if re.match(object_type_reference, object_type):
                                    # if the object_field is a dictionary, then the value is a formatted string to
                                    # apply with the template_field.  Otherwise, just try to get the value from the
                                    # template field, which is stored as a class attribute (on class initialization).
                                    try:
                                        if isinstance(object_field, dict):
                                            (object_field, object_val), = object_field.items()
                                            object_value = object_val.format(getattr(self, template_field))
                                        else:
                                            object_value = getattr(self, template_field)
                                    except AttributeError:
                                        object_value = None
                                        self.logger.info("A template value was attempted to be applied "
                                                         "to an object field but the template "
                                                         "field was not present in template object. "
                                                         "object: {}, object fieled: {}, template field: {}"
                                                         .format(object_type, object_field, template_field))
                                    if object_value:
                                        # On a match and valid value, apply the field.
                                        # If the object is a 'super' object used in a
                                        # BuildPath, then insert it in the 'Fields' dictionary.  Otherwise, insert it
                                        # into the top level of the object.
                                        if 'Fields' in tree_object[object_type].keys():
                                            tree_object[object_type]['Fields'][object_field] = object_value
                                        else:
                                            tree_object[object_type][object_field] = object_value
        # for each mapping instruction, iterate over the objects and apply if the object_type matches the reference
        if option_tree_mappings:
            # flatten list if it is nested due to yaml structuring
            option_tree_mappings = self._flatten_list(option_tree_mappings)
            # iterate over mapping instructions
            for otm in option_tree_mappings:
                for object_type_reference, mapping_structure in otm.items():
                    for mapping_field, mapping_dictionary in mapping_structure.items():
                        # Ensure there is only one object_key and it is 'Objects'
                        (object_key, tree_objects), = option_tree_leaf.items()
                        if not object_key == 'Objects':
                            raise PyExpandObjectsYamlError(
                                "Objects key missing from OptionTree leaf: {}".format(option_tree_leaf))
                        # iterate over each object from 'Objects' dictionary
                        for tree_object in tree_objects:
                            for object_type, object_fields in tree_object.items():
                                # if the object reference in the mapping dictionary matches the object, apply the map
                                if re.match(object_type_reference, object_type):
                                    for map_option, sub_dictionary in mapping_dictionary.items():
                                        if (map_option == 'None' and getattr(self, mapping_field, 'None') == 'None') or \
                                                hasattr(self, mapping_field) and getattr(self, mapping_field) == map_option:
                                            for field, val in sub_dictionary.items():
                                                try:
                                                    # On a match and valid value, apply the field.
                                                    # If the object is a 'super' object used in a
                                                    # BuildPath, then insert it in the 'Fields' dictionary.
                                                    # Otherwise, insert it into the top level of the object.
                                                    if 'Fields' in tree_object[object_type].keys():
                                                        tree_object[object_type]['Fields'][field] = val
                                                    else:
                                                        tree_object[object_type][field] = val
                                                except AttributeError:
                                                    self.logger.warning("Template field was attempted to be "
                                                                        "mapped to object but was not present "
                                                                        "in template inputs. mapping field: {}, "
                                                                        "object type: {}".format(field, object_type))
        return option_tree_leaf['Objects']

    def yaml_list_to_epjson_dictionaries(self, yaml_list: list) -> dict:
        """
        Convert list of YAML dictionaries into epJSON formatted dictionaries.

        YAML dictionaries can either be regular or 'super' objects which contain 'Fields' and 'Connectors'
        yaml_list: list of yaml objects to be formatted.
        :return: epJSON formatted dictionary
        """
        output_dictionary = {}
        for transitioned_object in yaml_list:
            try:
                (transitioned_object_type, transitioned_object_structure), = copy.deepcopy(transitioned_object).items()
                # get the dictionary nested in 'Fields' for super objects
                if transitioned_object_structure.get('Fields'):
                    object_name = transitioned_object_structure['Fields'].pop('name').format(self.unique_name)
                    transitioned_object_structure = transitioned_object_structure['Fields']
                else:
                    object_name = transitioned_object_structure.pop('name').format(self.unique_name)
                self.merge_epjson(
                    super_dictionary=output_dictionary,
                    object_dictionary={transitioned_object_type: {object_name: transitioned_object_structure}}
                )
            except (TypeError, KeyError, ValueError):
                raise PyExpandObjectsYamlStructureException(
                    "YAML object is incorrectly formatted: {}".format(transitioned_object))
        return output_dictionary

    @staticmethod
    def _resolve_complex_input_from_build_path(
            build_path: list,
            lookup_instructions: dict,
            connector_path: str = 'AirLoop') -> str:
        """
        Resolve a complex input using a build path and location based instructions.

        :param build_path: list of EnergyPlus super objects forming a build path
        :param lookup_instructions: instructions identifying the node location to return
        :return: Resolved field value
        """
        # keep a copy for output
        backup_copy = copy.deepcopy(lookup_instructions)
        # retrieve the necessary instructions from the instructions
        # if Location is an integer, lookup by index.  If it is a string, treat is as a regex and look for an
        # 'occurrence' key as well
        try:
            li = copy.deepcopy(lookup_instructions)
            location = li.pop('Location')
            connector_path = connector_path or li.pop('ConnectorPath', None)
            value_location = li.pop('ValueLocation')
        except KeyError:
            raise PyExpandObjectsYamlStructureException("Build path location reference is invalid: build path {}"
                                                        .format(backup_copy))
        try:
            # If location is an integer, then just retrieve the index
            if isinstance(location, int):
                super_object = build_path[location]
                (super_object_type, super_object_structure), = super_object.items()
            else:
                # If location is not an integer, assume it is a string and perform a regex match.  Also, check for an
                # Occurrence key in case the first match is not desired.  A Occurrence of -1 will just keep matching and
                # return the results from the last object match.
                occurrence = li.pop('Occurrence', 1)
                if not isinstance(occurrence, int):
                    raise PyExpandObjectsYamlStructureException('Occurrence key is not an integer: {}'.format(backup_copy))
                match_count = 0
                for super_object in build_path:
                    (super_object_type_check, _), = super_object.items()
                    if re.match(location, super_object_type_check):
                        (super_object_type, super_object_structure), = super_object.items()
                        match_count += 1
                        if match_count == occurrence:
                            break
                if (not match_count >= occurrence and occurrence != -1) or match_count == 0:
                    raise PyExpandObjectsYamlStructureException(
                        "The number of occurrences in a build path was never reached for "
                        "complex reference build path: {}, complex reference: {}".format(build_path, backup_copy))
        except (IndexError, ValueError):
            raise PyExpandObjectsYamlStructureException("Invalid build path or super object: {}".format(build_path))
        if value_location.lower() == 'self':
            return super_object_type
        elif value_location.lower() == 'key':
            return super_object_structure['Fields']['name']
        elif value_location in ('Inlet', 'Outlet'):
            reference_node = super_object_structure['Connectors'][connector_path][value_location]
            return super_object_structure['Fields'][reference_node]
        else:
            raise PyExpandObjectsYamlStructureException("Invalid complex input for build path lookup: lookup, {}, "
                                                        "value_location {}".format(backup_copy, value_location))

    def _resolve_complex_input(
            self,
            field_name: str,
            input_value: typing.Union[str, int, float, dict, list],
            epjson: dict = None,
            build_path: list = None) -> \
            typing.Generator[str, typing.Dict[str, str], None]:
        """
        Resolve a complex input into a field value

        :param epjson: epJSON dictionary of objects
        :param input_value: field value input
        :return: resolved field value
        """
        # Try class attributes if variables not defined in function
        epjson = epjson or self.epjson
        build_path = build_path or getattr(self, 'build_path', None)
        if isinstance(input_value, numbers.Number):
            yield {"field": field_name, "value": input_value}
        elif isinstance(input_value, str):
            # if a string is present within the formatting brackets, it is intended to be the template field (which is
            # a class attribute).
            # Extract the attribute reference and attempt to apply it.
            formatted_value = None
            template_field_rgx = re.search(r'.*{(\w+)}.*', input_value)
            if template_field_rgx:
                # if class field present, reformat the string to call the class attribute and apply.
                template_attribute = '0.{}'.format(template_field_rgx.group(1))
                formatted_string_rgx = re.sub(r'{(\w+)}', '{' + template_attribute + '}', input_value)
                try:
                    formatted_value = formatted_string_rgx.format(self)
                except AttributeError:
                    # If the class attribute does not exist, yield None as flag to handle in parent process.
                    yield {'field': field_name, 'value': None}
            else:
                # if no class attribute was specified {i.e. {}), just use the unique name.
                formatted_value = input_value.format(getattr(self, 'unique_name'))
            if formatted_value:
                # if a simple schedule is indicated by name, create it here.  The schedule
                # is stored to the class epjson attribute.
                always_val_rgx = re.search(r'^HVACTemplate-Always([\d\.]+)', str(formatted_value))
                if always_val_rgx:
                    always_val = always_val_rgx.group(1)
                    self.build_compact_schedule(
                        structure_hierarchy=['Objects', 'Common', 'Objects', 'Schedule', 'Compact', 'ALWAYS_VAL'],
                        insert_values=[always_val, ]
                    )
                # Try to evaluate the string, in case it is a mathematical expression.
                #  If the value is 'None' then pass it along without evaluation so it stays as a string.
                if str(formatted_value) != 'None':
                    try:
                        formatted_value = eval(formatted_value)
                    except (NameError, SyntaxError):
                        # Try to convert formatted value to correct type if it was not evaluated
                        num_rgx = re.match(r'^[-\d\.]+$', formatted_value)
                        if num_rgx:
                            if '.' in formatted_value:
                                formatted_value = float(formatted_value)
                            else:
                                formatted_value = int(formatted_value)
                yield {"field": field_name, "value": formatted_value}
        elif isinstance(input_value, dict):
            # unpack the referenced object type and the lookup instructions
            try:
                (reference_object_type, lookup_instructions), = input_value.items()
            except ValueError:
                raise PyExpandObjectsYamlStructureException('Complex input reference is invalid: {}'
                                                            .format(input_value))
            # If the input_value is instructing to use a 'BuildPathReference' then insert the object by build
            # path location
            if reference_object_type.lower() == 'buildpathreference':
                if not build_path:
                    raise PyExpandObjectsYamlStructureException("BuildPath complex input was specified with no build"
                                                                " path available: field {}, input {}"
                                                                .format(field_name, input_value))
                try:
                    # Get the referenced node value
                    extracted_value = self._resolve_complex_input_from_build_path(
                        build_path=build_path,
                        lookup_instructions=lookup_instructions)
                    # Resolve the extracted value with this function.
                    try:
                        complex_generator = self._resolve_complex_input(
                            epjson=epjson,
                            field_name=field_name,
                            input_value=extracted_value)
                        for cg in complex_generator:
                            yield cg
                    except RecursionError:
                        raise PyExpandObjectsYamlStructureException(
                            "Maximum Recursion limit exceeded when resolving {} for {}"
                            .format(input_value, field_name))
                except (KeyError, PyExpandObjectsYamlStructureException):
                    raise PyExpandObjectsYamlStructureException("Object field could not be resolved: input {}, "
                                                                "field {}, template name {}"
                                                                .format(input_value, field_name, self.unique_name))
            else:
                # If the input_value is an object type reference then try to match it with the EnergyPlus objects in
                # the super dictionary.
                for object_type in epjson.keys():
                    if re.match(reference_object_type, object_type):
                        # if 'self' is used as the reference node, return the energyplus object type
                        # if 'key' is used as the reference node, return the unique object name
                        # if the reference node is a dictionary, then it is a nested complex input and the function
                        #  is reapplied recursively
                        # For anything else, process the reference node and return a value.
                        (object_name, _), = epjson[object_type].items()
                        if lookup_instructions.lower() == 'self':
                            yield {"field": field_name, "value": object_type}
                        elif lookup_instructions.lower() == 'key':
                            yield {"field": field_name, "value": object_name}
                        elif isinstance(epjson[object_type][object_name][lookup_instructions], dict):
                            try:
                                complex_generator = self._resolve_complex_input(
                                    epjson=epjson,
                                    field_name=field_name,
                                    input_value=epjson[object_type][object_name][lookup_instructions])
                                for cg in complex_generator:
                                    yield cg
                            except RecursionError:
                                raise PyExpandObjectsYamlStructureException(
                                    "Maximum Recursion limit exceeded when resolving {} for {}"
                                    .format(input_value, field_name))
                        else:
                            # attempt to format both the field and value to be returned.
                            if isinstance(field_name, str):
                                formatted_field_name = field_name.format(self.unique_name)
                            else:
                                formatted_field_name = field_name
                            if isinstance(epjson[object_type][object_name][lookup_instructions], str):
                                formatted_value = epjson[object_type][object_name][lookup_instructions]\
                                    .format(self.unique_name)
                            else:
                                formatted_value = epjson[object_type][object_name][lookup_instructions]
                            yield {"field": formatted_field_name,
                                   "value": formatted_value}
        elif isinstance(input_value, list):
            # When the input is a list, iterate and apply this function recursively to each object.
            try:
                tmp_list = []
                for input_list_item in input_value:
                    tmp_d = {}
                    for input_list_field, input_list_value in input_list_item.items():
                        complex_generator = self._resolve_complex_input(
                            epjson=epjson,
                            field_name=input_list_field,
                            input_value=input_list_value)
                        for cg in complex_generator:
                            tmp_d[cg["field"]] = cg["value"]
                    tmp_list.append(tmp_d)
                yield {"field": field_name, "value": tmp_list}
            except RecursionError:
                raise PyExpandObjectsYamlStructureException(
                    "Maximum Recursion limit exceeded when resolving {} for {}"
                    .format(input_value, field_name))
        return

    def resolve_objects(self, epjson, reference_epjson=None):
        """
        Resolve complex inputs in epJSON formatted dictionary

        :param epjson: epJSON dictionary with complex inputs
        :param reference_epjson: (optional) epJSON dictionary to be used as reference objects for complex lookups.  If
            None, then the input epjson will be used
        :return: epJSON dictionary with values replacing complex inputs
        """
        schedule_dictionary = None
        if not reference_epjson:
            reference_epjson = copy.deepcopy(epjson)
        for object_type, object_structure in epjson.items():
            for object_name, object_fields in object_structure.items():
                # If a Schedule:Compact object is specified, and has special formatting, build it here.  The object
                # is saved to the class epjson attribute.
                if object_type == 'Schedule:Compact' and \
                        object_fields.get('structure') and object_fields.get('insert_values'):
                    structure = object_fields.pop('structure')
                    insert_values = object_fields.pop('insert_values')
                    schedule_dictionary = self.build_compact_schedule(
                        structure_hierarchy=structure.split(':'),
                        insert_values=insert_values)
                else:
                    for field_name, field_value in copy.deepcopy(object_fields).items():
                        input_generator = self._resolve_complex_input(
                            epjson=reference_epjson,
                            field_name=field_name,
                            input_value=field_value)
                        for ig in input_generator:
                            # if None was returned as the value, pop the key out of the dictionary and skip it.
                            # use the zero comparison to specifically pass that number.  The 'is not None' clause is
                            # not used here as this is more strict.
                            if isinstance(ig['value'], dict):
                                raise PyExpandObjectsYamlStructureException('complex input was not processed for '
                                                                            'object {}. Complex input: {}, output value'
                                                                            ' {}'.format(object_name, field_name,
                                                                                         field_value))
                            try:
                                test_zero = float(ig['value'])
                            except (TypeError, ValueError):
                                test_zero = ig['value']
                            if test_zero == 0 or ig['value']:
                                object_fields[ig['field']] = ig['value']
                            else:
                                object_fields.pop(ig['field'])
        # if a schedule dictionary was created, add it to the class epjson
        if schedule_dictionary:
            self.merge_epjson(
                super_dictionary=epjson,
                object_dictionary=schedule_dictionary,
                unique_name_override=True)
        return epjson

    def _create_objects(self, epjson=None):
        """
        Create a set of EnergyPlus objects for a given template

        :return: epJSON dictionary of newly created objects.  The input epJSON dictionary is also modified to include
            the newly created objects
        """
        # if epJSON dictionary not passed, use the class attribute
        epjson = epjson or self.epjson
        # Get the yaml structure from the template type
        structure_hierarchy = self.template_type.split(':')
        epjson_from_option_tree = self._get_option_tree_objects(structure_hierarchy=structure_hierarchy)
        # Always use merge_epjson to store objects in self.epjson in case objects have already been stored to
        # that dictionary during processing
        # For this processing, a temporary dictinoary needs to be made that merges the base epjson and the epjson
        # created from the option tree.  This is necessary such that a complex reference can find any epjson object that
        # was created.
        tmp_epjson = copy.deepcopy(epjson)
        self.merge_epjson(
            super_dictionary=tmp_epjson,
            object_dictionary=copy.deepcopy(epjson_from_option_tree)
        )
        resolved_inputs = self.resolve_objects(epjson_from_option_tree, reference_epjson=tmp_epjson)
        self.merge_epjson(
            super_dictionary=epjson,
            object_dictionary=resolved_inputs)
        return resolved_inputs

    def _parse_build_path(self, object_list, epjson=None):
        """
        Iterate over build path and check if each object is a super object.  If not, commit the object to the input
        epJSON.  Return a build path of only super objects.

        :param epjson: input epJSON dictionary
        :return: build path of only super objects
        """
        # Look over each object in the object_list.  If it is not a super object, then process it and save to
        #   class epjson object.  Use the current object_list as the reference epJSON to resolve the objects.
        #   If a larger scope of reference for the epJSON is needed, the object should be placed in BaseObjects or
        #   TemplateObjects sections of the yaml file.
        if not epjson:
            epjson = self.epjson
        if object_list:
            # make a temporary object list since non-super objects will be removed from the list
            tmp_object_list = []
            for o in object_list:
                (object_type, object_structure), = o.items()
                if not object_structure.get('Fields') and not object_structure.get('Connectors'):
                    epjson_object = self.yaml_list_to_epjson_dictionaries([o, ])
                    epjson_objects = self.yaml_list_to_epjson_dictionaries(object_list)
                    epjson_resolved_object = self.resolve_objects(epjson=epjson_object, reference_epjson=epjson_objects)
                    self.merge_epjson(
                        super_dictionary=epjson,
                        object_dictionary=epjson_resolved_object
                    )
                else:
                    tmp_object_list.append(o)
            # set the object list to only contain super objects
            object_list = tmp_object_list
        return object_list

    def _apply_build_path_action(self, build_path, action_instructions):
        """
        Mutate a build path list based on a set of action instructions

        :param build_path: Input build path list
        :param action_instructions: Formatted instructions to apply an action.  Valid actions are 'Insert', 'Remove',
            and 'Replace' (case insensitive).
        :return: mutated dictionary with action applied.
        """
        # get the indicated occurrence that the regex will match.  First match is default.
        occurrence = action_instructions.pop('Occurrence', 1)
        # Format check inputs for occurrence
        if not isinstance(occurrence, int) or (isinstance(occurrence, int) and occurrence < 0):
            raise PyExpandObjectsYamlStructureException('Occurrence must be a non-negative integer: {}'
                                                        .format(occurrence))
        # backup copy for output
        backup_copy = copy.deepcopy(action_instructions)
        try:
            # Format check inputs for action_type and location
            action_type = action_instructions.pop('ActionType').lower()
            if action_type not in ('insert', 'remove', 'replace'):
                raise PyExpandObjectsYamlStructureException('Invalid action type requested: {}'
                                                            .format(action_instructions))
            # check 'Location' format and ensure it is the right type and value.
            # if location is an integer then object_reference is not needed because the action will be
            # performed on that index and no object lookup will be required.
            if action_instructions.get('Location') is None and (action_type == 'remove' or action_type == 'replace'):
                location = None
                object_reference = action_instructions.pop('ObjectReference')
            elif isinstance(action_instructions['Location'], str) and \
                    action_instructions['Location'].lower() in ('before', 'after'):
                location = action_instructions.pop('Location').lower()
                object_reference = action_instructions.pop('ObjectReference')
            elif isinstance(action_instructions['Location'], int):
                location = action_instructions.pop('Location')
                object_reference = None
            else:
                raise PyExpandObjectsYamlStructureException('Insert reference value is not "Before", "After" or an '
                                                            'integer: {}'.format(backup_copy))
        except KeyError:
            raise PyExpandObjectsYamlStructureException(
                "Build Path Action is missing required instructions {}. ".format(backup_copy))
        # Get the option tree leaf for an action.
        # Remove does not require this step since it just removes objects from the original build path
        if action_type != 'remove':
            option_tree_leaf = self._get_option_tree_leaf(
                option_tree=action_instructions,
                leaf_path=[])
            # Apply transitions to the leaf to create an object list.
            object_list = self._apply_transitions(option_tree_leaf=option_tree_leaf)
        else:
            object_list = None
        object_list = self._parse_build_path(object_list=object_list)
        # Create new build path dictionary since the input dictionary will be mutated
        output_build_path = copy.deepcopy(build_path)
        # if the location is an integer, just perform the action on that index, otherwise, iterate over super objects
        #   keeping count of the index
        if isinstance(location, int):
            if action_type == 'insert':
                # if location is negative, then get the positive list index by subtraction
                if location < 0:
                    location = len(build_path) + location + 1
                output_build_path.insert(location, object_list)
            elif action_type == 'remove':
                output_build_path.pop(location)
            elif action_type == 'replace':
                output_build_path[location] = object_list
        else:
            # Iterate over the objects finding the appropriate location for the action.
            # Keep a count of number of times object has been matched.  This is for the 'Occurrence' key to
            #   perform an action on the nth occurrence of a match.
            match_count = 0
            for idx, super_object in enumerate(build_path):
                # if there is a match to the object type, and the occurrence is correct, then perform the action
                for super_object_type, super_object_structure in super_object.items():
                    if object_reference and re.match(object_reference, super_object_type):
                        match_count += 1
                        if match_count == occurrence:
                            if action_type == 'insert' and isinstance(location, str):
                                # The location variable is now either 'before' or 'after',
                                #   so mutate the variable to be an integer value for offset
                                location = 0 if location == 'before' else 1
                                output_build_path.insert(idx + location, object_list)
                            elif action_type == 'remove':
                                output_build_path.pop(idx)
                            elif action_type == 'replace':
                                output_build_path[idx] = object_list
                            else:
                                raise PyExpandObjectsYamlStructureException(
                                    "Action could not be performed on build path for an "
                                    "unknown reason: build path {}, action: {}".format(build_path, action_instructions))
            # check if the number of matches actually met the occurrence threshold
            if not match_count >= occurrence:
                raise PyExpandObjectsYamlStructureException(
                    "The number of occurrences in a build path was never reached for "
                    "an action. build path: {}, action: {}".format(build_path, action_instructions))
        # flatten build path list before output
        output_build_path = self._flatten_list(output_build_path)
        return output_build_path

    def _connect_and_convert_build_path_to_object_list(self, build_path=None, loop_type='AirLoop'):
        """
        Connect nodes in build path and convert to list of epJSON formatted objects

        :param build_path: build path of EnergyPlus super objects
        :return: object list of modified super objects.  The build path is also saved as a class attribute for
            future reference
        """
        build_path = build_path or getattr(self, 'build_path', None)
        if not build_path:
            raise PyExpandObjectsException("Build path was not provided nor was it available as a class attribute")
        # cleanse build path to only contain super objects.  Non super objects are saved to epJSON file
        parsed_build_path = self._parse_build_path(object_list=copy.deepcopy(build_path))
        object_list = []
        formatted_build_path = []
        out_node = None
        for idx, super_object in enumerate(parsed_build_path):
            (super_object_type, super_object_structure), = super_object.items()
            connectors = super_object_structure.get('Connectors')
            if not connectors:
                raise PyExpandObjectsYamlStructureException("Super object is missing Connectors key: {}"
                                                            .format(super_object))
            try:
                # if a super object is specified but the Loop Connectors is identified as False, then just
                #  append it to the build path but don't make a connection.  An example of this is the heat
                #  exchanger which connects to the OA node, not the inlet node of the OutdoorAir:Mixer, which is
                #  the return node
                if connectors[loop_type]:
                    # The first object only sets the outlet node variable and remains unchanged
                    if not out_node:
                        out_node = super_object_structure['Fields'][connectors[loop_type]['Outlet']]
                    else:
                        # After the first object, the inlet node name is changed to the previous object's outlet node
                        # name.  Then the outlet node variable is reset.
                        super_object_structure['Fields'][connectors[loop_type]['Inlet']] = out_node
                        out_node = super_object_structure['Fields'][connectors[loop_type]['Outlet']]
                object_list.append({super_object_type: super_object_structure['Fields']})
                formatted_build_path.append({super_object_type: super_object_structure})
            except (AttributeError, KeyError):
                raise PyExpandObjectsYamlStructureException("Field/Connector mismatch. Object: {}, connectors: {}"
                                                            .format(super_object_structure, connectors))
        # Save build path to class attribute for later reference.
        self.build_path = formatted_build_path
        return object_list

    def _create_availability_manager_assignment_list(self, epjson: dict = None) -> dict:
        """
        Create AvailabilityManagerAssignmentList object from epJSON dictionary
        This list object is separated from the OptionTree build operations because it will vary based on the
        presence of AvailabilityManager:.* objects in the epJSON dictionary.
        Therefore, the list objects must be built afterwards in order to retrieve the referenced objects.

        :param epjson: system epJSON formatted dictionary
        :return: epJSON formatted AirLoopHVAC:ControllerList objects.  These objects are also stored back to the
            input epJSON object.
        """
        # if build_path and/or epjson are not passed to function, get the class attributes
        epjson = epjson or self.epjson
        availability_managers = {i: j for i, j in epjson.items() if re.match(r'^AvailabilityManager:.*', i)}
        # loop over availability managers and add them to the list.
        availability_manager_list_object = \
            self.get_structure(structure_hierarchy=['AutoCreated', 'System', 'AvailabilityManagerAssignmentList', 'Base'])
        availability_manager_list_object['managers'] = []
        try:
            for object_type, object_structure in availability_managers.items():
                for object_name, object_fields in object_structure.items():
                    availability_manager_list_object['managers'].append({
                        'availability_manager_name': object_name,
                        'availability_manager_object_type': object_type})
        except AttributeError:
            raise PyExpandObjectsTypeError("AvailabilityManager object not properly formatted: {}"
                                           .format(availability_managers))
        availability_manager_assignment_list_object = self.yaml_list_to_epjson_dictionaries([
            {'AvailabilityManagerAssignmentList': availability_manager_list_object}, ])
        self.merge_epjson(
            super_dictionary=epjson,
            object_dictionary=self.resolve_objects(epjson=availability_manager_assignment_list_object))
        return self.resolve_objects(epjson=availability_manager_assignment_list_object)

    def _process_build_path(self, option_tree):
        """
        Create a connected group of objects from the BuildPath branch in the OptionTree.  A build path is a list of
        'super objects' which have an extra layer of structure.  These keys are 'Fields' and 'Connectors'.  The Fields
        are regular EnergyPlus field name-value pairs.  The connectors are structured dictionaries that provide
        information on how one object should connect the previous/next object in the build path list.  A branch of
        connected objects is also produced.

        :return: list of EnergyPlus super objects.  Additional EnergyPlus objects (Branch, Branchlist) that require
            the build path for their creation.
        """
        # Get the base objects from the build path dictionary and apply transitions to obtain a list of dictionary
        #  objects that have been formatted.
        build_path_leaf = self._get_option_tree_leaf(
            option_tree=option_tree,
            leaf_path=['BaseObjects', ])
        build_path = self._apply_transitions(build_path_leaf)
        # if the build path from base objects is empty, it comes back as a dictionary.  Therefore, it needs to be
        # explicity changed to a list
        build_path = build_path if bool(build_path) else []
        # Get the list actions to perform on a build bath, based on template inputs, and process them in order
        actions = option_tree.pop('Actions', None)
        if actions:
            # flatten action list due to yaml formatting
            actions = self._flatten_list(actions)
            for action in actions:
                action_applied = None
                template_field_processing = None
                try:
                    for template_field, action_structure in action.items():
                        template_field_processing = template_field
                        if getattr(self, template_field, 'None') == 'None':
                            action_applied = True
                        for template_value, action_instructions in action_structure.items():
                            # check if the option tree template value matches a class template field.
                            # If the template value is 'None' in the yaml, then perform the operation if the class
                            # attribute is missing or None.
                            if (template_value == 'None' and getattr(self, template_field, 'None') == 'None') or \
                                    (getattr(self, template_field, None) and (
                                        template_value == str(getattr(self, template_field)) or (
                                            template_value == 'AnyValue' and re.match(r'\w+', str(getattr(self, template_field)))))):
                                if action_instructions:
                                    build_path = self._apply_build_path_action(
                                        build_path=build_path,
                                        action_instructions=action_instructions)
                                action_applied = True
                except (AttributeError, KeyError):
                    raise PyExpandObjectsYamlStructureException("Action is incorrectly formatted: {}".format(action))
                if not action_applied:
                    raise PyExpandObjectsYamlStructureException('A build path action was not applied for template field {} '
                                                                'and option {}: {}'.format(
                                                                    template_field_processing,
                                                                    getattr(self, template_field_processing, None),
                                                                    action))
        # Format the created build path
        object_list = self._connect_and_convert_build_path_to_object_list(build_path)
        return object_list

    def build_compact_schedule(
            self,
            structure_hierarchy: list,
            insert_values: list,
            name: str = None) -> dict:
        """
        Build a Schedule:Compact schedule from inputs.  Save epjJSON object to class dictionary and return
        to calling function.

        :param structure_hierarchy: list indicating YAML structure hierarchy
        :param insert_values: list of values to insert into object
        :param name: (optional) name of object.
        :return: epJSON object of compact schedule
        """
        structure_object = self.get_structure(structure_hierarchy=structure_hierarchy)
        if not isinstance(insert_values, list):
            insert_values = [insert_values, ]
        if not name:
            name = structure_object.pop('name')
        if '{}' in name:
            name = name.format(insert_values[0])
        if not structure_object.get('schedule_type_limits_name', None):
            structure_object['schedule_type_limits_name'] = 'Any Number'
        # for each element in the schedule, convert to numeric if value replacement occurs
        if insert_values:
            formatted_data_lines = [
                {j: float(k.format(float(*insert_values)))}
                if re.match(r'.*{}', k, re.IGNORECASE) else {j: k}
                for i in structure_object['data'] for j, k in i.items()]
        else:
            formatted_data_lines = [{j: k} for i in structure_object for j, k in i.items()]
        schedule_object = {
            'Schedule:Compact': {
                name: {
                    'schedule_type_limits_name': structure_object['schedule_type_limits_name'],
                    'data': formatted_data_lines
                }
            }
        }
        # add objects to class epjson dictionary
        self.merge_epjson(
            super_dictionary=self.epjson,
            object_dictionary=schedule_object,
            unique_name_override=True
        )
        return schedule_object


class ExpandThermostat(ExpandObjects):
    """
    Thermostat expansion operations
    """

    def __init__(self, template, epjson=None):
        # fill/create class attributes values with template inputs
        super().__init__(template=template)
        self.unique_name = self.template_name
        self.epjson = epjson or self.epjson
        return

    def _create_and_set_schedules(self):
        """
        Create, or use existing, schedules.  Assign schedule names to class variable

        :return: Cooling and/or Heating schedule variables as class attributes
        """
        for thermostat_type in ['heating', 'cooling']:
            if not getattr(self, '{}_setpoint_schedule_name'.format(thermostat_type), None) \
                    and getattr(self, 'constant_{}_setpoint'.format(thermostat_type), None):
                thermostat_schedule = self.build_compact_schedule(
                    structure_hierarchy=['Objects', 'Common', 'Objects', 'Schedule', 'Compact', 'ALWAYS_VAL'],
                    insert_values=getattr(self, 'constant_{}_setpoint'.format(thermostat_type)),
                )
                (thermostat_schedule_type, thermostat_schedule_structure), = thermostat_schedule.items()
                (thermostat_schedule_name, _), = thermostat_schedule_structure.items()
                setattr(self, '{}_setpoint_schedule_name'.format(thermostat_type), thermostat_schedule_name)
        return

    def _create_thermostat_setpoints(self):
        """
        Create ThermostatSetpoint objects based on class setpoint_schedule_name attributes
        :return: Updated class epJSON dictionary with ThermostatSetpoint objects added.
        """
        if hasattr(self, 'heating_setpoint_schedule_name') \
                and hasattr(self, 'cooling_setpoint_schedule_name'):
            thermostat_setpoint_object = {
                "ThermostatSetpoint:DualSetpoint": {
                    '{} SP Control'.format(self.unique_name): {
                        'heating_setpoint_temperature_schedule_name': getattr(self, 'heating_setpoint_schedule_name'),
                        'cooling_setpoint_temperature_schedule_name': getattr(self, 'cooling_setpoint_schedule_name')
                    }
                }
            }
        elif hasattr(self, 'heating_setpoint_schedule_name'):
            thermostat_setpoint_object = {
                "ThermostatSetpoint:SingleHeating": {
                    '{} SP Control'.format(self.unique_name): {
                        'setpoint_temperature_schedule_name': getattr(self, 'heating_setpoint_schedule_name')
                    }
                }
            }
        elif hasattr(self, 'cooling_setpoint_schedule_name'):
            thermostat_setpoint_object = {
                "ThermostatSetpoint:SingleCooling": {
                    '{} SP Control'.format(self.unique_name): {
                        'setpoint_temperature_schedule_name': getattr(self, 'cooling_setpoint_schedule_name')
                    }
                }
            }
        else:
            # todo_eo: should the final else case make a floating thermostat or this error?
            raise InvalidTemplateException(
                'No setpoints or schedules provided to HVACTemplate:Thermostat object: {}'.format(self.unique_name))
        self.merge_epjson(
            super_dictionary=self.epjson,
            object_dictionary=thermostat_setpoint_object,
            unique_name_override=False
        )
        return

    def run(self):
        """
        Perform all template expansion operations and return the class to the parent calling function.
        :return: Class object with epJSON dictionary as class attribute
        """
        self.logger.info('Processing Thermostat: {}'.format(self.unique_name))
        self._create_and_set_schedules()
        self._create_thermostat_setpoints()
        return self


class ZonevacEquipmentListOjectType:
    """
    Set a class attribute to select the appropriate ZoneHVAC:EquipmentList from TemplateOptions in the YAML lookup.
    """
    def __get__(self, obj, owner):
        return obj._zone_hvac_equipmentlist_object_type

    def __set__(self, obj, value):
        (template_type, template_structure), = value.items()
        (_, template_fields), = template_structure.items()
        # Check for doas reference
        doas_equipment = None
        if template_fields.get('dedicated_outdoor_air_system_name', 'None') != 'None':
            doas_equipment = True
        # Check for baseboard reference
        baseboard_equipment = None
        if template_fields.get('baseboard_heating_type', 'None') != 'None':
            baseboard_equipment = True
        if doas_equipment and baseboard_equipment:
            obj._zone_hvac_equipmentlist_object_type = 'WithDOASAndBaseboard'
        elif doas_equipment:
            obj._zone_hvac_equipmentlist_object_type = 'WithDOAS'
        elif baseboard_equipment:
            if template_type == 'HVACTemplate:Zone:BaseboardHeat':
                obj._zone_hvac_equipmentlist_object_type = 'Baseboard'
            else:
                obj._zone_hvac_equipmentlist_object_type = 'WithBaseboard'
        else:
            obj._zone_hvac_equipmentlist_object_type = 'Base'
        return


class ExpandZone(ExpandObjects):
    """
    Zone expansion operations
    """

    zone_hvac_equipmentlist_object_type = ZonevacEquipmentListOjectType()

    def __init__(self, template, epjson=None):
        # fill/create class attributes values with template inputs
        super().__init__(template=template)
        try:
            self.unique_name = getattr(self, 'zone_name')
            if not self.unique_name:
                raise InvalidTemplateException("Zone name not provided in template: {}".format(template))
        except AttributeError:
            raise InvalidTemplateException("Zone name not provided in zone template: {}".format(template))
        self.zone_hvac_equipmentlist_object_type = template
        self.epjson = epjson or self.epjson
        return

    def run(self):
        """
        Process zone template
        :return: Class object with epJSON dictionary as class attribute
        """
        self.logger.info('Processing Zone: {}'.format(self.unique_name))
        self._create_objects()
        return self


class AirLoopHVACUnitaryObjectType:
    """
    Set a class attribute to select the appropriate unitary equipment type from TemplateOptions in the YAML lookup.
    """
    def __get__(self, obj, owner):
        return obj._airloop_hvac_unitary_object_type

    def __set__(self, obj, value):
        (template_type, template_structure), = value.items()
        (template_name, template_fields), = template_structure.items()
        cooling_coil_type = None if template_fields.get('cooling_coil_type', 'None') == 'None' else \
            template_fields.get('cooling_coil_type')
        heating_coil_type = None if template_fields.get('heating_coil_type', 'None') == 'None' else \
            template_fields.get('heating_coil_type')
        if not heating_coil_type:
            heating_coil_type = None if template_fields.get('heat_pump_heating_coil_type') == 'None' else \
                template_fields.get('heat_pump_heating_coil_type')
        supplemental_heating_type = None if template_fields.get('supplemental_heating_or_reheat_coil_type', 'None') == \
            'None' else True
        if template_type == 'HVACTemplate:System:Unitary' and cooling_coil_type and heating_coil_type:
            obj._airloop_hvac_unitary_object_type = 'Furnace:HeatCool'
        elif template_type == 'HVACTemplate:System:UnitaryHeatPump:AirToAir':
            obj._airloop_hvac_unitary_object_type = 'HeatPump:AirToAirWithSupplemental'
        elif template_type == 'HVACTemplate:System:UnitarySystem':
            if cooling_coil_type == 'MultiSpeedDX' and heating_coil_type and not supplemental_heating_type:
                obj._airloop_hvac_unitary_object_type = 'HeatPump:AirToAirMultiSpeedDX'
            elif cooling_coil_type and heating_coil_type and not supplemental_heating_type:
                obj._airloop_hvac_unitary_object_type = 'HeatPump:AirToAir'
            elif cooling_coil_type and heating_coil_type and supplemental_heating_type:
                obj._airloop_hvac_unitary_object_type = 'HeatPump:AirToAirWithSupplemental'
        return


class AirLoopHVACUnitaryFanTypeAndPlacement:
    """
    Set a class attribute to select the appropriate fan type and placement from TemplateOptions in the YAML lookup.
    """
    def __get__(self, obj, owner):
        return obj._airloop_hvac_unitary_fan_type_and_placement

    def __set__(self, obj, value):
        (template_type, template_structure), = value.items()
        (template_name, template_fields), = template_structure.items()
        supply_fan_placement = 'BlowThrough' if template_fields.get('supply_fan_placement', 'None') == 'None' else \
            template_fields.get('supply_fan_placement')
        cooling_coil_type = 'Base' if template_fields.get('cooling_coil_type', 'None') == 'None' else \
            template_fields.get('cooling_coil_type')
        if cooling_coil_type == 'MultiSpeedDX':
            supply_fan_type = 'VariableVolume'
        else:
            supply_fan_type = 'Base'
        obj._airloop_hvac_unitary_fan_type_and_placement = ''.join([supply_fan_type, supply_fan_placement])
        return


class AirLoopHVACObjectType:
    """
    Set a class attribute to select the appropriate AirLoopHVAC type from TemplateOptions in the YAML lookup.
    """
    def __get__(self, obj, owner):
        return obj._airloop_hvac_object_type

    def __set__(self, obj, value):
        (template_type, template_structure), = value.items()
        (_, template_fields), = template_structure.items()
        cooling_coil_type = True if 'chilledwater' == template_fields.get('cooling_coil_type', 'None').lower() else False
        heating_coil_type = True if 'hotwater' == template_fields.get('heating_coil_type', 'None').lower() else False
        if not re.match(r'HVACTemplate:System:Unitary.*', template_type) and (cooling_coil_type or heating_coil_type):
            obj._airloop_hvac_object_type = 'Water'
        else:
            obj._airloop_hvac_object_type = 'Base'
        return


class ModifyCoolingCoilSetpointControlType:
    """
    Modify cooling_coil_setpoint_control_type based on other template attributes for YAML TemplateOptions lookup.
    """
    def __get__(self, obj, owner):
        return obj._cooling_coil_setpoint_control_type

    def __set__(self, obj, value):
        # If the field is getting set on load with a string, then just return the string.  Otherwise, modify it with
        #  the template
        if isinstance(value, str):
            obj._cooling_coil_setpoint_control_type = value
        else:
            (_, template_structure), = value.items()
            (_, template_fields), = template_structure.items()
            dehumidification_status = True if template_fields.get('dehumidification_control_type', 'None') != 'None' else False
            cooling_setpoint = template_fields.get('cooling_coil_setpoint_control_type', 'FixedSetpoint')
            if dehumidification_status:
                obj._cooling_coil_setpoint_control_type = ''.join([cooling_setpoint, 'WithDehumidification'])
        return


class ModifyHeatingCoilSetpointControlType:
    """
    Modify heating_coil_setpoint_control_type based on other template attributes for YAML TemplateOptions lookup.
    """
    def __get__(self, obj, owner):
        return obj._heating_coil_setpoint_control_type

    def __set__(self, obj, value):
        # If the field is getting set on load with a string, then just return the string.  Otherwise, modify it with
        #  the template
        if isinstance(value, str):
            obj._heating_coil_setpoint_control_type = value
        else:
            (_, template_structure), = value.items()
            (_, template_fields), = template_structure.items()
            dehumidification_status = True if template_fields.get('dehumidification_control_type', 'None') != 'None' else False
            heating_setpoint = template_fields.get('cooling_coil_setpoint_control_type', 'FixedSetpoint')
            if dehumidification_status:
                obj._heating_coil_setpoint_control_type = ''.join([heating_setpoint, 'WithDehumidification'])
        return


class ExpandSystem(ExpandObjects):
    """
    System expansion operations
    """

    airloop_hvac_unitary_object_type = AirLoopHVACUnitaryObjectType()
    airloop_hvac_object_type = AirLoopHVACObjectType()
    airloop_hvac_unitary_fan_type_and_placement = AirLoopHVACUnitaryFanTypeAndPlacement()
    cooling_coil_setpoint_control_type = ModifyCoolingCoilSetpointControlType()
    heating_coil_setpoint_control_type = ModifyHeatingCoilSetpointControlType()

    def __init__(self, template, epjson=None):
        super().__init__(template=template)
        # map variable variants to common value and remove original
        self.rename_attribute('cooling_coil_design_setpoint_temperature', 'cooling_coil_design_setpoint')
        self.rename_attribute('economizer_upper_temperature_limit', 'economizer_maximum_limit_dry_bulb_temperature')
        self.rename_attribute('economizer_lower_temperature_limit', 'economizer_minimum_limit_dry_bulb_temperature')
        self.unique_name = self.template_name
        self.epjson = epjson or self.epjson
        self.build_path = None
        self.airloop_hvac_unitary_object_type = template
        self.airloop_hvac_object_type = template
        self.airloop_hvac_unitary_fan_type_and_placement = template
        self.cooling_coil_setpoint_control_type = template
        self.heating_coil_setpoint_control_type = template
        return

    def _create_controller_list_from_epjson(self, epjson: dict = None, build_path: list = None) -> dict:
        """
        Create AirLoopHVAC:ControllerList objects from epJSON dictionary
        These list objects are separated from the OptionTree build operations because they will vary based on the
        presence of Controller:WaterCoil and Controller:OutdoorAir objects in the epJSON dictionary.
        Therefore, the list objects must be built afterwards in order to retrieve the referenced Controller:.* objects.

        :param epjson: system epJSON formatted dictionary
        :param build_path: List of epJSON super objects in build path order
        :return: epJSON formatted AirLoopHVAC:ControllerList objects.  These objects are also stored back to the
            input epJSON object.
        """
        # if epjson/build_path not provided, use the class attribute:
        epjson = epjson or self.epjson
        build_path = build_path or self.build_path
        # Create a list of actuators in stream order.  This will be used to determine the controller list order.
        actuator_list = []
        for bp in build_path:
            (super_object_type, super_object_structure), = bp.items()
            if re.match(r'Coil:(Cooling|Heating):Water.*', super_object_type):
                epjson_object = self.yaml_list_to_epjson_dictionaries([bp])
                resovled_epjson_object = self.resolve_objects(epjson=epjson_object)
                (object_name, object_fields), = resovled_epjson_object[super_object_type].items()
                actuator_list.append(object_fields['water_inlet_node_name'])
        object_list = []
        for controller_type in ['Controller:WaterCoil', 'Controller:OutdoorAir']:
            controller_objects = epjson.get(controller_type)
            if controller_objects:
                airloop_hvac_controllerlist_object = \
                    self.get_structure(structure_hierarchy=['AutoCreated', 'System', 'AirLoopHVAC', 'ControllerList',
                                                            controller_type.split(':')[1], 'Base'])
                try:
                    object_id = 0
                    for object_name, object_structure in controller_objects.items():
                        # For water coils, try to get the index of the actuator from the list and use that to set
                        #  the order.  Raise a ValueError if no match is found
                        if controller_type == 'Controller:WaterCoil':
                            object_id = actuator_list.index(object_structure['actuator_node_name']) + 1
                        else:
                            object_id += 1
                        airloop_hvac_controllerlist_object['controller_{}_name'.format(object_id)] = \
                            object_name
                        airloop_hvac_controllerlist_object['controller_{}_object_type'.format(object_id)] = \
                            controller_type
                except ValueError:
                    raise PyExpandObjectsTypeError("Actuator node for water coil object does not match controller "
                                                   "object reference. build_path: {}, controllers: {}"
                                                   .format(build_path, controller_objects))
                except AttributeError:
                    raise PyExpandObjectsTypeError("Controller object not properly formatted: {}"
                                                   .format(controller_objects))
                object_list.append({'AirLoopHVAC:ControllerList': airloop_hvac_controllerlist_object})
        controller_epjson = self.yaml_list_to_epjson_dictionaries(object_list)
        self.merge_epjson(
            super_dictionary=epjson,
            object_dictionary=self.resolve_objects(epjson=controller_epjson))
        return self.resolve_objects(epjson=controller_epjson)

    def _create_outdoor_air_equipment_list_from_build_path(
            self, build_path: list = None, epjson: dict = None) -> dict:
        """
        Create AirLoopHVAC:OutdoorAirSystem:EquipmentList objects from system build path
        This object is separated from the OptionTree build operations because it varies based on the final build path.
        Therefore, this object must be built afterwards in order to retrieve the referenced outdoor air equipment
        objects.

        :param build_path: system build path
        :param epjson: epJSON dictionary
        :return: epJSON formatted AirLoopHVAC:OutdoorAirSystem:EquipmentList objects.  These objects are also stored
            back to the input epJSON object.
        """
        # if build_path and/or epjson are not passed to function, get the class attributes
        epjson = epjson or self.epjson
        build_path = build_path or getattr(self, 'build_path', None)
        if not build_path:
            raise PyExpandObjectsException("Build path was not provided nor was it available as a class attribute")
        # set dictionary and loop variables
        stop_loop = False
        object_count = 1
        oa_equipment_list_dictionary = self.get_structure(
            structure_hierarchy=['AutoCreated', 'System', 'AirLoopHVAC', 'OutdoorAirSystem', 'EquipmentList', 'Base'])
        # iterate over build path returning every object up to the OutdoorAir:Mixer
        # if return fan is specified skip the first object as long as it is a (return) fan
        for idx, super_object in enumerate(build_path):
            for super_object_type, super_object_constructor in super_object.items():
                if getattr(self, 'return_fan', None) == 'Yes' and idx == 0:
                    if not re.match(r'Fan:.*', super_object_type):
                        raise PyExpandObjectsException('Return fan specified in template but is not the first object in '
                                                       'build path: {}'.format(build_path))
                    else:
                        continue
                if stop_loop:
                    break
                oa_equipment_list_dictionary['component_{}_object_type'.format(object_count)] = \
                    super_object_type
                oa_equipment_list_dictionary['component_{}_name'.format(object_count)] = \
                    super_object_constructor['Fields']['name']
                if super_object_type == 'OutdoorAir:Mixer':
                    stop_loop = True
                object_count += 1
        outdoor_air_equipment_list_object = self.yaml_list_to_epjson_dictionaries([
            {'AirLoopHVAC:OutdoorAirSystem:EquipmentList': oa_equipment_list_dictionary}, ])
        self.merge_epjson(
            super_dictionary=epjson,
            object_dictionary=self.resolve_objects(epjson=outdoor_air_equipment_list_object))
        return self.resolve_objects(epjson=outdoor_air_equipment_list_object)

    def _create_outdoor_air_system(self, epjson: dict = None) -> dict:
        """
        Create AirLoopHVAC:OutdoorAirSystem object from epJSON dictionary
        This list object is separated from the OptionTree build operations because it must seek out the correct
        ControllerList containing the OutdoorAir:Mixer object.

        :param epjson: system epJSON formatted dictionary
        :return: epJSON formatted AirLoopHVAC:OutdoorAirSystem objects.  These objects are also stored back to the
            input epJSON object.
        """
        epjson = epjson or self.epjson
        # find oa controllerlist by looking for the Controller:OutdoorAir
        oa_controller_list_name = None
        controller_list_objects = epjson.get('AirLoopHVAC:ControllerList')
        if controller_list_objects:
            for object_name, object_structure in controller_list_objects.items():
                for field, value in object_structure.items():
                    if re.match(r'controller_\d+_object_type', field) and value == 'Controller:OutdoorAir':
                        oa_controller_list_name = object_name
                        break
        if not oa_controller_list_name:
            raise PyExpandObjectsException("No outdoor air AirLoopHVAC:ControllerList present in the {} system "
                                           "build process, possibly because no Controller:OutdooAir object present "
                                           "in template creation process either.".format(self.unique_name))
        # get outdoor air system equipment list
        try:
            oa_system_equipment_list_object = epjson.get('AirLoopHVAC:OutdoorAirSystem:EquipmentList')
            (oa_system_equipment_name, _), = oa_system_equipment_list_object.items()
        except (ValueError, AttributeError):
            raise PyExpandObjectsException('Only one AirLoopHVAC:OutdoorAirSystem:EquipmentList object is allowed '
                                           'in {} template build process'.format(self.unique_name))
        # get availability manager list
        try:
            availability_manager_list_object = epjson.get('AvailabilityManagerAssignmentList')
            (availability_manager_name, _), = availability_manager_list_object.items()
        except (ValueError, AttributeError):
            raise PyExpandObjectsException('Only one AvailabilityManagerAssignmentList object is allowed in '
                                           '{} template build process'.format(self.unique_name))
        outdoor_air_system_yaml_object = \
            self.get_structure(structure_hierarchy=['AutoCreated', 'System', 'AirLoopHVAC', 'OutdoorAirSystem', 'Base'])
        outdoor_air_system_yaml_object['availability_manager_list_name'] = availability_manager_name
        outdoor_air_system_yaml_object['controller_list_name'] = oa_controller_list_name
        outdoor_air_system_yaml_object['outdoor_air_equipment_list_name'] = oa_system_equipment_name
        outdoor_air_system_list_object = self.yaml_list_to_epjson_dictionaries([
            {'AirLoopHVAC:OutdoorAirSystem': outdoor_air_system_yaml_object}, ])
        self.merge_epjson(
            super_dictionary=epjson,
            object_dictionary=self.resolve_objects(epjson=outdoor_air_system_list_object))
        return self.resolve_objects(epjson=outdoor_air_system_list_object)

    def _modify_build_path_for_outside_air_system(
            self, loop_type: str = 'AirLoop', epjson: dict = None, build_path: list = None) -> list:
        """
        Modify input build path to use AirLoopHVAC:OutdoorAirSystem as the first component, rather than individual
        outside air system components

        :param build_path: list of EnergyPlus Super objects
        :return: build path
        """
        # if build_path is not passed to function, get the class attributes
        epjson = epjson or self.epjson
        build_path = build_path or getattr(self, 'build_path', None)
        if not build_path:
            raise PyExpandObjectsException("Build path was not provided nor was it available as a class attribute")
        # The first object in the branch must be the AirLoopHVAC:OutdoorAirSystem that must be present in the epjson
        # from previous steps.
        outdoor_air_system = epjson.get('AirLoopHVAC:OutdoorAirSystem')
        if not outdoor_air_system:
            raise PyExpandObjectsException("No AirLoopHVAC:OutdoorAirSystem detected in {} build process"
                                           .format(self.unique_name))
        # iterate backwards over build_path and insert each object until the OutdoorAir:Mixer is hit.
        # Do first append with OutdoorAirSystem object
        parsed_build_path = []
        for super_object in copy.deepcopy(build_path)[::-1]:
            (super_object_type, super_object_structure), = super_object.items()
            if not super_object_type == 'OutdoorAir:Mixer':
                parsed_build_path.insert(0, super_object)
            else:
                # insert AirLoopHVAC:OutdoorAirSystem at the beginning.
                (outdoor_air_system_name, _), = outdoor_air_system.items()
                try:
                    parsed_build_path.insert(0, {
                        'AirLoopHVAC:OutdoorAirSystem': {
                            'Fields': {
                                'name': outdoor_air_system_name,
                                'inlet_node_name': super_object_structure['Fields']['return_air_stream_node_name'],
                                'outlet_node_name': super_object_structure['Fields']['mixed_air_node_name']
                            },
                            'Connectors': {
                                loop_type: {
                                    'Inlet': 'inlet_node_name',
                                    'Outlet': 'outlet_node_name'
                                }
                            }
                        }
                    })
                    break
                except (AttributeError, KeyError, ValueError):
                    raise PyExpandObjectsYamlStructureException("Error inserting AirLoopHVAC:OutdoorairSystem into "
                                                                "build path for system {}: {}"
                                                                .format(self.unique_name, build_path))
        # check that the outdoor air system was applied to the build path
        if 'AirLoopHVAC:OutdoorAirSystem' not in [list(i.keys())[0] for i in parsed_build_path]:
            raise PyExpandObjectsException("AirLoopHVAC:OutdoorAirSystem failed to be applied in {} build path {}"
                                           .format(self.unique_name, build_path))
        # check if a return fan is specified in the template.  If so, then copy the first object, which should be a fan
        # and also should have been skipped by the above process.  Insert the object into the list at the end of the
        # process at position 0
        if getattr(self, 'return_fan', None) == 'Yes':
            (return_fan_type, return_fan_structure), = build_path[0].items()
            if not re.match(r'Fan:.*', return_fan_type):
                raise PyExpandObjectsException('Return fan was specified in HVACTemplate:System, however, a fan was not '
                                               'the first object specified in the build path: {}'.format(build_path))
            else:
                parsed_build_path.insert(0, copy.deepcopy(build_path[0]))
        return parsed_build_path

    def _modify_build_path_for_equipment(
            self, loop_type: str = 'AirLoop', build_path: list = None) -> list:
        """
        Modify input build path to use special equipment objects in the build path, rather than individual components.

        :param build_path: list of EnergyPlus Super objects
        :return: build path
        """
        # todo_eo: move this to YAML file
        # todo_eo: Coil:Heating:.* will remove the heating coil and supplemental heating coil, might be an issue
        equipment_lookup = (
            (
                ['HVACTemplate:System:Unitary', ],
                'AirLoopHVAC:Unitary:.*',
                {'Inlet': 'furnace_air_inlet_node_name',
                 'Outlet': 'furnace_air_outlet_node_name'},
                (
                    ('Coil:Cooling.*', None if getattr(self, 'cooling_coil_type', 'None') == 'None' else True),
                    ('Coil:Heating.*', None if getattr(self, 'heating_coil_type', 'None') == 'None' else True),
                    ('Fan:.*', True))),
            (
                ['HVACTemplate:System:UnitarySystem', ],
                'AirLoopHVAC:Unitary*',
                {'Inlet': 'air_inlet_node_name',
                 'Outlet': 'air_outlet_node_name'},
                (
                    ('Coil:Cooling.*', None if getattr(self, 'cooling_coil_type', 'None') == 'None' else True),
                    ('Coil:Heating.*', None if getattr(self, 'heating_coil_type', 'None') == 'None' else True),
                    ('Fan:.*', True))),
            (
                ['HVACTemplate:System:UnitaryHeatPump:AirToAir', ],
                'AirLoopHVAC:UnitaryHeatPump.*',
                {'Inlet': 'air_inlet_node_name',
                 'Outlet': 'air_outlet_node_name'},
                (
                    ('Coil:Cooling.*', None if getattr(self, 'cooling_coil_type', 'None') == 'None' else True),
                    ('Coil:Heating.*', None if getattr(self, 'heat_pump_heating_coil_type', 'None') == 'None' else True),
                    ('Fan:.*', True))),
            (
                ['HVACTemplate:System:PackagedVAV', 'HVACTemplate:System:DedicatedOutdoorAir'],
                'CoilSystem:Cooling.*',
                {'Inlet': 'dx_cooling_coil_system_inlet_node_name',
                 'Outlet': 'dx_cooling_coil_system_outlet_node_name'},
                (
                    ('Coil:Cooling.*', None if getattr(self, 'cooling_coil_type', 'None') == 'None' else True), )))
        # if build_path is not passed to function, get the class attributes
        build_path = build_path or getattr(self, 'build_path', None)
        if not build_path:
            raise PyExpandObjectsException("Build path was not provided nor was it available as a class attribute")
        equipment_object = None
        for el in equipment_lookup:
            if self.template_type in el[0]:
                equipment_regex = el[1]
                equipment_connectors = el[2]
                # check for template indicators of objects to remove
                object_check_list = el[3]
                # The unitary equipment must be present, and extracted from, the build path
                for idx, super_object in enumerate(build_path):
                    (super_object_type, _), = super_object.items()
                    if re.match(equipment_regex, super_object_type):
                        equipment_object = build_path.pop(idx)
                        # set connectors now that it will be included in the build path.
                        #  This is not included in the YAML object to keep the object from connecting to its neighbors
                        #  before this point.
                        equipment_object[super_object_type]['Connectors'][loop_type] = equipment_connectors
                # make check if equipment object was found.  If not, return original build path
                if equipment_object:
                    try:
                        (_, equipment_object_keys), = equipment_object.items()
                        if {'Fields', 'Connectors'} != set(equipment_object_keys.keys()):
                            raise ValueError
                    except ValueError:
                        raise PyExpandObjectsException("Equipment is improperly formatted, must be a super"
                                                       "object. system: {} object: {}"
                                                       .format(self.unique_name, equipment_object))
                    # Iterate through list and remove objects that match the check list
                    parsed_build_path = []
                    removed_items = 0
                    for super_object in copy.deepcopy(build_path):
                        (super_object_type, super_object_structure), = super_object.items()
                        keep_object = True
                        for object_reference, object_presence in object_check_list:
                            if re.match(object_reference, super_object_type) and object_presence:
                                keep_object = None
                                removed_items += 1
                        if keep_object:
                            parsed_build_path.append(super_object)
                        # if object_check_list is empty, it's done.  Pass the equipment then proceed.  Add one to the
                        # removed_items so it isn't called again
                        if removed_items == len(object_check_list):
                            parsed_build_path.append(equipment_object)
                            removed_items += 1
                    if removed_items < sum(1 for i, j in object_check_list if j):
                        raise PyExpandObjectsException("Equipment modification process failed to remove all objects "
                                                       "for system {}".format(self.unique_name))
                    return parsed_build_path
                else:
                    return build_path
        # if no matches are made, return original build_path
        return build_path

    def _create_branch_and_branchlist_from_build_path(
            self,
            build_path: list = None,
            loop_type: str = 'AirLoop',
            epjson: dict = None):
        """
        Create Branch and BranchList objects from system build path
        These objects are separated from the OptionTree build operations because they vary based on the final build
        path.  Also, the Branch object must reference an AirLoopHVAC:OutdoorAirSystem object that is also built after
        the OptionTree build operations.

        :param build_path: system build path
        :param loop_type: string descriptor of the loop type, AirLoop by default
        :param epjson: epJSON dictionary
        :return: epJSON formatted Branch and BranchList objects.  These objects are also stored back to the
            input epJSON object.
        """
        # if build_path and/or epjson are not passed to function, get the class attributes
        epjson = epjson or self.epjson
        build_path = build_path or getattr(self, 'build_path', None)
        if not build_path:
            raise PyExpandObjectsException("Build path was not provided nor was it available as a class attribute")
        # Edit build path for AirLoopHVAC:OutdoorAirSystem
        build_path = self._modify_build_path_for_outside_air_system(
            epjson=epjson,
            build_path=copy.deepcopy(build_path))
        # Edit build path for special equipment
        build_path = self._modify_build_path_for_equipment(
            build_path=copy.deepcopy(build_path))
        components = []
        for super_object in copy.deepcopy(build_path):
            component = {}
            (super_object_type, super_object_structure), = super_object.items()
            try:
                connectors = super_object_structure.pop('Connectors')
            except KeyError:
                raise PyExpandObjectsYamlStructureException("Super object is missing Connectors key: {}"
                                                            .format(super_object))
            try:
                component['component_inlet_node_name'] = \
                    super_object_structure['Fields'][connectors[loop_type]['Inlet']]
                component['component_outlet_node_name'] = \
                    super_object_structure['Fields'][connectors[loop_type]['Outlet']]
                component['component_object_type'] = super_object_type
                component['component_name'] = super_object_structure['Fields']['name']
                components.append(component)
            except (AttributeError, KeyError):
                raise PyExpandObjectsYamlStructureException("Field/Connector mismatch or name not in Fields. "
                                                            "Object: {}, connectors: {}"
                                                            .format(super_object_structure, connectors))
        branch_fields = self.get_structure(structure_hierarchy=['AutoCreated', 'System', 'Branch', 'Base'])
        branch_fields['components'] = components
        branch = {
            "Branch": branch_fields
        }
        branchlist_fields = self.get_structure(structure_hierarchy=['AutoCreated', 'System', 'BranchList', 'Base'])
        branchlist = {
            "BranchList": branchlist_fields
        }
        branch_and_branchlist_objects = self.yaml_list_to_epjson_dictionaries([branch, branchlist])
        self.merge_epjson(
            super_dictionary=epjson,
            object_dictionary=self.resolve_objects(epjson=branch_and_branchlist_objects))
        return self.resolve_objects(epjson=branch_and_branchlist_objects)

    def run(self):
        """
        Process system template
        :return: class object with epJSON dictionary as class attribute
        """
        self.logger.info('Processing System: {}'.format(self.unique_name))
        if self.template_type == 'HVACTemplate:System:DualDuct':
            for duct_type, duct_field_name in (
                    ('ColdDuct', 'cold_duct'),
                    ('HotDuct', 'hot_duct')):
                # Make a copy of the class object and split to cold/hot class objects
                duct_system_class_object = copy.deepcopy(self)
                duct_system_class_object.template_type = ':'.join(['HVACTemplate:System:DualDuct', duct_type])
                # rename hot/cold duct to typical names now that their type is identified by the class
                for attribute in [i for i in vars(duct_system_class_object).keys() if i.startswith(duct_field_name)]:
                    setattr(duct_system_class_object, attribute.replace('cold_duct_', ''), getattr(duct_system_class_object, attribute))
                structure_hierarchy = duct_system_class_object.template_type.split(':')
                epjson_from_option_tree = duct_system_class_object._get_option_tree_objects(structure_hierarchy=structure_hierarchy)
                self.merge_epjson(
                    super_dictionary=self.epjson,
                    object_dictionary=duct_system_class_object.epjson)
                self.merge_epjson(
                    super_dictionary=self.epjson,
                    object_dictionary=epjson_from_option_tree)
            # rename main branch for processing
            for attribute in [i for i in vars(self).keys() if i.startswith(duct_field_name)]:
                setattr(self, attribute.replace('main_supply_fan', 'supply_fan'), getattr(self, attribute))
        self._create_objects()
        self._create_outdoor_air_equipment_list_from_build_path()
        self._create_availability_manager_assignment_list()
        self._create_controller_list_from_epjson()
        self._create_outdoor_air_system()
        self._create_branch_and_branchlist_from_build_path()
        return self


class ExpandPlantLoop(ExpandObjects):
    """
    Plant loop expansion operations
    """
    def __init__(self, template, epjson=None):
        super().__init__(template=template)
        self.unique_name = self.template_name
        self.epjson = epjson or self.epjson
        return

    def run(self):
        """
        Process plant loop template
        :return: class object with epJSON dictionary as class attribute
        """
        self.logger.info('Processing PlantLoop: {}'.format(self.unique_name))
        self._create_objects()
        self._create_availability_manager_assignment_list()
        return self


class RetrievePlantEquipmentLoop:
    """
    Get and set the a priority list of plant loops for the equipment to serve.
    """
    def __get__(self, obj, owner):
        return obj._template_plant_loop_type

    def __set__(self, obj, value):
        """
        Set priority list of plant loops to attach the equipment.  Apply defaults if no input is given.
        """
        # set value and check at the end for error output
        obj._template_plant_loop_type = None
        # create hash of object references and default loop types
        default_loops = {
            '^HVACTemplate:Plant:Tower.*': ['ChilledWaterLoop', 'MixedWaterLoop'],
            '^HVACTemplate:Plant:Chiller.*': ['ChilledWaterLoop', ],
            '^HVACTemplate:Plant:Boiler.*': ['HotWaterLoop', 'MixedWaterLoop'],
        }
        # If a string is passed, then use it as the entry
        if isinstance(value, str):
            obj._template_plant_loop_type = value if value.endswith('Loop') else ''.join([value, 'Loop'])
        else:
            # extract the template plant loop type
            # try/except not needed here because the template has already been validated from super class init
            (_, template_structure), = value['template'].items()
            (_, template_fields), = template_structure.items()
            template_plant_loop_type_list = []
            if template_fields.get('template_plant_loop_type'):
                template_plant_loop_type_list = [''.join([template_fields['template_plant_loop_type'], 'Loop']), ]
            else:
                # if loop reference was not made, set default based on template type
                (template_type, _), = value['template'].items()
                for object_reference, default_list in default_loops.items():
                    default_rgx = re.match(object_reference, template_type)
                    if default_rgx:
                        template_plant_loop_type_list = default_loops[object_reference]
                        break
            # Check the loop type priority list against the expanded loops and return the first match.
            plant_loops = [i.template_type.split(":")[-1] for i in value.get('plant_loop_class_objects', {}).values()]
            # Check that plant_loops has only unique entries and that it isn't empty
            if not plant_loops or len(list(set(plant_loops))) != len(list(plant_loops)):
                raise InvalidTemplateException("An invalid number of plant loops were created, either None or there"
                                               " are duplicates present: {}".format(plant_loops))
            for pl in template_plant_loop_type_list:
                if pl in plant_loops:
                    # Special handling for Tower object
                    (template_type, _), = value['template'].items()
                    if template_type in ['HVACTemplate:Plant:Tower', 'HVACTemplate:Plant:Tower:ObjectReference'] \
                            and pl == 'ChilledWaterLoop':
                        obj._template_plant_loop_type = 'CondenserWaterLoop'
                    else:
                        obj._template_plant_loop_type = pl
                    break
            # verify the field was set to a value
            if not obj._template_plant_loop_type:
                raise InvalidTemplateException("Plant equipment loop type did not have a corresponding loop to "
                                               "reference.  Priority list {}, Plant loops {}"
                                               .format(template_plant_loop_type_list, plant_loops))
        return


class ChillerAndCondenserType:
    """
    Set a class attribute to select the appropriate fan type and placement from TemplateOptions in the YAML lookup.
    """
    def __get__(self, obj, owner):
        return obj._chiller_and_condenser_type

    def __set__(self, obj, value):
        (template_type, template_structure), = value.items()
        (template_name, template_fields), = template_structure.items()
        if template_type == 'HVACTemplate:Plant:Chiller':
            chiller_type = template_fields.get('chiller_type', 'None')
            condenser_type = 'WaterCooled' if template_fields.get('condenser_type', 'None') == 'None' else \
                template_fields.get('condenser_type')
            obj._chiller_and_condenser_type = ''.join([chiller_type, condenser_type])
        return


class ExpandPlantEquipment(ExpandObjects):
    """
    Plant Equipment operations
    """

    template_plant_loop_type = RetrievePlantEquipmentLoop()
    chiller_and_condenser_type = ChillerAndCondenserType()

    def __init__(self, template, plant_loop_class_objects=None, epjson=None):
        """
        Initialize class

        :param template: HVACTemplate:Plant:(Chiller|Tower|Boiler) objects
        :param plant_loop_class_objects: dictionary of ExpandPlantLoop objects
        """
        super().__init__(template=template)
        self.unique_name = self.template_name
        plant_loops = {'plant_loop_class_objects': plant_loop_class_objects} if plant_loop_class_objects else {}
        self.template_plant_loop_type = {'template': template, **plant_loops}
        self.chiller_and_condenser_type = template
        self.epjson = epjson or self.epjson
        return

    def run(self):
        """
        Process plant loop template
        :return: class object with epJSON dictionary as class attribute
        """
        self.logger.info('Processing Plant Equipment: {}'.format(self.unique_name))
        self._create_objects()
        return self
