import unittest
from pathlib import Path
import subprocess
import tempfile

from tests import BaseTest
from tests.simulations import BaseSimulationTest

test_dir = Path(__file__).parent.parent


class TestSimulationSimple(BaseTest, BaseSimulationTest, unittest.TestCase):
    def setUp(self):
        return

    def teardown(self):
        return

    def test_no_schema_command_line_args(self):
        with tempfile.TemporaryDirectory() as output_directory:
            sub_process = subprocess.Popen(
                [
                    'python',
                    str(test_dir / '..' / 'src' / 'main.py'),
                    '-ns',
                    str(test_dir / '..' / 'simulation' / 'ExampleFiles' /
                        'HVACTemplate-5ZoneVAVWaterCooled.epJSON'),
                    '-o',
                    output_directory
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
        process_msg, _ = sub_process.communicate()
        # check console output for errors
        self.assertNotIn('ERROR', str(process_msg))
        return
