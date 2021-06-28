from pathlib import Path

from tests.simulations import BaseSimulationTest
from src.epjson_handler import EPJSON

test_dir = Path(__file__).parent.parent.parent


class TestSimulationsPlantEquipmentBoilerObjectReference(BaseSimulationTest):
    def setUp(self):
        self.ej = EPJSON()
        base_idf_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles',
                                               'HVACTemplate-5ZoneVAVWaterCooled-ObjectReference.idf')
        base_copy_file_path = self._copy_to_test_directory(base_idf_file_path)
        # read in base file, then edit inputs for alternate tests
        self.base_epjson = self.get_epjson_object_from_idf_file(base_copy_file_path)
        return

    def teardown(self):
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:PlantEquipment:Boiler:ObjectReference:priority")
    def test_priority(self):
        # todo_eo: discuss with team that priority requires a string and not integer.
        self.base_epjson['HVACTemplate:Plant:Boiler:ObjectReference']['Main Boiler Connection']['priority'] = 2
        self.ej.merge_epjson(
            super_dictionary=self.base_epjson,
            object_dictionary={
                "Boiler:HotWater": {
                    "Second Boiler": {
                        "boiler_flow_mode": "ConstantFlow",
                        "boiler_water_inlet_node_name": "Second Boiler HW Inlet",
                        "boiler_water_outlet_node_name": "Second Boiler HW Outlet",
                        "design_water_flow_rate": "Autosize",
                        "efficiency_curve_temperature_evaluation_variable": "LeavingBoiler",
                        "fuel_type": "NaturalGas",
                        "maximum_part_load_ratio": 1.1,
                        "minimum_part_load_ratio": 0.0,
                        "nominal_capacity": "Autosize",
                        "nominal_thermal_efficiency": 0.8,
                        "normalized_boiler_efficiency_curve_name": "Second Boiler Efficiency Curve",
                        "optimum_part_load_ratio": 1.0,
                        "parasitic_electric_load": 0,
                        "sizing_factor": 1.0,
                        "water_outlet_upper_temperature_limit": 100.0
                    }
                },
                "Curve:Quadratic": {
                    "second Boiler Efficiency Curve": {
                        "coefficient1_constant": 0.97,
                        "coefficient2_x": 0.0633,
                        "coefficient3_x_2": -0.0333,
                        "maximum_value_of_x": 1.0,
                        "minimum_value_of_x": 0.0
                    }
                },
                'HVACTemplate:Plant:Boiler:ObjectReference': {
                    'Second Boiler Connections': {
                        "boiler_object_type": "Boiler:HotWater",
                        "boiler_name": "Second Boiler",
                        "priority": 1
                    }
                }
            }
        )
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath('..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'Second Boiler',
            epjson_output['PlantEquipmentList']['Hot Water Loop All Equipment']['equipment'][0]['equipment_name'])
        return