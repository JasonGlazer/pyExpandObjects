from pathlib import Path
import unittest

from expand_objects.epjson_handler import EPJSON

minimum_objects_d = {
    "Building": {
        "Test Building": {}
    },
    "GlobalGeometryRules": {
        "GlobalGeometryRules 1": {
            "coordinate_system": "Relative",
            "starting_vertex_position": "UpperLeftCorner",
            "vertex_entry_direction": "Counterclockwise"

        }
    }
}


class TestEPJSONHandler(unittest.TestCase):
    def setUp(self):
        self.epjson_handler = EPJSON()
        self.epjson_handler.logger.setLevel('ERROR')
        self.example_file_dir = Path(__file__).resolve().parent / 'example_files'

    def test_default_schema_is_valid(self):
        self.epjson_handler.load_schema()
        assert self.epjson_handler.schema_is_valid

    def test_blank_schema_is_not_valid(self):
        bad_return_value = self.epjson_handler._validate_schema({"properties": {"id": "asdf"}})
        self.assertFalse(bad_return_value)

    def test_good_object_is_valid(self):
        self.epjson_handler.load_schema()
        self.epjson_handler.load_epjson({
            **minimum_objects_d,
            "Version": {
                "Version 1": {
                    "version_identifier": "9.4"
                }
            }
        })
        self.assertTrue(self.epjson_handler.epjson_is_valid)

    def test_good_file_is_verified(self):
        self.epjson_handler.load_schema()
        self.epjson_handler.load_epjson(str(self.example_file_dir / 'RefBldgMediumOfficeNew2004_Chicago_epJSON.epJSON'))
        self.assertTrue(self.epjson_handler.epjson_is_valid)


# make load_schema() and/or validate_schema() accept string and file implementations?
# tests
# - bad file path gives meaningful error
# - good file outputs success
