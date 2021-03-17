import unittest
import os
import sys

this_script_path = os.path.dirname(
    os.path.abspath(__file__)
)

sys.path.append(os.path.join(this_script_path, '..', 'src'))

from hvac_template import HVACTemplate
from . import BaseTest

minimum_objects_d = {
    "Building": {
        "Test Building": {}
    },
    "GlobalGeometryRules": {
        "GlobalGeometryRules 1": {
            "coordinate_system": "Relative",
            "starting_vertex_position": "UpperLeftCorner",
            "vertex_entry_direction": "Counterclockwise"
        }
    }
}


class TestHVACTemplateObject(BaseTest, unittest.TestCase):
    def setUp(self):
        self.hvac_template = HVACTemplate()
        self.hvac_template.logger.setLevel('INFO')
        self.hvac_template.load_schema()
        return

    def tearDown(self):
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Verify no input templates returns no class templates")
    def test_no_hvac_objects_returns_with_zero_templates(self):
        self.hvac_template.load_epjson({
            **minimum_objects_d,
            "Version": {
                "Version 1": {
                    "version_identifier": "9.4"
                }
            }
        })
        self.assertTrue(self.hvac_template.input_epjson_is_valid)
        self.assertEqual(0, len(self.hvac_template.templates))
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Verify non HVACTemplate objects are passed to base dictionary")
    def test_base_objects_are_stored(self):
        self.hvac_template.load_epjson({
            **minimum_objects_d,
            "HVACTemplate:Thermostat": {
                "All Zones": {
                    "heating_setpoint_schedule_name": "Htg-SetP-Sch",
                    "cooling_setpoint_schedule_name": "Clg-SetP-Sch"
                }
            }
        })
        self.hvac_template.hvac_template_process(self.hvac_template.input_epjson)
        self.assertTrue(self.hvac_template.input_epjson_is_valid)
        self.assertEqual(2, len(self.hvac_template.base_objects))
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Verify input templates returns class templates")
    def test_one_hvac_object_one_template_returns_true(self):
        self.hvac_template.load_epjson({
            **minimum_objects_d,
            "HVACTemplate:Thermostat": {
                "All Zones": {
                    "heating_setpoint_schedule_name": "Htg-SetP-Sch",
                    "cooling_setpoint_schedule_name": "Clg-SetP-Sch"
                }
            }
        })
        self.hvac_template.hvac_template_process(self.hvac_template.input_epjson)
        self.assertTrue(self.hvac_template.input_epjson_is_valid)
        self.assertEqual(len(self.hvac_template.templates.keys()), 1)
        self.assertIn(
            'HVACTemplate:Thermostat',
            self.hvac_template.templates.keys())
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Verify different templates returns "
                                    "correct class templates")
    def test_n_hvac_objects_n_templates_returns_true(self):
        self.hvac_template.load_epjson({
            **minimum_objects_d,
            "HVACTemplate:Thermostat": {
                "All Zones 1": {
                    "heating_setpoint_schedule_name": "Htg-SetP-Sch",
                    "cooling_setpoint_schedule_name": "Clg-SetP-Sch"
                },
                "All Zones 2": {
                    "heating_setpoint_schedule_name": "Htg-SetP-Sch",
                    "cooling_setpoint_schedule_name": "Clg-SetP-Sch"
                },
            },
            "HVACTemplate:Zone:IdealLoadsAirSystem": {
                "HVACTemplate:Zone:IdealLoadsAirSystem 1": {"zone_name": "Zone 1"},
                "HVACTemplate:Zone:IdealLoadsAirSystem 2": {"zone_name": "Zone 2"}
            }
        })
        self.hvac_template.hvac_template_process(self.hvac_template.input_epjson)
        self.assertTrue(self.hvac_template.input_epjson_is_valid)
        self.assertEqual(len(self.hvac_template.templates['HVACTemplate:Thermostat'].keys()), 2)
        self.assertEqual(len(self.hvac_template.templates['HVACTemplate:Zone:IdealLoadsAirSystem'].keys()), 2)
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:Verify fields are saved within templates")
    def test_templates_have_good_objects(self):
        self.hvac_template.load_epjson({
            **minimum_objects_d,
            "HVACTemplate:Thermostat": {
                "All Zones": {
                    "heating_setpoint_schedule_name": "Htg-SetP-Sch",
                    "cooling_setpoint_schedule_name": "Clg-SetP-Sch"
                },
                "All Zones 2": {
                    "heating_setpoint_schedule_name": "Htg-SetP-Sch",
                    "cooling_setpoint_schedule_name": "Clg-SetP-Sch"
                }
            }
        })
        self.hvac_template.hvac_template_process(self.hvac_template.input_epjson)
        self.assertTrue(self.hvac_template.input_epjson_is_valid)
        self.assertEqual(
            len(self.hvac_template.templates_thermostats['HVACTemplate:Thermostat'].keys()),
            2)
        return

    # todo_eo One test for each template type

    @BaseTest._test_logger(doc_text="HVACTemplate:Validate processing steps")
    def test_thermostat_processing(self):
        self.hvac_template.load_epjson({
            **minimum_objects_d,
            "HVACTemplate:Thermostat": {
                "All Zones": {
                    "heating_setpoint_schedule_name": "Htg-SetP-Sch",
                    "cooling_setpoint_schedule_name": "Clg-SetP-Sch"
                },
                "All Zones 2": {
                    "heating_setpoint_schedule_name": "Htg-SetP-Sch",
                    "cooling_setpoint_schedule_name": "Clg-SetP-Sch"
                }
            }
        })
        epjson = self.hvac_template.run(self.hvac_template.input_epjson)
        name_check = True
        object_check = True
        outputs = self.hvac_template.unpack_epjson(epjson['epJSON'])
        if len([i for i in outputs]) == 0:
            name_check = False
            object_check = False
        for output in outputs:
            (name, _), = output.items()
            if name not in ['All Zones SP Control', 'All Zones 2 SP Control',
                            'Test Building', 'GlobalGeometryRules 1']:
                name_check = False
        self.assertTrue(name_check)
        for object_type in epjson.keys():
            if object_type not in ['HVACTemplate:Thermostat', 'Building',
                                   'GlobalGeometryRules', 'outputPreProcessorMessage', 'epJSON']:
                object_check = False
        self.assertTrue(object_check)
        return
