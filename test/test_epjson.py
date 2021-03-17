from pathlib import Path
import unittest

from expand_objects.epjson_handler import EPJSON
import expand_objects.exceptions as eoe


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
        self.epjson_handler_no_schema = EPJSON()
        self.epjson_handler.logger.setLevel('ERROR')
        self.example_file_dir = Path(__file__).resolve().parent / 'resources'

    def test_merge_same_object_type(self):
        dict_1 = {
            "Zone": {
                "SPACE1-1": {
                    "ceiling_height": 2.438400269,
                    "direction_of_relative_north": 0,
                    "multiplier": 1,
                    "type": 1,
                    "volume": 103.311355591,
                    "x_origin": 0,
                    "y_origin": 0,
                    "z_origin": 0
                }
            }
        }
        dict_2 = {
            "Zone": {
                "SPACE2-1": {
                    "ceiling_height": 2.438400269,
                    "direction_of_relative_north": 0,
                    "multiplier": 1,
                    "type": 1,
                    "volume": 239.247360229,
                    "x_origin": 0,
                    "y_origin": 0,
                    "z_origin": 0
                }
            }
        }
        dict_3 = self.epjson_handler.merge_epjson(
            super_dictionary=dict_1,
            object_dictionary=dict_2,
        )
        self.assertIn('SPACE1-1', dict_3['Zone'].keys())
        self.assertIn('SPACE2-1', dict_3['Zone'].keys())
        return

    def test_merge_two_objects(self):
        dict_1 = {
            "Zone": {
                "SPACE1-1": {
                    "ceiling_height": 2.438400269,
                    "direction_of_relative_north": 0,
                    "multiplier": 1,
                    "type": 1,
                    "volume": 103.311355591,
                    "x_origin": 0,
                    "y_origin": 0,
                    "z_origin": 0
                }
            }
        }
        dict_2 = {
            "ZoneInfiltration:DesignFlowRate": {
                "SPACE1-1 Infil 1": {
                    "constant_term_coefficient": 0,
                    "design_flow_rate": 0.0167,
                    "design_flow_rate_calculation_method": "Flow/Zone",
                    "schedule_name": "INFIL-SCH",
                    "temperature_term_coefficient": 0,
                    "velocity_squared_term_coefficient": 0,
                    "velocity_term_coefficient": 0.2237,
                    "zone_or_zonelist_name": "SPACE1-1"
                }
            }
        }
        dict_3 = self.epjson_handler.merge_epjson(
            super_dictionary=dict_1,
            object_dictionary=dict_2,
        )
        self.assertIn('Zone', dict_3.keys())
        self.assertGreater(len(dict_3['Zone']['SPACE1-1'].keys()), 0)
        self.assertIn('ZoneInfiltration:DesignFlowRate', dict_3.keys())
        self.assertGreater(len(dict_3['ZoneInfiltration:DesignFlowRate']['SPACE1-1 Infil 1'].keys()), 0)
        return

    def test_merge_fail_duplicate_name(self):
        dict_1 = {
            "Zone": {
                "SPACE1-1": {
                    "ceiling_height": 2.438400269,
                    "direction_of_relative_north": 0,
                    "multiplier": 1,
                    "type": 1,
                    "volume": 103.311355591,
                    "x_origin": 0,
                    "y_origin": 0,
                    "z_origin": 0
                }
            }
        }
        dict_2 = {
            "Zone": {
                "SPACE1-1": {
                    "ceiling_height": 2.438400269,
                    "direction_of_relative_north": 0,
                    "multiplier": 1,
                    "type": 1,
                    "volume": 103.311355591,
                    "x_origin": 0,
                    "y_origin": 0,
                    "z_origin": 0
                }
            }
        }
        with self.assertRaisesRegex(eoe.UniqueNameException, '.*SPACE1-1.*Zone'):
            self.epjson_handler.merge_epjson(
                super_dictionary=dict_1,
                object_dictionary=dict_2,
                unique_name_override=False
            )
        return

    def test_unpack_epjson(self):
        outputs = self.epjson_handler.unpack_epjson({
            "Zone": {
                "SPACE1-1": {
                    "ceiling_height": 2.438400269,
                    "direction_of_relative_north": 0,
                    "multiplier": 1,
                    "type": 1,
                    "volume": 103.311355591,
                    "x_origin": 0,
                    "y_origin": 0,
                    "z_origin": 0
                },
                "SPACE2-1": {
                    "ceiling_height": 2.438400269,
                    "direction_of_relative_north": 0,
                    "multiplier": 1,
                    "type": 1,
                    "volume": 103.311355591,
                    "x_origin": 0,
                    "y_origin": 0,
                    "z_origin": 0
                }
            }
        })
        key_check = True
        for output in outputs:
            (name, _), = output.items()
            if name not in ['SPACE1-1', 'SPACE2-1']:
                key_check = False
        self.assertTrue(key_check)
        return

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
        self.assertTrue(self.epjson_handler.input_epjson_is_valid)

    def test_good_file_is_verified(self):
        self.epjson_handler.load_schema()
        self.epjson_handler.load_epjson(str(self.example_file_dir / 'RefBldgMediumOfficeNew2004_Chicago_epJSON.epJSON'))
        self.assertTrue(self.epjson_handler.input_epjson_is_valid)

    def test_no_schema_returns_json(self):
        self.epjson_handler_no_schema.load_epjson({
            **minimum_objects_d,
            "Version": {
                "Version 1": {
                    "version_identifier": "9.4"
                }
            }
        })
        self.assertIsNone(self.epjson_handler_no_schema.schema)
        self.assertIsNone(self.epjson_handler_no_schema.schema_is_valid)
        self.assertIsNone(self.epjson_handler_no_schema.input_epjson_is_valid)
        self.assertEqual(len(self.epjson_handler_no_schema.input_epjson.keys()), 3)
        return

    # todo_eo: need to provide path for user provided schema location
