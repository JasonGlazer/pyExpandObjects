from pathlib import Path

from tests.simulations import BaseSimulationTest

test_dir = Path(__file__).parent.parent


class TestSimulationsFullSystem(BaseSimulationTest):
    def setUp(self):
        return

    def teardown(self):
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Full:Base:HVACTemplate-5ZoneBaseboardHeat")
    def test_simulation_full_hvactemplate_5_zone_baseboard_heat(self):
        base_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles', 'HVACTemplate-5ZoneBaseboardHeat.idf')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Full:Base:HVACTemplate-5ZoneFanCoil")
    def test_simulation_full_hvactemplate_5_zone_fan_coil(self):
        base_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles', 'HVACTemplate-5ZoneFanCoil.idf')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Full:Base:HVACTemplate-5ZoneVAVWaterCooled")
    def test_simulation_full_hvactemplate_5_zone_vav_watercooled(self):
        base_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles', 'HVACTemplate-5ZoneVAVWaterCooled.idf')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        return
