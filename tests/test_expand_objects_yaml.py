import unittest

from src.expand_objects import ExpandObjects
from src.expand_objects import PyExpandObjectsTypeError, PyExpandObjectsYamlStructureException
from . import BaseTest

mock_template = {
    'HVACTemplate:Zone:VAV': {
        'template_name': {
            'template_field': 'template_test_value'
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
                                "name": "{} ATU"
                            }
                        }
                    ],
                    'Transitions': {
                        "template_field": {
                            "ZoneHVAC:AirDistributionUnit": "object_test_field"
                        }
                    }
                },
                'TemplateObjects': [
                    {
                        'reheat_coil_type': {
                            "HotWater": {
                                'Objects': [
                                    {
                                        'AirTerminal:SingleDuct:VAV:Reheat': {
                                            'name': '{} VAV Reheat',
                                            'maximum_air_flow_rate': 'Autosize',
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
                ]
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

    @BaseTest._test_logger(doc_text="HVACTemplate:Base:Get Option Tree")
    def test_get_option_tree_from_yaml(self):
        eo = ExpandObjects(
            template=mock_template,
            expansion_structure=mock_option_tree)
        structure_hierarcy = ['OptionTree', 'Zone', 'VAV']
        output = eo.get_option_tree(structure_hierarchy=structure_hierarcy)
        key_check = True
        try:
            output['BaseObjects']
        except KeyError:
            key_check = False
        self.assertTrue(key_check)
        # test without OptionTree
        structure_hierarchy = ['Zone', 'VAV']
        output = eo.get_option_tree(structure_hierarchy=structure_hierarchy)
        key_check = True
        try:
            output['BaseObjects']
        except KeyError:
            key_check = False
        self.assertTrue(key_check)
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Base:Reject bad OptionTree request")
    def test_reject_bad_option_tree_request(self):
        eo = ExpandObjects(
            template=mock_template,
            expansion_structure=mock_option_tree)
        structure_hierarchy = 'BadString'
        with self.assertRaises(PyExpandObjectsTypeError):
            eo.get_option_tree(structure_hierarchy=structure_hierarchy)
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Base:Fail on bad returned structure")
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
            eo.get_option_tree(structure_hierarchy=structure_hierarchy)
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Base:Retrieve option tree branch")
    def test_retrieve_base_option_tree_leaf(self):
        eo = ExpandObjects(
            template=mock_template,
            expansion_structure=mock_option_tree)
        structure_hierarcy = ['OptionTree', 'Zone', 'VAV']
        option_tree = eo.get_option_tree(structure_hierarchy=structure_hierarcy)
        option_tree_leaf = eo._get_option_tree_leaf(option_tree=option_tree, leaf_path=['BaseObjects', ])
        key_check = True
        for k in option_tree_leaf.keys():
            if k not in ['Objects', 'Transitions']:
                key_check = False
        self.assertTrue(key_check)
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Base:Retrieve build path without transition key")
    def test_retrieve_base_leaf_without_transitions(self):
        # remove Transitions for this test
        mock_option_tree['OptionTree']['Zone']['VAV']['BaseObjects'].pop('Transitions')
        eo = ExpandObjects(
            template=mock_template,
            expansion_structure=mock_option_tree)
        structure_hierarcy = ['OptionTree', 'Zone', 'VAV']
        option_tree = eo.get_option_tree(structure_hierarchy=structure_hierarcy)
        option_tree_leaf = eo._get_option_tree_leaf(option_tree=option_tree, leaf_path=['BaseObjects', ])
        self.assertIsNone(option_tree_leaf['Transitions'])
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Base:Apply transitions to an object")
    def test_apply_transitions(self):
        eo = ExpandObjects(
            template=mock_template,
            expansion_structure=mock_option_tree)
        structure_hierarcy = ['OptionTree', 'Zone', 'VAV']
        option_tree = eo.get_option_tree(structure_hierarchy=structure_hierarcy)
        option_tree_leaf = eo._get_option_tree_leaf(option_tree=option_tree, leaf_path=['BaseObjects', ])
        transitioned_option_tree_leaf = eo._apply_transitions(option_tree_leaf)
        self.assertEqual(
            'template_test_value',
            transitioned_option_tree_leaf['Objects'][0]['ZoneHVAC:AirDistributionUnit']['object_test_field'])
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Base:Write warning on failed applying of transition fields")
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
        option_tree = eo.get_option_tree(structure_hierarchy=structure_hierarchy)
        option_tree_leaf = eo._get_option_tree_leaf(option_tree=option_tree, leaf_path=['BaseObjects', ])
        eo._apply_transitions(option_tree_leaf)
        # Logger (Parent class of ExpandObjects) keeps logs in self.stream
        self.assertIn('Template field (template_bad_field) was', eo.stream.getvalue())
        return

    # todo_eo: test function to get template inputs.
    # convert each item to regular object {object_type: {object_name: object_fields}} and combine in epJSON dictionary
    # using merge_dictionary.  Make sure to flatten list of objects, or iterate though each sub-list.
    # These will have unresolved references (i.e. complex inputs)
    # Build complex input function
    # todo_eo: perform complex input for each object in dictionary, using recursion if another complex input is found.
