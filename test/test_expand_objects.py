import unittest
import os

from expand_objects.expand_objects import ExpandObjects
from test import BaseTest

this_script_path = os.path.dirname(
    os.path.abspath(__file__)
)


class TestExpandThermostats(BaseTest, unittest.TestCase):
    def setUp(self):
        return

    def teardown(self):
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Base:Verify file location exists")
    def test_reject_bad_expansion_file_path(self):
        expansion_file_location = 'does/not/exist.yaml'
        with self.assertRaises(FileNotFoundError):
            ExpandObjects(template={"test", ''}, expansion_structure=expansion_file_location)
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Base:Reject non-yaml structure files")
    def test_reject_bad_expansion_file_format(self):
        expansion_file_location = os.path.abspath(__file__)
        with self.assertRaises(TypeError):
            ExpandObjects(template={"test", ''}, expansion_structure=expansion_file_location)
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Base:Accept preconfigured dictionaries")
    def test_expansion_dictionary_okay(self):
        expansion_dictionary = {'test': 'val'}
        expand_object = ExpandObjects(template={"test", ''}, expansion_structure=expansion_dictionary)
        self.assertEqual('val', expand_object.expansion_structure['test'])
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Base:Reject other reference types")
    def test_expansion_dictionary_okay(self):
        expansion_dictionary = []
        with self.assertRaises(TypeError):
            ExpandObjects(template={"test", ''}, expansion_structure=expansion_dictionary)
        return
