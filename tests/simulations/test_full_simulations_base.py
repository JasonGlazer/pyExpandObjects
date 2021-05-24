from pathlib import Path

from tests.simulations import BaseSimulationTest

test_dir = Path(__file__).parent.parent


class TestSimulationsFullSystem(BaseSimulationTest):
    def setUp(self):
        return

    def teardown(self):
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Full:Base:HVACTemplate-5ZoneBaseboardHeat")
    def test_5_zone_baseboard_heat(self):
        base_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles', 'HVACTemplate-5ZoneBaseboardHeat.idf')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Full:Base:HVACTemplate-5ZoneConstantVolumeChillerBoiler")
    def test_5_zone_constant_volume_chiller_boiler(self):
        base_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles', 'HVACTemplate-5ZoneConstantVolumeChillerBoiler.idf')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        return

    # @BaseSimulationTest._test_logger(doc_text="Simulation:Full:Base:HVACTemplate-5ZoneDualDuct")
    # def test_5_zone_dual_duct(self):
    #     base_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles', 'HVACTemplate-5ZoneDualDuct.idf')
    #     self.perform_full_comparison(base_idf_file_path=base_file_path)
    #     return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Full:Base:HVACTemplate-5ZoneFanCoil")
    def test_5_zone_fan_coil(self):
        base_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles', 'HVACTemplate-5ZoneFanCoil.idf')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Full:Base:HVACTemplate-5ZoneFanCoil-DOAS")
    # Chilled water low temp turnoff is not created in base file, appears to be error.  Causing failure
    # todo_eo: discuss issue with low temp turnoff missing in base file
    def test_5_zone_fan_coil_doas(self):
        base_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles', 'HVACTemplate-5ZoneFanCoil-DOAS.idf')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Full:Base:HVACTemplate-5ZoneFurnaceDX")
    def test_5_zone_furnace_dx(self):
        base_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles', 'HVACTemplate-5ZoneFurnaceDX.idf')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Full:Base:HVACTemplate-5ZonePacakagedVAV")
    def test_5_zone_packaged_vav(self):
        base_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles', 'HVACTemplate-5ZonePackagedVAV.idf')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Full:Base:HVACTemplate-5ZonePTAC")
    def test_5_zone_ptac(self):
        base_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles', 'HVACTemplate-5ZonePTAC.idf')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Full:Base:HVACTemplate-5ZonePTAC-DOAS")
    def test_5_zone_ptac_doas(self):
        base_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles', 'HVACTemplate-5ZonePTAC-DOAS.idf')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Full:Base:HVACTemplate-5ZonePTHP")
    def test_5_zone_pthp(self):
        base_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles', 'HVACTemplate-5ZonePTHP.idf')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Full:Base:HVACTemplate-5ZoneVAVWaterCooled")
    def test_5_zone_vav_watercooled(self):
        base_file_path = test_dir.joinpath('..', 'simulation', 'ExampleFiles', 'HVACTemplate-5ZoneVAVWaterCooled.idf')
        self.perform_full_comparison(base_idf_file_path=base_file_path)
        return
