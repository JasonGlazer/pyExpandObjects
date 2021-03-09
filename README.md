# pyExpandObjects

FIX BRANCH NAMES IN THESE LINKS

[![Documentation Status](https://readthedocs.org/projects/epjson-expandobjects/badge/?version=latest)](https://epjson-expandobjects.readthedocs.io/en/latest/?badge=latest)
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/john-grando/pyExpandObjects/Unit%20Tests)](https://github.com/john-grando/pyExpandObjects/actions)
[![Coverage Status](https://coveralls.io/repos/github/john-grando/pyExpandObjects/badge.svg?branch=main)](https://coveralls.io/github/john-grando/pyExpandObjects?branch=main)
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/john-grando/pyExpandObjects/Flake8?label=pep8)](https://github.com/john-grando/pyExpandObjects/actions)

HVACTemplate and ExpandObjects support with epJSON


#### Example Instructions

An example script and files are provided for initial testing.  There are two command line arguments that must be provided

* -y: The yaml file location
* -f: The epJSON file containing HVACTemplate Objects

`python test/expand_examples/expand_vav_system.py -y expand_objects/resources/energyplus_objects_config.yaml -f test/expand_examples/expand_vav_system.epJSON`

The program will output a file 'epjson_test.epJSON' to the same directory as the python file.