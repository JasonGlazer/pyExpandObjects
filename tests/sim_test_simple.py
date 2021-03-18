import unittest
import json
import subprocess
from pathlib import Path
import sys
import os

from . import BaseTest
from src.epjson_handler import EPJSON
from src.expand_objects import ExpandThermostat

this_script_dir = Path(__file__).parent


class TestSimulationSimple(BaseTest, unittest.TestCase):
    def setUp(self):
        return

    def teardown(self):
        return

    # todo_eo: much of this function needs to be refactored and set up for reuse in subsequent tests
    @unittest.skip
    def test_simulation(self):
        base_file_path = str(this_script_dir / '..' / 'simulation' / 'ExampleFiles' /
                             'HVACTemplate-5ZoneVAVWaterCooled.epJSON')
        with open(base_file_path, 'r') as f:
            test_data = f.read()
        base_raw_epjson = json.loads(test_data)
        test_template = base_raw_epjson.pop('HVACTemplate:Thermostat')
        epj = EPJSON()
        epj.load_epjson(epjson_ref=base_raw_epjson)
        base_epjson = epj.input_epjson
        print(test_template)
        eo = ExpandThermostat(template=test_template)
        eo.run()
        print(eo.epjson)
        test_epjson = epj.merge_epjson(
            super_dictionary=base_epjson,
            object_dictionary=eo.epjson,
            unique_name_override=False
        )
        subprocess.run(
            [
                'wine',
                str(this_script_dir / '..' / 'simulation' / 'energyplus.exe'),
                '-d',
                str(this_script_dir / '..' / 'simulation' / 'test'),
                '-w',
                str(this_script_dir / '..' / 'simulation' / 'WeatherData' / 'USA_CO_Golden-NREL.724666_TMY3.epw'),
                base_file_path
             ]
        )
        # set output in file like this
        # "Output:Table:SummaryReports": {
        #     "report 1" : {
        #         "reports": [
        #             {"report_name": "EndUseEnergyConsumptionElectricityMonthly"}
        #         ]
        #     }
        # },
        # "OutputControl:Table:Style": {
        #     "Style 1": {
        #         "column_separator": "Comma"
        #     }
        # },
        # get output
        import csv
        total_energy_base = 0
        with open(str(this_script_dir / '..' / 'simulation' / 'test' / 'eplustbl.csv'), 'r') as f:
            csvreader = csv.reader(f)
            for row in csvreader:
                if 'Annual Sum or Average' in row:
                    for val in row:
                        try:
                            total_energy_base += float(val)
                        except ValueError:
                            pass
        print(total_energy_base)
        # run again with test_file
        # compare err files for :
        # ************* EnergyPlus Completed Successfully--
        # 7 Warning; 0 Severe Errors; Elapsed Time=00hr 00min  1.32sec
        # import os
        # with open(os.path.join(os.path.dirname(__file__), 'epjson_test.epJSON'), 'w') as f:
        #     json.dump(test_epjson, f, indent=4, sort_keys=True)
        return