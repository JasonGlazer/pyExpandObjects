from pathlib import Path
import unittest

from expand_objects import ExpandObjects


class TestExpandObject(unittest.TestCase):
    def setUp(self):
        self.expand_object = ExpandObjects()
        self.expand_object.logger.setLevel('ERROR')
        self.example_file_dir = Path(__file__).resolve().parent / 'example_files'

    def test_full_good_file_is_verified(self):
        self.expand_object.run(
            file_location=str(self.example_file_dir / 'RefBldgMediumOfficeNew2004_Chicago_epJSON.epJSON')
        )
        self.assertTrue(self.expand_object.epjson_handler.epjson_is_valid)
