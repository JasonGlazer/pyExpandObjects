import unittest
import subprocess
import os
import sys
from argparse import Namespace

from expand_objects.main import main

this_script_path = os.path.dirname(
    os.path.abspath(__file__)
)


class TestHVACTemplateObject(unittest.TestCase):

    def test_no_schema_main(self):
        exception_raised = False
        try:
            output_epjson = main(
                Namespace(
                    no_schema=True,
                    files=[os.path.join(this_script_path, 'example_files', 'HVACTemplate-5ZonePurchAir.epJSON')]
                )
            )
        except Exception as e:
            exception_raised = e
            exception_raised = True
        self.assertFalse(exception_raised)
        # Make more detailed test when output is constructed.
        print(output_epjson)
        return

    def test_bad_file_path_returns_none(self):
        output_epjson = main(
            Namespace(
                no_schema=True,
                files=['bad_path.epJSON', ]
            )
        )
        self.assertIsNone(output_epjson)
        return

    def test_bad_file_extension_returns_none(self):
        output_epjson = main(
            Namespace(
                no_schema=True,
                files=['bad_extension.epJSON_bad', ]
            )
        )
        self.assertIsNone(output_epjson)
        return

    @unittest.skip
    def test_no_schema_command_line_args(self):
        sub_process = subprocess.Popen(
            [
                'python',
                os.path.join(this_script_path, '..', 'expand_objects', 'main.py'),
                '-ns',
                os.path.join(this_script_path, 'example_files', 'RefBldgMediumOfficeNew2004_Chicago_epJSON.epJSON2')
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        process_error, _ = sub_process.communicate()
        print(process_error)
        print(sub_process.returncode)
        # make additional tests when console output is generated
        self.assertEqual(sub_process.returncode, 0)
        return
