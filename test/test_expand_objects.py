import os
import unittest as ut
from unittest import skip

from expand_objects import ExpandObjects


class TestExpandObject(ut.TestCase):
    def setUp(self):
        self.logger_name = 'console_logger'
        self.expand_object = ExpandObjects(logger_name=self.logger_name)
        self.expand_object.logger.setLevel('ERROR')
        return

    def tearDown(self):
        return

    @skip
    def test_full_good_file_is_verified(self):
        self.expand_object.run(
            file_location=os.path.join(
                os.environ.get('ENERGYPLUS_EXPANDOBJECTS_ROOT_DIR'),
                'test',
                'example_files',
                'RefBldgMediumOfficeNew2004_Chicago_epJSON.epJSON'
            )
        )
        self.assertTrue(self.expand_object.epjson_handler.epjson_is_valid)
        return

    def test_one(self):
        pass


if __name__ == "__main__":
    ut.main()
