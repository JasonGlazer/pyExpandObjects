import unittest
import os
import re

from src.expand_objects import ExpandObjects
from src.expand_objects import InvalidTemplateException
from . import BaseTest

mock_template = {
    'template_name': {
        'field': 'value'
    }
}


class TestExpandThermostats(BaseTest, unittest.TestCase):
    def setUp(self):
        return

    def teardown(self):
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Base:Verify file location exists")
    def test_reject_bad_expansion_file_path(self):
        expansion_file_location = 'does/not/exist.yaml'
        with self.assertRaises(FileNotFoundError):
            ExpandObjects(template=mock_template, expansion_structure=expansion_file_location)
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Base:Reject non-yaml structure files")
    def test_reject_bad_expansion_file_format(self):
        expansion_file_location = os.path.abspath(__file__)
        with self.assertRaises(TypeError):
            ExpandObjects(template=mock_template, expansion_structure=expansion_file_location)
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Base:Accept preconfigured dictionaries")
    def test_expansion_dictionary_okay(self):
        expansion_dictionary = {'test': 'val'}
        expand_object = ExpandObjects(
            template=mock_template,
            expansion_structure=expansion_dictionary)
        self.assertEqual('val', expand_object.expansion_structure['test'])
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Base:Reject other reference types")
    def test_bad_expansion_dictionary_rejected(self):
        expansion_dictionary = []
        with self.assertRaises(TypeError):
            ExpandObjects(template=mock_template, expansion_structure=expansion_dictionary)
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Base:Retrieve YAML object")
    def test_retrieve_structure(self):
        structure_hierarchy = ['Schedule', 'Compact', 'ALWAYS_VAL']
        eo = ExpandObjects(template=mock_template)
        structure = eo.get_structure(structure_hierarchy=structure_hierarchy)
        name_match_rgx = re.compile(r'^HVACTemplate.*')
        name_match = False
        if re.match(name_match_rgx, structure['name']):
            name_match = True
        self.assertTrue(name_match)
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Base:Reject bad YAML object")
    def test_exception_with_bad_structure(self):
        structure_hierarchy = ['Schedule', 'Compact', 'Bad']
        with self.assertRaises(TypeError):
            eo = ExpandObjects(template=mock_template)
            eo.get_structure(structure_hierarchy=structure_hierarchy)
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Base:Reject bad template object")
    def test_reject_bad_template(self):
        templates = {}
        with self.assertRaises(InvalidTemplateException):
            ExpandObjects(template=templates)
        templates = []
        with self.assertRaises(TypeError):
            ExpandObjects(template=templates)
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Base:Create always value schedule")
    def test_make_compact_schedule_always_val(self):
        structure_hierarchy = ['Schedule', 'Compact', 'ALWAYS_VAL']
        eo = ExpandObjects(template=mock_template)
        schedule = eo.build_compact_schedule(structure_hierarchy=structure_hierarchy, insert_values=[3, ])
        (schedule_name, schedule_fields), = schedule['Schedule:Compact'].items()
        name_match_rgx = re.compile(r'^HVACTemplate-Always3')
        name_match = False
        if re.match(name_match_rgx, schedule_name):
            name_match = True
        self.assertTrue(name_match)
        set_value = schedule_fields['data'][-1]['field']
        self.assertEqual(3, set_value)
        return
