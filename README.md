# pyExpandObjects

FIX BRANCH NAMES IN THESE LINKS

[![Documentation Status](https://readthedocs.org/projects/epjson-expandobjects/badge/?version=main)](https://epjson-expandobjects.readthedocs.io/en/main/?badge=main)
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/john-grando/pyExpandObjects/Unit%20Tests)](https://github.com/john-grando/pyExpandObjects/actions)
[![Coverage Status](https://coveralls.io/repos/github/john-grando/pyExpandObjects/badge.svg?branch=main)](https://coveralls.io/github/john-grando/pyExpandObjects?branch=main)
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/john-grando/pyExpandObjects/Flake8?label=pep8)](https://github.com/john-grando/pyExpandObjects/actions)

HVACTemplate and ExpandObjects support with epJSON


#### Example Instructions

This program is still in development; however, some files can be processed.  The command for expanding files is as follows

* --file: The epJSON file containing HVACTemplate Objects.
* --output_directory: The output directory.  If none is specified, the epJSON file directory is used.

`python src/main.py --file simulation/ExampleFiles/HVACTemplate-5ZoneVAVWaterCooled.epJSON`

This program will output three files:

* original-file-name_base.epJSON: Contains all non HVACTemplate objects from original file
* original-file-name_hvac_templates.epJSON: Contains all HVACTemplate objects from original file
* original-file-name_expanded.epJSON: Expanded file for simulation.
