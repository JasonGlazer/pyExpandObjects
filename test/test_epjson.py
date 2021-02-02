import unittest as ut
import jsonschema, os

from expand_objects.epjson_handler import EPJSON

minimum_objects_d = {
    "Building": {
        "Ref Bldg Medium Office New2004_v1.3_5.0": {
            "loads_convergence_tolerance_value": 0.04,
            "maximum_number_of_warmup_days": 25,
            "minimum_number_of_warmup_days": 6,
            "north_axis": 0.0,
            "solar_distribution": "FullInteriorAndExterior",
            "temperature_convergence_tolerance_value": 0.2,
            "terrain": "City"
        }
    },
    "GlobalGeometryRules": {
        "GlobalGeometryRules 1": {
            "coordinate_system": "Relative",
            "daylighting_reference_point_coordinate_system": "Relative",
            "starting_vertex_position": "UpperLeftCorner",
            "vertex_entry_direction": "Counterclockwise"

        }
    }
}

class TestEPJSONHandler(ut.TestCase):
    def setUp(self):
        self.logger_name = 'console_logger'
        self.epjson_handler = EPJSON(logger_name = self.logger_name)
        self.epjson_handler.logger.setLevel('ERROR')
        return

    def tearDown(self):
        return

    def test_default_schema_is_valid(self):
        self.epjson_handler.load_schema()
        assert self.epjson_handler.schema_is_valid == True
        return

    def test_blank_schema_is_not_valid(self):
        bad_return_value = self.epjson_handler._validate_schema({"properties" : {"id" : "asdf"}})
        self.assertFalse(bad_return_value)
        return

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
        return

    def test_good_file_is_verified(self):
        self.epjson_handler.load_schema()
        self.epjson_handler.load_epjson(
            os.path.join(
                os.environ.get('ENERGYPLUS_EXPANDOBJECTS_ROOT_DIR'),
                'test',
                'example_files',
                'RefBldgMediumOfficeNew2004_Chicago_epJSON.epJSON'
            )
        )
        self.assertTrue(self.epjson_handler.epjson_is_valid)
        return

#make load_schema() and/or validate_schema() accept string and file implementations?
#tests
# - bad file path gives meaningful error
# - good file outputs success

if __name__ == "__main__":
    ut.main()
