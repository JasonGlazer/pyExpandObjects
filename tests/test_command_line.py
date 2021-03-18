import unittest
import subprocess
import os
import re
from argparse import Namespace

from . import BaseTest
from src.main import main

this_script_path = os.path.dirname(
    os.path.abspath(__file__)
)


class TestMain(BaseTest, unittest.TestCase):

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
        return

    def test_output_message_contains_class_keys(self):
        output = {}
        exception_raised = False
        try:
            output = main(
                Namespace(
                    no_schema=True,
                    file=os.path.join(
                        this_script_path, '..', 'simulation', 'ExampleFiles', 'HVACTemplate-5ZoneVAVWaterCooledExpanded.epJSON')
                )
            )
        except Exception as e:
            print(e)
            print('test')
            self.assertEqual(e, e)
            exception_raised = True
        self.assertFalse(exception_raised)
        self.assertIn('outputPreProcessorMessage', output.keys())
        msg_rgx = re.match('.*##### HVACTemplate #####.*', output['outputPreProcessorMessage'].replace('\n', ' '))
        msg_status = False
        if msg_rgx:
            msg_status = True
        self.assertTrue(msg_status)
        return

    def test_bad_file_path_returns_message(self):
        output = main(
            Namespace(
                no_schema=True,
                file='bad_path.epJSON'
            )
        )
        msg_rgx = re.match('.*File does not exist.*', output['outputPreProcessorMessage'].replace('\n', ' '))
        msg_status = False
        if msg_rgx:
            msg_status = True
        self.assertTrue(msg_status)
        return

    def test_bad_file_extension_returns_message(self):
        output = main(
            Namespace(
                no_schema=True,
                file='bad_extension.epJSON_bad'
            )
        )
        msg_rgx = re.match('.*Bad file extension.*', output['outputPreProcessorMessage'].replace('\n', ' '))
        msg_status = False
        if msg_rgx:
            msg_status = True
        self.assertTrue(msg_status)
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
