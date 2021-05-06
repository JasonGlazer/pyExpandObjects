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

    @BaseSimulationTest._test_logger(doc_text="Simulation:Full:System:HVACTemplate-5ZoneVAVWAterCooled:Return Fan")
    def test_simulation_full_hvactemplate_5_zone_vav_watercooled_with_return_fan(self):
        base_file_path = str(test_dir / '..' / 'simulation' / 'ExampleFiles' /
                             'HVACTemplate-5ZoneVAVWaterCooled.epJSON')
        # read in base file, then edit inputs for alternate tests
        ej = EPJSON()
        base_epjson = ej._get_json_file(base_file_path)
        base_epjson['HVACTemplate:System:VAV']['VAV Sys 1']['return_fan'] = 'Yes'
        with tempfile.NamedTemporaryFile() as tmp_f:
            with open(tmp_f.name, 'w') as f:
                json.dump(base_epjson, f, indent=4, sort_keys=True)
                f.seek(0)
                self.perform_full_comparison(baseline_file_location=tmp_f.name)
        return
