import unittest
import json
from pathlib import Path
import subprocess
import sys
import os

from expand_objects import ExpandThermostat
from epjson_handler import EPJSON
import custom_exceptions as eoe
from . import BaseTest

this_script_dir = Path(__file__).parent


class TestExpandThermostats(BaseTest, unittest.TestCase):
    def setUp(self):
        return

    def teardown(self):
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Thermostat:Input Template Required")
    def test_check_templates_are_required(self):
        with self.assertRaises(TypeError):
            ExpandThermostat()
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Thermostat:Verify valid template object")
    def test_verify_good_template(self):
        template = {
            "All Zones": {
                "heating_setpoint_schedule_name": "Htg-SetP-Sch",
                "cooling_setpoint_schedule_name": "Clg-SetP-Sch"
            }
        }
        output = ExpandThermostat(template=template)
        self.assertEqual('All Zones', list(output.template.keys())[0])
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Thermostat:Reject bad template object")
    def test_reject_bad_template(self):
        templates = {}
        with self.assertRaises(eoe.InvalidTemplateException):
            ExpandThermostat(template=templates)
        templates = []
        with self.assertRaises(TypeError):
            ExpandThermostat(template=templates)
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Thermostat:Create schedule from constant setpoint")
    def test_create_thermostat_schedule_from_constant_setpoint(self):
        thermostat_template = {
            'Thermostat 1': {
                'constant_cooling_setpoint': 18,
                'constant_heating_setpoint': 12
            }
        }
        eo = ExpandThermostat(template=thermostat_template)
        eo.create_and_set_schedules()
        schedule_name_match = False
        schedule_names = [i for i in list(eo.epjson['Schedule:Compact'].keys())]
        schedule_match = [i for i in schedule_names if i == 'HVACTemplate-Always12']
        if any(schedule_match):
            schedule_name_match = True
        self.assertTrue(schedule_name_match)
        self.assertEqual(len(schedule_names), 2)
        self.assertEqual(
            eo.epjson['Schedule:Compact']['HVACTemplate-Always12']['data'][-1]['field'],
            12)
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Thermostat:Assign schedule from constant setpoint")
    def test_assign_thermostat_schedule_from_constant_setpoint(self):
        thermostat_template = {
            'Thermostat 1': {
                'constant_heating_setpoint': 12
            }
        }
        eo = ExpandThermostat(template=thermostat_template)
        eo.create_and_set_schedules()
        self.assertEqual('HVACTemplate-Always12', eo.heating_setpoint_schedule_name)
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Thermostat:Reject empty template")
    def test_reject_no_inputs(self):
        thermostat_template = {'Thermostat 1': {}}
        eo = ExpandThermostat(template=thermostat_template)
        eo.create_and_set_schedules()
        with self.assertRaises(eoe.InvalidTemplateException):
            eo.create_thermostat_setpoints()
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Thermostat:Options:DualSetpoint from setpoints")
    def test_create_dual_thermostat_from_setpoints(self):
        thermostat_template = {
            'Thermostat 1': {
                'constant_cooling_setpoint': 18,
                'constant_heating_setpoint': 12
            }
        }
        eo = ExpandThermostat(template=thermostat_template)
        eo.create_and_set_schedules()
        eo.create_thermostat_setpoints()
        self.assertEqual(
            eo.epjson['ThermostatSetpoint:DualSetpoint']['Thermostat 1 SP Control']
            ['cooling_setpoint_temperature_schedule_name'],
            'HVACTemplate-Always18')
        self.assertEqual(
            eo.epjson['ThermostatSetpoint:DualSetpoint']['Thermostat 1 SP Control']
            ['heating_setpoint_temperature_schedule_name'],
            'HVACTemplate-Always12')
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Thermostat:Options:DualSetpoint from schedules")
    def test_create_dual_thermostat_from_schedules(self):
        thermostat_template = {
            'Thermostat 1': {
                'cooling_setpoint_schedule_name': 'HVACTemplate-Always18',
                'heating_setpoint_schedule_name': 'HVACTemplate-Always12'
            }
        }
        eo = ExpandThermostat(template=thermostat_template)
        eo.create_and_set_schedules()
        eo.create_thermostat_setpoints()
        self.assertEqual(
            eo.epjson['ThermostatSetpoint:DualSetpoint']['Thermostat 1 SP Control']
            ['cooling_setpoint_temperature_schedule_name'],
            'HVACTemplate-Always18')
        self.assertEqual(
            eo.epjson['ThermostatSetpoint:DualSetpoint']['Thermostat 1 SP Control']
            ['heating_setpoint_temperature_schedule_name'],
            'HVACTemplate-Always12')
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Thermostat:Options:SingleHeating from setpoint")
    def test_create_thermostat_single_heating_from_setpoint(self):
        thermostat_template = {
            'Thermostat 1': {
                'constant_heating_setpoint': 12
            }
        }
        eo = ExpandThermostat(template=thermostat_template)
        eo.create_and_set_schedules()
        eo.create_thermostat_setpoints()
        self.assertEqual(
            eo.epjson['ThermostatSetpoint:SingleHeating']['Thermostat 1 SP Control']
            ['setpoint_temperature_schedule_name'],
            'HVACTemplate-Always12')
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Thermostat:Options:SingleHeating from schedule")
    def test_create_thermostat_single_heating_from_schedule(self):
        thermostat_template = {
            'Thermostat 1': {
                'heating_setpoint_schedule_name': 'HVACTemplate-Always12'
            }
        }
        eo = ExpandThermostat(template=thermostat_template)
        eo.create_and_set_schedules()
        eo.create_thermostat_setpoints()
        self.assertEqual(
            eo.epjson['ThermostatSetpoint:SingleHeating']['Thermostat 1 SP Control']
            ['setpoint_temperature_schedule_name'],
            'HVACTemplate-Always12')
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Thermostat:Options:SingleCooling from setpoint")
    def test_create_thermostat_single_cooling_from_setpoint(self):
        thermostat_template = {
            'Thermostat 1': {
                'constant_cooling_setpoint': 18
            }
        }
        eo = ExpandThermostat(template=thermostat_template)
        eo.create_and_set_schedules()
        eo.create_thermostat_setpoints()
        self.assertEqual(
            eo.epjson['ThermostatSetpoint:SingleCooling']['Thermostat 1 SP Control']
            ['setpoint_temperature_schedule_name'],
            'HVACTemplate-Always18')
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Thermostat:Options:SingleCooling from schedule")
    def test_create_thermostat_single_cooling_from_schedule(self):
        thermostat_template = {
            'Thermostat 1': {
                'cooling_setpoint_schedule_name': 'HVACTemplate-Always18'
            }
        }
        eo = ExpandThermostat(template=thermostat_template)
        eo.create_and_set_schedules()
        eo.create_thermostat_setpoints()
        self.assertEqual(
            eo.epjson['ThermostatSetpoint:SingleCooling']['Thermostat 1 SP Control']
            ['setpoint_temperature_schedule_name'],
            'HVACTemplate-Always18')
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Thermostat:Processing test")
    def test_processing(self):
        thermostat_template = {
            'Thermostat 1': {
                'cooling_setpoint_schedule_name': 'HVACTemplate-Always18',
                'heating_setpoint_schedule_name': 'HVACTemplate-Always12'
            }
        }
        eo = ExpandThermostat(template=thermostat_template)
        eo.run()
        self.assertEqual(
            eo.epjson['ThermostatSetpoint:DualSetpoint']['Thermostat 1 SP Control']
            ['cooling_setpoint_temperature_schedule_name'],
            'HVACTemplate-Always18')
        self.assertEqual(
            eo.epjson['ThermostatSetpoint:DualSetpoint']['Thermostat 1 SP Control']
            ['heating_setpoint_temperature_schedule_name'],
            'HVACTemplate-Always12')
        return

    # todo_eo test summary data

    # todo_eo may need to run this under different file (sim_test_*) so it's skipped by CI
    # this is likely a function that can be pushed up to base class
    # def test_simulation(self):
    #     base_file_path = str(this_script_dir / 'simulation' / 'ExampleFiles' /
    #                          'HVACTemplate-5ZonePurchAir.epJSON')
    #     with open(str(this_script_dir / 'simulation' / 'ExampleFiles' /
    #                   'HVACTemplate-5ZonePurchAir.epJSON'), 'r') as f:
    #         test_data = f.read()
    #     base_raw_epjson = json.loads(test_data)
    #     test_template = base_raw_epjson.pop('HVACTemplate:Thermostat')
    #     epj = EPJSON()
    #     epj.load_epjson(epjson_ref=base_raw_epjson)
    #     base_epjson = epj.input_epjson
    #     print(test_template)
    #     eo = ExpandThermostat(template=test_template)
    #     eo.run()
    #     print(eo.epjson)
    #     test_epjson = epj.merge_epjson(
    #         super_dictionary=base_epjson,
    #         object_dictionary=eo.epjson,
    #         unique_name_override=False
    #     )
    #     subprocess.run(
    #         [
    #             'wine',
    #             str(this_script_dir / 'simulation' / 'energyplus.exe'),
    #             '-d',
    #             str(this_script_dir / 'simulation' / 'test'),
    #             '-w',
    #             str(this_script_dir / 'simulation' / 'WeatherData' / 'USA_CO_Golden-NREL.724666_TMY3.epw'),
    #             base_file_path
    #          ]
    #     )
    #     # get output
    #     # run again with test_file
    #     # compare mtr files
    #     # compare err files for :
    #     # ************* EnergyPlus Completed Successfully--
    #     7 Warning; 0 Severe Errors; Elapsed Time=00hr 00min  1.32sec
    #     # import os
    #     # with open(os.path.join(os.path.dirname(__file__), 'epjson_test.epJSON'), 'w') as f:
    #     #     json.dump(test_epjson, f, indent=4, sort_keys=True)
    #     return
