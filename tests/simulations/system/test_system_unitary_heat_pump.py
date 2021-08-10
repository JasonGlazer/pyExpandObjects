from pathlib import Path

from tests.simulations import BaseSimulationTest
from src.epjson_handler import EPJSON

test_dir = Path(__file__).parent.parent.parent


class TestSimulationsSystemUnitaryHeatPump(BaseSimulationTest):
    def setUp(self):
        self.ej = EPJSON()
        base_idf_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles',
                                               'HVACTemplate-5ZoneUnitaryHeatPump.idf')
        base_copy_file_path = self._copy_to_test_directory(base_idf_file_path)
        # read in base file, then edit inputs for alternate tests
        self.base_epjson = self.get_epjson_object_from_idf_file(base_copy_file_path)
        self.base_epjson.pop('Output:Variable')
        return

    def teardown(self):
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:system_availability_schedule_name")
    def test_system_availability_schedule_name(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'system_availability_schedule_name'] = 'OCCUPY-1'
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'night_cycle_control'] = 'CycleOnAny'
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['Fan:OnOff']['Heat Pump 1 Supply Fan']['availability_schedule_name'])
        self.assertEqual(
            'OCCUPY-1',
            epjson_output['AvailabilityManager:NightCycle']['Heat Pump 1 Availability']['fan_schedule_name'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:cooling_supplY_air_flow_rate")
    def test_cooling_supply_air_flow_rate(self):
        # todo_eo: rated_air_flow_rate in cooling coil is set by this input, but is not in other systems.  Is that
        #  correct?  Usually just the Sizing:System an AirLoop objects are set.
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'cooling_supply_air_flow_rate'] = 1.01
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            1.01,
            epjson_output['Sizing:System']['Heat Pump 1 Sizing System']['cooling_supply_air_flow_rate'])
        self.assertEqual(
            1.01,
            epjson_output['AirLoopHVAC:UnitaryHeatPump:AirToAir']['Heat Pump 1 Heat Pump'][
                'cooling_supply_air_flow_rate'])
        self.assertEqual(
            1.01,
            epjson_output['Coil:Cooling:DX:SingleSpeed']['Heat Pump 1 Cooling Coil'][
                'rated_air_flow_rate'])
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:System:UnitaryHeatPump:heating_supplY_air_flow_rate")
    def test_heating_supply_air_flow_rate(self):
        self.base_epjson['HVACTemplate:System:UnitaryHeatPump:AirToAir']['Heat Pump 1'][
            'heating_supply_air_flow_rate'] = 1.01
        base_file_path = self.create_idf_file_from_epjson(epjson=self.base_epjson, file_name='base_pre_input.epJSON')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        epjson_output = self.ej._get_json_file(test_dir.joinpath(
            '..', 'simulation', 'test', 'test_input_epjson.epJSON'))
        self.assertEqual(
            1.01,
            epjson_output['Sizing:System']['Heat Pump 1 Sizing System']['heating_supply_air_flow_rate'])
        return
