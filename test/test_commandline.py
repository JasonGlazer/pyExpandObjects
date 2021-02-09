import unittest
import subprocess
import os

this_script_path = os.path.dirname(
    os.path.abspath(__file__)
)


class TestHVACTemplateObject(unittest.TestCase):

    def test_no_schema_command_line_args(self):
        sub_process = subprocess.Popen(
            [
                'python',
                os.path.join(this_script_path, '..', 'expand_objects', 'main.py'),
                '-ns',
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        process_error, _ = sub_process.communicate()
        print(process_error)
        # make additional tests when console output is generated
        self.assertEqual(sub_process.returncode, 0)
        return
