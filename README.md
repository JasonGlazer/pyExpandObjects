# pyExpandObjects

[![Documentation Status](https://readthedocs.org/projects/epjson-expandobjects/badge/?version=main)](https://epjson-expandobjects.readthedocs.io/en/main/?badge=main)
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/john-grando/pyExpandObjects/Unit%20Tests)](https://github.com/john-grando/pyExpandObjects/actions)
[![Coverage Status](https://coveralls.io/repos/github/john-grando/pyExpandObjects/badge.svg?branch=main)](https://coveralls.io/github/john-grando/pyExpandObjects?branch=main)
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/john-grando/pyExpandObjects/Flake8?label=pep8)](https://github.com/john-grando/pyExpandObjects/actions)

HVACTemplate and ExpandObjects support with epJSON

#### Overview

Much like the existing ExpandObjects program packaged in EnergyPlus, the pyExpandObjects expands HVACTem-
plate objects from into an expanded file that can be directly run in EnergyPlus, but in this case the processed files are in epJSON format.  Additionally, in order to achieve greater alignment with other programming initiatives in EnergyPlus, take advantage of the epJSON schema structure, and make use of object-oriented programming methodologies, this program is written in Python.  This tool provides the same deliverable as its predecessor, which is an output file with regular objects that have been mapped from template objects, but in epJSON format.

#### General Instructions

This program is called via the command line with the following arguments:

* --file: The epJSON file containing HVACTemplate Objects.
* --output_directory: The directory to output expanded files.  If none is specified, the epJSON file directory is used.
* --no_backup: Prevent the creation of optional file outputs.
* --no_schema: Skip epJSON schema verification steps.
* --logger_level: Specify the level of logging output.  This follows the standard Python logging naming structure (e.g. DEBUG, WARN, etc.)

Unless `--no_backup` is specified, this program will output three files.  If `--no_backup` is specified, then only the last item will be created.

* original-file-name_base.epJSON: Contains all non HVACTemplate objects from original file
* original-file-name_hvac_templates.epJSON: Contains all HVACTemplate objects from original file
* original-file-name_expanded.epJSON: Expanded file for simulation.
