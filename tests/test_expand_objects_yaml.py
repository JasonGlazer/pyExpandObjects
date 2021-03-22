import unittest

from src.expand_objects import ExpandObjects
from src.expand_objects import PyExpandObjectsTypeError, PyExpandObjectsYamlStructureException
from . import BaseTest

mock_template = {
    'HVACTemplate:Thermostat': {
        'template_name': {
            'template_field': 'template_test_value'
        }
    }
}

mock_option_tree = {
    'OptionTree': {
        'Zone': {
            'VAV': {
                'Template': {
                    'BuildPath': [
                        {
                            'AirTerminal:SingleDuct:VAV:Reheat': {
                                'Fields': {
                                    'name': '{} VAV Reheat',
                                    'maximum_air_flow_rate': 'Autosize',
                                },
                                'Connectors': {
                                }
                            }
                        },
                        {
                            'Coil:Heating:Water': {
                                'Fields': {
                                    'name': '{} Reheat Coil',
                                    'air_inlet_node_name': '{} Damper Outlet',
                                    'air_outlet_node_name': '{} Supply Inlet',
                                },
                                'Connectors': {
                                    'AirLoop': {
                                        'Inlet': 'air_inlet_node_name',
                                        'Outlet': 'air_outlet_node_name'
                                    },
                                    'HotWaterLoop': {
                                        'Inlet': 'water_inlet_node_name',
                                        'Outlet': 'water_outlet_node_name'
                                    }
                                }
                            }
                        }
                    ],
                    'Transitions': {
                        "template_field": {
                            "AirTerminal:.*": "object_test_field"
                        }
                    }
                }
            },
            'InsertElement': {},
            'ReplaceElement': {},
            'RemoveElement': {},
            'AdditionalObjects': {},
            'AdditionalTemplateObjects': {}
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
        self.assertEqual('object_test_field', output['Template']['Transitions']["template_field"]['AirTerminal:.*'])
        # test without OptionTree
        structure_hierarcy = ['Zone', 'VAV']
        output = eo.get_option_tree(structure_hierarchy=structure_hierarcy)
        self.assertEqual('object_test_field', output['Template']['Transitions']["template_field"]['AirTerminal:.*'])
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
                            'InsertElement': {},
                            'ReplaceElement': {},
                            'RemoveElement': {},
                            'AdditionalObjects': {},
                            'AdditionalTemplateObjects': {}
                        }
                    }
                }
            }
        )
        structure_hierarchy = ['OptionTree', 'Zone', 'VAV']
        with self.assertRaises(PyExpandObjectsYamlStructureException):
            eo.get_option_tree(structure_hierarchy=structure_hierarchy)
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Base:Retrieve build path")
    def test_retrieve_build_path(self):
        eo = ExpandObjects(
            template=mock_template,
            expansion_structure=mock_option_tree)
        structure_hierarcy = ['OptionTree', 'Zone', 'VAV']
        option_tree = eo.get_option_tree(structure_hierarchy=structure_hierarcy)
        build_path = eo._get_option_tree_leaf(option_tree=option_tree, leaf_path=['Template', ])
        key_check = True
        for k in build_path.keys():
            if k not in ['objects', 'transitions']:
                key_check = False
        self.assertTrue(key_check)
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Base:Retrieve build path without transition key")
    def test_retrieve_build_path_without_transitions(self):
        mock_option_tree['OptionTree']['Zone']['VAV']['Template'].pop('Transitions')
        eo = ExpandObjects(
            template=mock_template,
            expansion_structure=mock_option_tree)
        structure_hierarcy = ['OptionTree', 'Zone', 'VAV']
        option_tree = eo.get_option_tree(structure_hierarchy=structure_hierarcy)
        build_path = eo._get_option_tree_leaf(option_tree=option_tree, leaf_path=['Template', ])
        self.assertIsNone(build_path['transitions'])
        return

    def test_apply_transitions(self):
        # todo_eo: make comments and do better documentation on _get_opttion_tree_leaf and _apply_transitions
        eo = ExpandObjects(
            template=mock_template,
            expansion_structure=mock_option_tree)
        structure_hierarcy = ['OptionTree', 'Zone', 'VAV']
        option_tree = eo.get_option_tree(structure_hierarchy=structure_hierarcy)
        build_path = eo._get_option_tree_leaf(option_tree=option_tree, leaf_path=['Template', ])
        transitioned_build_path = eo._apply_transitions(build_path)
        self.assertEqual(
            'template_test_value',
            transitioned_build_path['objects'][0]['AirTerminal:SingleDuct:VAV:Reheat']['Fields']['object_test_field'])
        return
