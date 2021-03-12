import unittest
import subprocess
import os
from argparse import Namespace

from expand_objects.main import main
from test import BaseTest

this_script_path = os.path.dirname(
    os.path.abspath(__file__)
)


class TestHVACTemplateObject(BaseTest, unittest.TestCase):
    @BaseTest._test_logger(doc_text="Core:No schema flag works")
    def test_no_schema_main(self):
        output = {}
        exception_raised = False
        try:
            output = main(
                Namespace(
                    no_schema=True,
                    file=os.path.join(this_script_path, 'resources', 'HVACTemplate-5ZonePurchAir.epJSON')
                )
            )
        except Exception as e:
            self.assertEqual(e, e)
            exception_raised = True
        self.assertFalse(exception_raised)
        self.assertIn('outputPreProcessorMessage', output.keys())
        self.assertFalse(output['outputPreProcessorMessage'])
        return

    @BaseTest._test_logger(doc_text="Core:Bad file paths are rejected")
    def test_bad_file_path_returns_message(self):
        output = main(
            Namespace(
                no_schema=True,
                file='bad_path.epJSON'
            )
        )
        self.assertIn('File does not exist', output['outputPreProcessorMessage'][0])
        return

    @BaseTest._test_logger(doc_text="Core:Bad file extensions are rejected")
    def test_bad_file_extension_returns_message(self):
        output_epjson = main(
            Namespace(
                no_schema=True,
                file='bad_extension.epJSON_bad'
            )
        )
        self.assertIn('Bad file extension', output_epjson['outputPreProcessorMessage'][0])
        return

    @unittest.skip
    def test_no_schema_command_line_args(self):
        sub_process = subprocess.Popen(
            [
                'python',
                os.path.join(this_script_path, '..', 'expand_objects', 'main.py'),
                '-ns',
                os.path.join(this_script_path, 'resources', 'HVACTemplate-5ZonePurchAir.epJSON')
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
