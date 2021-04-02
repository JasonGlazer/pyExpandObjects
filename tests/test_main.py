import unittest
from pathlib import Path
import re
from argparse import Namespace

from . import BaseTest
from src.main import main

test_dir = Path(__file__).parent


class TestMain(BaseTest, unittest.TestCase):
    def test_no_schema_main(self):
        output = {}
        exception_raised = False
        try:
            output = main(
                Namespace(
                    no_schema=True,
                    file=str(test_dir / '..' / 'simulation' / 'ExampleFiles' / 'HVACTemplate-5ZoneVAVWaterCooled.epJSON')
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
                    file=str(test_dir / '..' / 'simulation' / 'ExampleFiles' / 'HVACTemplate-5ZoneVAVWaterCooled.epJSON')
                )
            )
        except Exception as e:
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
