import tempfile
import json
from pathlib import Path

from tests.simulations import BaseSimulationTest
from src.epjson_handler import EPJSON

test_dir = Path(__file__).parent.parent


class TestSimulationsFullSystem(BaseSimulationTest):
    def setUp(self):
        return

    def teardown(self):
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Full:Base:HVACTemplate-5ZoneFanCoil")
    def test_simulation_full_hvactemplate_5_zone_fan_coil(self):
        base_file_path = str(test_dir / '..' / 'simulation' / 'ExampleFiles' /
                             'HVACTemplate-5ZoneFanCoil.epJSON')
        self.perform_full_comparison(baseline_file_location=base_file_path)
        return

    @BaseSimulationTest._test_logger(doc_text="Simulation:Full:Base:HVACTemplate-5ZoneVAVWaterCooled")
    def test_simulation_full_hvactemplate_5_zone_vav_watercooled(self):
        base_file_path = str(test_dir / '..' / 'simulation' / 'ExampleFiles' /
                             'HVACTemplate-5ZoneVAVWaterCooled.epJSON')
        self.perform_full_comparison(baseline_file_location=base_file_path)
        return
