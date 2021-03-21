import unittest

from src.expand_objects import ExpandObjects
from src.expand_objects import PyExpandObjectsTypeError, PyExpandObjectsYamlStructureException
from . import BaseTest

mock_template = {
    'HVACTemplate:Thermostat': {
        'template_name': {
            'field': 'value'
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
                        "test_key": "test_val"
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
        self.assertEqual('test_val', output['Template']['Transitions']['test_key'])
        # test without OptionTree
        structure_hierarcy = ['Zone', 'VAV']
        output = eo.get_option_tree(structure_hierarchy=structure_hierarcy)
        self.assertEqual('test_val', output['Template']['Transitions']['test_key'])
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
        build_path = eo._get_build_path(option_tree=option_tree)
        key_check = True
        for k in build_path.keys():
            if k not in ['build_path', 'transitions']:
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
        build_path = eo._get_build_path(option_tree=option_tree)
        print(build_path)
        self.assertIsNone(build_path['transitions'])
        return
