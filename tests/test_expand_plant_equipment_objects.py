import unittest

from src.expand_objects import ExpandPlantEquipment
from . import BaseTest


class TestExpandPlantEquipmentObjects(BaseTest, unittest.TestCase):
    """
    EnergyPlus object testing for ExpandPlantEquipment operations
    """
    def setUp(self):
        return

    def teardown(self):
        return

    def test_water_cooled_chiller_equipment_objects_created(self):
        epe = ExpandPlantEquipment(template={
            "HVACTemplate:Plant:Chiller": {
                "Main Chiller": {
                    "capacity": "Autosize",
                    "chiller_type": "ElectricReciprocatingChiller",
                    "condenser_type": "WaterCooled",
                    "nominal_cop": 3.2,
                    "priority": "1"
                }
            }
        })
        output = epe.run()
        self.assertEqual(
            {
                'Branch': 2,
                'Chiller:Electric:EIR': 1,
                'Curve:Biquadratic': 2,
                'Curve:Quadratic': 1
            },
            epe.summarize_epjson(output.epjson))
        return

    def test_hot_water_boiler_objects_created(self):
        # epe = ExpandPlantEquipment(template={
        #     "HVACTemplate:Plant:Boiler": {
        #         "Main Boiler": {
        #             "boiler_type": "HotWaterBoiler",
        #             "capacity": "Autosize",
        #             "efficiency": 0.8,
        #             "fuel_type": "NaturalGas",
        #             "priority": "1"
        #         }
        #     }
        # })
        # todo_eo: Need to figure out how to handle template_plant_loop_type list structure to format
        # print(epe.template_plant_loop_type)
        # output = epe.run()
        # from pprint import pprint
        # pprint(output.epjson, width=200)
        return
