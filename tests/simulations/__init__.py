import json
import copy
from pathlib import Path
import subprocess
import csv
import re
import sys
import os

from src.epjson_handler import EPJSON

test_dir = Path(__file__).parent.parent


class BaseSimulationTest(object):
    """
    Setup, extraction, and comparison functions for simulation testing.
    """

    @staticmethod
    def setup_file(file_path):
        """
        Format epJSON file to have correct outputs for testing
        :param file_path: epJSON file path
        :return: formatted epJSON
        """
        with open(file_path, 'r') as f:
            test_data = f.read()
        base_raw_epjson = json.loads(test_data)
        epj = EPJSON()
        epj.epjson_process(epjson_ref=base_raw_epjson)
        # Edit base epjson, make input epjson, write to test folder, and run
        purged_epjson = epj.purge_epjson(
            epjson=base_raw_epjson,
            purge_dictionary={
                'Output:Table:SummaryReports': '.*',
                'OutputControl:Table:Style': '.*'
            })
        formatted_epjson = copy.deepcopy(purged_epjson)
        epj.merge_epjson(
            super_dictionary=formatted_epjson,
            object_dictionary={
                "Output:Table:SummaryReports": {
                    "report 1": {
                        "reports": [
                            {"report_name": "EndUseEnergyConsumptionElectricityMonthly"}
                        ]
                    }
                },
                "OutputControl:Table:Style": {
                    "Style 1": {
                        "column_separator": "Comma"
                    }
                }
            }
        )
        return formatted_epjson

    @staticmethod
    def write_file_for_testing(epjson, file_name, sub_directory=('simulation', 'test')):
        """
        write file to simulation testing sudirectory
        :param epjson: epJSON dictionary
        :param sub_directory: project subdirectory
        :param file_name: file name to write
        :return: file_path for written epJSON
        """
        input_file_path = test_dir.joinpath('..', *sub_directory, file_name)
        with open(input_file_path, 'w') as f:
            json.dump(epjson, f, indent=4, sort_keys=True)
        return input_file_path

    @staticmethod
    def perform_comparison(epjson_files):
        """
        Simulate and compare epJSON files
        :param epjson_files: input epJSON files to compare
        :return: dictionary of status outputs
        """
        total_energy_outputs = []
        warning_outputs = []
        error_outputs = []
        finished_statuses = []
        for file_path in epjson_files:
            # move files from previous runs, rm is too dangerous
            try:
                os.rename(
                    str(test_dir / '..' / 'simulation' / 'test' / 'eplustbl.csv'),
                    str(test_dir / '..' / 'simulation' / 'test' / 'eplustbl_previous.csv')
                )
            except:
                pass
            try:
                os.rename(
                    str(test_dir / '..' / 'simulation' / 'test' / 'eplusout.err'),
                    str(test_dir / '..' / 'simulation' / 'test' / 'eplusout_previous.err')
                )
            except:
                pass
            try:
                os.rename(
                    str(test_dir / '..' / 'simulation' / 'test' / 'eplusout.end'),
                    str(test_dir / '..' / 'simulation' / 'test' / 'eplusout_previous.end')
                )
            except:
                pass
            if sys.platform.startswith('win'):
                subprocess.run(
                    [
                        str(test_dir / '..' / 'simulation' / 'energyplus.exe'),
                        '-d',
                        str(test_dir / '..' / 'simulation' / 'test'),
                        '-w',
                        str(test_dir / '..' / 'simulation' / 'WeatherData' / 'USA_CO_Golden-NREL.724666_TMY3.epw'),
                        str(file_path)
                    ]
                )
            else:
                subprocess.run(
                    [
                        'wine',
                        str(test_dir / '..' / 'simulation' / 'energyplus.exe'),
                        '-d',
                        str(test_dir / '..' / 'simulation' / 'test'),
                        '-w',
                        str(test_dir / '..' / 'simulation' / 'WeatherData' / 'USA_CO_Golden-NREL.724666_TMY3.epw'),
                        file_path
                    ]
                )
            total_energy = 0
            # get sum of total row to use as comparison
            with open(str(test_dir / '..' / 'simulation' / 'test' / 'eplustbl.csv'), 'r') as f:
                csvreader = csv.reader(f)
                for row in csvreader:
                    if 'Annual Sum or Average' in row:
                        for val in row:
                            try:
                                total_energy += float(val)
                            except ValueError:
                                pass
            with open(str(test_dir / '..' / 'simulation' / 'test' / 'eplusout.end'), 'r') as f:
                lines = f.readlines()
            # check end file for matches and success message
            warning_rgx = r'(\d+)\s+Warning;'
            error_rgx = r'(\d+) Severe Errors'
            status_rgx = r'^EnergyPlus\s+Completed\s+Successfully'
            status_val = 0
            for line in lines:
                warning_match = re.match(warning_rgx, line)
                error_match = re.match(error_rgx, line)
                status_match = re.match(status_rgx, line)
                if warning_match:
                    try:
                        warning_outputs.append(float(warning_match.group(1)))
                    except TypeError:
                        # special flag for type error
                        warning_outputs.append(-1)
                if error_match:
                    try:
                        error_outputs.append(float(error_match.group(1)))
                    except TypeError:
                        error_outputs.append(-1)
                if status_match:
                    status_val = 1
            finished_statuses.append(status_val)
            total_energy_outputs.append(total_energy)
        return {
            "total_energy_outputs": total_energy_outputs,
            "warning_outputs": warning_outputs,
            "error_outputs": error_outputs,
            "finished_statuses": finished_statuses
        }

    @staticmethod
    def compare_epjsons(epjson_1, epjson_2):
        """
        Summarize and compare two epJSONs based on object counts.

        :param epjson_1: epJSON object
        :param epjson_2: epJSON object
        :return: message if failures occur, otherwise None
        """
        eo = EPJSON()
        epjson_summary_1 = eo.summarize_epjson(epjson_1)
        epjson_summary_2 = eo.summarize_epjson(epjson_2)
        # remove schedule compact
        epjson_summary_1.pop('Schedule:Compact')
        epjson_summary_2.pop('Schedule:Compact')
        msg = ''
        for k, v in epjson_summary_1.items():
            if k not in epjson_summary_2.keys():
                msg += '{} not in {}\n'.format(k, epjson_summary_2)
            else:
                if epjson_summary_1[k] != epjson_summary_2[k]:
                    msg += '{} is not the same number of objects\n'.format(k)
        for k, v in epjson_summary_2.items():
            if k not in epjson_summary_1.keys():
                msg += '{} not in {}\n'.format(k, epjson_summary_2)
        if msg == '':
            return None
        else:
            return msg
