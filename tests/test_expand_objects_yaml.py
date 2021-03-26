import unittest
import copy
import json

from src.expand_objects import ExpandObjects, ExpandZone
from src.expand_objects import PyExpandObjectsTypeError, PyExpandObjectsYamlStructureException
from . import BaseTest

mock_template = {
    'HVACTemplate:Zone:VAV': {
        'template_name': {
            'template_field': 'template_test_value',
            'template_field2': 'test_pre_mapped_value',
            'reheat_coil_type': 'HotWater',
            'zone_name': 'test zone'
        }
    }
}

mock_option_tree = {
    'OptionTree': {
        'Zone': {
            'VAV': {
                'BaseObjects': {
                    "Objects": [
                        {
                            'ZoneHVAC:AirDistributionUnit': {
                                "name": "{} ATU",
                                "field_name": "field_value"
                            }
                        }
                    ],
                    'Transitions': {
                        "template_field": {
                            "ZoneHVAC:AirDistributionUnit": "object_test_field"
                        },
                        "template_field2": {
                            "ZoneHVAC:AirDistributionUnit": "object_test_field2"
                        }
                    },
                    'Mappings': {
                        'ZoneHVAC:AirDistributionUnit': {
                            "object_test_field2": {
                                "test_pre_mapped_value": "test_mapped_value"
                            }
                        }
                    }
                },
                'TemplateObjects': {
                    'reheat_coil_type': {
                        "HotWater": {
                            'Objects': [
                                [
                                    {
                                        'AirTerminal:SingleDuct:VAV:Reheat': {
                                            'name': '{} VAV Reheat',
                                            'maximum_air_flow_rate': 'Autosize',
                                        }
                                    }
                                ],
                                {
                                    "Branch": {
                                        "name": "{} HW Branch"
                                    }
                                }
                            ],
                            'Transitions': {
                                "template_field": {
                                    "AirTerminal:.*": "object_test_field"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}


class TestExpandObjectsYaml(BaseTest, unittest.TestCase):
    """
    General handling and processing of YAML instructions
    """
    def setUp(self):
        return

    def teardown(self):
        return

    def test_get_option_tree_from_yaml(self):
        eo = ExpandObjects(
            template=mock_template,
            expansion_structure=mock_option_tree)
        structure_hierarcy = ['OptionTree', 'Zone', 'VAV']
        output = eo._get_option_tree(structure_hierarchy=structure_hierarcy)
        key_check = True
        try:
            output['BaseObjects']
        except KeyError:
            key_check = False
        self.assertTrue(key_check)
        # test without OptionTree
        structure_hierarchy = ['Zone', 'VAV']
        output = eo._get_option_tree(structure_hierarchy=structure_hierarchy)
        key_check = True
        try:
            output['BaseObjects']
        except KeyError:
            key_check = False
        self.assertTrue(key_check)
        return

    def test_reject_bad_option_tree_request(self):
        eo = ExpandObjects(
            template=mock_template,
            expansion_structure=mock_option_tree)
        structure_hierarchy = 'BadString'
        with self.assertRaises(PyExpandObjectsTypeError):
            eo._get_option_tree(structure_hierarchy=structure_hierarchy)
        return

    def test_reject_bad_option_tree_structure(self):
        eo = ExpandObjects(
            template=mock_template,
            expansion_structure={
                'OptionTree': {
                    'Zone': {
                        'VAV': {
                            'BadKey': {},
                            'InsertObject': {},
                            'ReplaceObject': {},
                            'RemoveObject': {},
                            'Objects': {},
                            'TemplateObjects': {}
                        }
                    }
                }
            }
        )
        structure_hierarchy = ['OptionTree', 'Zone', 'VAV']
        with self.assertRaises(PyExpandObjectsYamlStructureException):
            eo._get_option_tree(structure_hierarchy=structure_hierarchy)
        return

    def test_option_tree_leaf(self):
        eo = ExpandObjects(
            template=mock_template,
            expansion_structure=mock_option_tree)
        structure_hierarchy = ['OptionTree', 'Zone', 'VAV']
        option_tree = eo._get_option_tree(structure_hierarchy=structure_hierarchy)
        option_tree_leaf = eo._get_option_tree_leaf(option_tree=option_tree, leaf_path=['BaseObjects', ])
        key_check = True
        for k in option_tree_leaf.keys():
            if k not in ['Objects', 'Transitions', 'Mappings']:
                key_check = False
        self.assertTrue(key_check)
        return

    def test_option_tree_leaf_without_transitions(self):
        # remove Transitions for this test
        bad_mock_option_tree = copy.deepcopy(mock_option_tree)
        bad_mock_option_tree['OptionTree']['Zone']['VAV']['BaseObjects'].pop('Transitions')
        eo = ExpandObjects(
            template=mock_template,
            expansion_structure=bad_mock_option_tree)
        structure_hierarchy = ['OptionTree', 'Zone', 'VAV']
        option_tree = eo._get_option_tree(structure_hierarchy=structure_hierarchy)
        option_tree_leaf = eo._get_option_tree_leaf(option_tree=option_tree, leaf_path=['BaseObjects', ])
        self.assertIsNone(option_tree_leaf['Transitions'])
        return

    def test_apply_transitions(self):
        eo = ExpandObjects(
            template=mock_template,
            expansion_structure=mock_option_tree)
        structure_hierarchy = ['OptionTree', 'Zone', 'VAV']
        option_tree = eo._get_option_tree(structure_hierarchy=structure_hierarchy)
        option_tree_leaf = eo._get_option_tree_leaf(option_tree=option_tree, leaf_path=['BaseObjects', ])
        transitioned_option_tree_leaf = eo._apply_transitions(option_tree_leaf)
        self.assertEqual(
            'template_test_value',
            transitioned_option_tree_leaf[0]['ZoneHVAC:AirDistributionUnit']['object_test_field'])
        return

    def test_apply_transitions_and_map(self):
        eo = ExpandObjects(
            template=mock_template,
            expansion_structure=mock_option_tree)
        structure_hierarchy = ['OptionTree', 'Zone', 'VAV']
        option_tree = eo._get_option_tree(structure_hierarchy=structure_hierarchy)
        option_tree_leaf = eo._get_option_tree_leaf(option_tree=option_tree, leaf_path=['BaseObjects', ])
        transitioned_option_tree_leaf = eo._apply_transitions(option_tree_leaf)
        self.assertEqual(
            'test_mapped_value',
            transitioned_option_tree_leaf[0]['ZoneHVAC:AirDistributionUnit']['object_test_field2'])
        return

    def test_yaml_list_to_dictionary_regular_object(self):
        dict_1 = {
            "Object:1": {
                "name": "test_name",
                "field_1": "val_1"
            }
        }
        eo = ExpandZone(template=mock_template)
        output = eo._yaml_list_to_epjson_dictionaries([dict_1, ])
        self.assertEqual('val_1', output['Object:1']['test_name']['field_1'])
        return

    def test_yaml_list_to_dictionary_super_object(self):
        dict_1 = {
            "Object:1": {
                "Fields": {
                    "name": "test_name",
                    "field_1": "val_1"
                },
                "Connectors": {}
            }
        }
        eo = ExpandZone(template=mock_template)
        output = eo._yaml_list_to_epjson_dictionaries([dict_1, ])
        self.assertEqual('val_1', output['Object:1']['test_name']['field_1'])
        return

    def test_warning_on_bad_apply_transitions(self):
        # make a bad template reference
        bad_mock_option_tree = mock_option_tree
        bad_mock_option_tree['OptionTree']['Zone']['VAV']['BaseObjects']['Transitions'] = {
            "template_bad_field": {
                "ZoneHVAC:AirDistributionUnit": "object_test_field"
            }
        }
        eo = ExpandObjects(
            template=mock_template,
            expansion_structure=bad_mock_option_tree)
        structure_hierarchy = ['OptionTree', 'Zone', 'VAV']
        option_tree = eo._get_option_tree(structure_hierarchy=structure_hierarchy)
        option_tree_leaf = eo._get_option_tree_leaf(option_tree=option_tree, leaf_path=['BaseObjects', ])
        eo._apply_transitions(option_tree_leaf)
        # Logger (Parent class of ExpandObjects) keeps logs in self.stream
        self.assertIn('Template field (template_bad_field) was', eo.stream.getvalue())
        return

    def test_error_on_bad_object(self):
        # make a bad template reference
        # check missing 'name' field
        bad_mock_option_tree = copy.deepcopy(mock_option_tree)
        bad_mock_option_tree['OptionTree']['Zone']['VAV']['BaseObjects']['Objects'] = [
            {
                'ZoneHVAC:AirDistributionUnit': {
                    "bad_name": "{} ATU"
                }
            }
        ]
        eo = ExpandObjects(
            template=mock_template,
            expansion_structure=bad_mock_option_tree)
        structure_hierarchy = ['OptionTree', 'Zone', 'VAV']
        option_tree = eo._get_option_tree(structure_hierarchy=structure_hierarchy)
        option_tree_leaf = eo._get_option_tree_leaf(option_tree=option_tree, leaf_path=['BaseObjects', ])
        object_list = eo._apply_transitions(option_tree_leaf)
        with self.assertRaises(PyExpandObjectsYamlStructureException):
            eo._yaml_list_to_epjson_dictionaries(object_list)
        # more than one object in a dictionary
        bad_mock_option_tree = copy.deepcopy(mock_option_tree)
        bad_mock_option_tree['OptionTree']['Zone']['VAV']['BaseObjects']['Objects'] = [
            {
                'ZoneHVAC:AirDistributionUnit': {
                    "name": "{} ATU"
                },
                'ZoneHVAC:AirDistributionUnit2': {
                    "name": "{} ATU"
                }
            }
        ]
        eo = ExpandObjects(
            template=mock_template,
            expansion_structure=bad_mock_option_tree)
        structure_hierarchy = ['OptionTree', 'Zone', 'VAV']
        option_tree = eo._get_option_tree(structure_hierarchy=structure_hierarchy)
        option_tree_leaf = eo._get_option_tree_leaf(option_tree=option_tree, leaf_path=['BaseObjects', ])
        object_list = eo._apply_transitions(option_tree_leaf)
        with self.assertRaises(PyExpandObjectsYamlStructureException):
            eo._yaml_list_to_epjson_dictionaries(object_list)
        return

    def test_retrieve_objects_from_option_tree(self):
        eo = ExpandZone(template=mock_template)
        structure_hierarchy = ['OptionTree', 'HVACTemplate', 'Zone', 'VAV']
        template_objects = eo._get_option_tree_objects(structure_hierarchy=structure_hierarchy)
        key_check = True
        for key in template_objects.keys():
            if key not in [
                    'ZoneHVAC:AirDistributionUnit',
                    'ZoneHVAC:EquipmentList',
                    'ZoneHVAC:EquipmentConnections',
                    'DesignSpecification:OutdoorAir',
                    'DesignSpecification:ZoneAirDistribution',
                    'Sizing:Zone',
                    'AirTerminal:SingleDuct:VAV:Reheat',
                    'Coil:Heating:Water',
                    'Branch']:
                key_check = False
            self.assertTrue(key_check)
        return

    def test_complex_inputs_simple(self):
        test_d = {
            "Object:1": {
                "name_1": {
                    "field_1": "value_1"
                }
            }
        }
        eo = ExpandZone(template=mock_template)
        # string test
        output = eo._resolve_complex_input(
            epjson=test_d,
            field_name="field_1",
            input_value="{} test_val"
        )
        self.assertEqual('test zone test_val', [i for i in output][0]["value"])
        # number test
        output = eo._resolve_complex_input(
            epjson=test_d,
            field_name="field_1",
            input_value=3
        )
        self.assertEqual(3, [i for i in output][0]["value"])
        return

    def test_complex_inputs_dictionary(self):
        test_d = {
            "Object:1": {
                "name_1": {
                    "field_1": "value_1"
                }
            }
        }
        eo = ExpandZone(template=mock_template)
        # field value check
        output = eo._resolve_complex_input(
            epjson=test_d,
            field_name="field_1",
            input_value={
                "Object:1": "field_1"
            }
        )
        tmp_d = {}
        for o in output:
            tmp_d[o['field']] = o['value']
        self.assertEqual('field_1', list(tmp_d.keys())[0])
        self.assertEqual('value_1', tmp_d['field_1'])
        # dictionary key check
        output = eo._resolve_complex_input(
            epjson=test_d,
            field_name="field_1",
            input_value={
                "Object:1": "self"
            }
        )
        tmp_d = {}
        for o in output:
            tmp_d[o['field']] = o['value']
        self.assertEqual('Object:1', tmp_d['field_1'])
        # name check
        output = eo._resolve_complex_input(
            epjson=test_d,
            field_name="field_1",
            input_value={
                "Object:1": "key"
            }
        )
        tmp_d = {}
        for o in output:
            tmp_d[o['field']] = o['value']
        self.assertEqual('name_1', tmp_d['field_1'])
        return

    def test_complex_inputs_recursion_dictionary(self):
        test_d = {
            "Object:1": {
                "name_1": {
                    "field_1": "value_1"
                }
            },
            "Object:2": {
                "name_1": {
                    "field_1": {
                        "Object:1": "field_1"
                    }
                }
            }
        }
        eo = ExpandZone(template=mock_template)
        # field value check
        output = eo._resolve_complex_input(
            epjson=test_d,
            field_name="field_test",
            input_value={
                "Object:2": "field_1"
            }
        )
        tmp_d = {}
        for o in output:
            tmp_d[o['field']] = o['value']
        self.assertEqual('value_1', tmp_d['field_test'])
        return

    def test_complex_inputs_recursion_limit(self):
        test_d = {
            "Object:1": {
                "name_1": {
                    "field_1": {
                        "Object:2": "field_1"
                    }
                }
            },
            "Object:2": {
                "name_1": {
                    "field_1": {
                        "Object:1": "field_1"
                    }
                }
            }
        }
        eo = ExpandObjects(
            template=mock_template,
            expansion_structure=mock_option_tree)
        with self.assertRaises(PyExpandObjectsYamlStructureException):
            output = eo._resolve_complex_input(
                epjson=test_d,
                field_name="field_test",
                input_value={
                    "Object:2": "field_1"
                }
            )
            tmp_d = {}
            for o in output:
                tmp_d[o['field']] = o['value']
        return

    def test_complex_inputs_list(self):
        test_d = {
            "Object:2": {
                "name_1": {
                    "field_1": "value_1"
                }
            }
        }
        eo = ExpandZone(template=mock_template)
        # field value check
        output = eo._resolve_complex_input(
            epjson=test_d,
            field_name="field_test",
            input_value=[
                {"field_sub_test": {"Object:2": "field_1"}}
            ]
        )
        tmp_d = {}
        for o in output:
            tmp_d[o['field']] = o['value']
        self.assertEqual('value_1', tmp_d['field_test'][0]['field_sub_test'])
        return

    def test_complex_inputs_list_recursion(self):
        test_d = {
            "Object:1": {
                "name_1": {
                    "field_1": "value_1"
                }
            },
            "Object:2": {
                "name_1": {
                    "field_1": {
                        "Object:1": "field_1"
                    }
                }
            }
        }
        eo = ExpandZone(template=mock_template)
        # field value check
        output = eo._resolve_complex_input(
            epjson=test_d,
            field_name="field_test",
            input_value=[
                {"field_sub_test": {"Object:2": "field_1"}}
            ]
        )
        tmp_d = {}
        for o in output:
            tmp_d[o['field']] = o['value']
        self.assertEqual('value_1', tmp_d['field_test'][0]['field_sub_test'])
        return

    def test_resolve_complex_inputs_object(self):
        test_d = {
            "Object:1": {
                "name_1": {
                    "field_1": "value_1"
                }
            },
            "Object:2": {
                "name_1": {
                    "field_1": {
                        "Object:1": "field_1"
                    }
                }
            }
        }
        eo = ExpandZone(template=mock_template)
        eo._resolve_objects(epjson=test_d)
        self.assertEqual('value_1', test_d['Object:2']['name_1']['field_1'])
        return

    def test_complex_nested_test(self):
        test_d = {
            'AirTerminal:SingleDuct:VAV:Reheat': {
                'SPACE1-1 VAV Reheat': {
                    'air_inlet_node_name': '{} Zone Equip Inlet',
                    'air_outlet_node_name': '{} Supply Inlet',
                    'damper_air_outlet_node_name': '{} Damper Outlet',
                    'damper_heating_action': 'Reverse',
                    'maximum_air_flow_rate': 'Autosize',
                    'maximum_hot_water_or_steam_flow_rate': 'Autosize',
                    'reheat_coil_name': '{} Reheat Coil',
                    'reheat_coil_object_type': 'Coil:Heating:Water',
                    'zone_minimum_air_flow_input_method': 'Constant'}},
            'Branch': {
                'SPACE1-1 HW Reheat Branch': {
                    'components': [
                        {
                            'component_inlet_node_name': {'Coil:Heating:Water': 'water_inlet_node_name'},
                            'component_name': {'Coil:Heating:Water': 'key'},
                            'component_object_type': {'Coil:Heating:Water': 'self'},
                            'component_outlet_node_name': {'Coil:Heating:Water': 'water_outlet_node_name'}
                        }
                    ]
                }
            },
            'Coil:Heating:Water': {
                'SPACE1-1 Reheat Coil': {
                    'air_inlet_node_name': '{} Damper Outlet',
                    'air_outlet_node_name': '{} Supply Inlet',
                    'maximum_water_flow_rate': 'Autosize',
                    'performance_input_method': 'UFactorTimesAreaAndDesignWaterFlowRate',
                    'rated_capacity': 'Autosize',
                    'rated_inlet_air_temperature': 16.6,
                    'rated_inlet_water_temperature': 82.2,
                    'rated_outlet_air_temperature': 32.2,
                    'rated_outlet_water_temperature': 71.1,
                    'rated_ratio_for_air_and_water_convection': 0.5,
                    'u_factor_times_area_value': 'Autosize',
                    'water_inlet_node_name': '{} Heating Coil Hw Inlet',
                    'water_outlet_node_name': '{} Heating Coil Hw Outlet'}},
            'ZoneHVAC:AirDistributionUnit': {
                'SPACE1-1 ATU': {
                    'air_distribution_unit_outlet_node_name':
                        {'^AirTerminal:.*': 'air_outlet_node_name'},
                    'air_terminal_name':
                        {'^AirTerminal:.*': 'key'},
                    'air_terminal_object_type':
                        {'^AirTerminal:.*': 'self'}
                }
            }
        }
        eo = ExpandZone(
            template=mock_template)
        eo._resolve_objects(epjson=test_d)
        # Check that no string remains unformatted.  The * and ^ are the common regex special characters.
        json_string = json.dumps(test_d)
        self.assertNotIn('{}', json_string)
        self.assertNotIn('^', json_string)
        self.assertNotIn('*', json_string)
        return
