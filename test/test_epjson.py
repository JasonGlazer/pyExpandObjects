import unittest as ut
import unittest.mock
import jsonschema

from expand_objects.epjson_handler import EPJSON

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


#make load_schema() and/or validate_schema() accept string and file implementations?
if __name__ == "__main__":
    ut.main()
