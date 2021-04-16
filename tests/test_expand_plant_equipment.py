import copy
import unittest

from src.expand_objects import ExpandPlantEquipment
from src.expand_objects import InvalidTemplateException
from . import BaseTest

mock_plant_equipment_template = {
    "HVACTemplate:Plant:Chiller": {
        "Main Chiller": {
            "capacity": "Autosize",
            "chiller_type": "ElectricReciprocatingChiller",
            "condenser_type": "WaterCooled",
            "nominal_cop": 3.2,
            "priority": "1"
        }
    }
}


class TestExpandPlantEquipmentObjects(BaseTest, unittest.TestCase):
    """
    General processing of ExpandPlantEquipmentLoop operations
    """
    def setUp(self):
        return

    def teardown(self):
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:PlantEquipment:Input Template Required")
    def test_check_templates_are_required(self):
        with self.assertRaises(TypeError):
            ExpandPlantEquipment()
        return

    @BaseTest._test_logger(doc_text="HVACTemplate:PlantEquipment:Verify valid template object")
    def test_verify_good_template(self):
        output = ExpandPlantEquipment(template=mock_plant_equipment_template)
        self.assertEqual('Main Chiller', output.template_name)
        return

    def test_verify_plant_loop_type_is_set_default(self):
        output = ExpandPlantEquipment(template=mock_plant_equipment_template)
        self.assertEqual(['ChilledWaterLoop', ], output.plant_loop_type)
        return

    def test_verify_plant_loop_type_is_set_from_template(self):
        tmp_mock = copy.deepcopy(mock_plant_equipment_template)
        tmp_mock['HVACTemplate:Plant:Chiller']['Main Chiller']['template_plant_loop_type'] = 'Test'
        output = ExpandPlantEquipment(template=tmp_mock)
        self.assertEqual(['TestLoop', ], output.plant_loop_type)
        return

    def test_reject_plant_loop_type_with_no_default_options(self):
        tmp_mock = {
            "HVACTemplate:Plant:BadEquipment": {
                "Bad Name": {
                    "capacity": "Autosize"
                }
            }
        }
        with self.assertRaisesRegex(InvalidTemplateException, 'Plant equipment loop was not set and'):
            ExpandPlantEquipment(template=tmp_mock)
        return
