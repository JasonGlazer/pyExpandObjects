***********************
Code Structure Overview
***********************

------------------------------
Class Inheritance and Overview
------------------------------
The pyExpandObject classes are loosely structured to reflect the hierarchy of the EnergyPlus HVACTemplate naming conventions.  These classes will hold common methods and procedures that can be shared to child classes.  Also, some classes will hold high-level variables and flags which will inform the child classes.  These classes build the necessary functions to identify and organize the various template objects.  The actual expansion mapping from template to regular object is held within a set of yaml files which are discussed in detail in a later section.  While some command line arguments are provided, this program serves a simple static service; it translates epJSON files which contain HVACTemplate objects to expanded epJSON files with only regular objects that are ready for simulation.

**Class Inheritance Tree**

* Logger

  * EPJSON

    * HVACTemplate

      * System
      * Plant

        * HotWater
        * ChilledWater
        * MixedWater
      * Thermostat

Logger
~~~~~~
A logging object is created and saved globally so that no duplicate loggers will be created.  This class has only an initialization function which returns a logger object as a class attribute.

EPJSON
~~~~~~
The input and output file type (epJSON) are JSON objects which follow a schema structure.  This class is where all input/output operations occur; such as reading, writing, and validating epJSON files.

.... Remaining classes ....

------------------------------
Operational Logic
------------------------------
Given that pyExpandObject serves a simple overall purpose, the processing path is fairly static.  Outlined below are the general steps that the program takes to perform its operation.

1. A schema file is read and validated using the jsonschema package `Versioned Validator`_ class.  In this case, the Draft4Validator is used.  If the `--no-schema` option has been passed to the program, then no validation will occur at any point in the process.
2. The epJSON file is read, validated, and loaded as a dictionary object.
3. The HVACTemplate class is initialized and extracts all HVACTemplate objects from the epJSON input file object.
4. The objects are organized into groups by their dependencies to the top-level HVACTemplate:System object and stored as a class-level attribute for the System class operations.  For HVACTemplate:Zone level objects that require no System class, a special 'NA' system will be created.
5. Groups created for Plant:ChilledWater, Plant:HotWater, Plant:MixedWater, and Thermostat
6. For each System group:

  1. A yaml file will be called which contains a list of build steps for that system type (key = 'build_path').  Each build step will contain a dictionary where they key value is the EnergyPlus object to be created.  The value is a sub-dictionary that identifies:

    * output - value to return at completion of object build.  This is intended to be the connecting node to the next object.
    * fields - key-value pairs to insert node names.  values identified as 'output_value' will  use the output value returned from the previous object.

  2. A yaml file will be called which contains build steps for each zone system type, including water coils.  Groups of water coils will be stored and saved for the Plant:* class steps noted below.

7.asdf

.. _Versioned Validator: https://python-jsonschema.readthedocs.io/en/stable/validate/#versioned-validators

----------------------
Command Line Interface
----------------------



Unstructured Notes
~~~~~~~~~~~~~~~~~~

HVACTemplate
* Attributes

  * templates_exist - boolean for whether templates were detected
  * templates - dictionary of captured objects
  * chilled_water_templates - Plant:* objects that belong to chilled water.
  * hot_water_templates - hw loop objects
  * mixed_water_templates - mw loop objects
  * flags needed for controllers, setpointmanagers, etc.

HVACTemplate(System)

Yaml example showing how code reuses common configurations

.. code-block:: yaml

  base: &baseOutdoorAir
    OutdoorAir:NodeList:
      fields:
        - '{} Outside Air Inlet'
      output:
        - '{} Outside Air Inlet'
    OutdoorAir:Mixer:
      fields:
        name: '{} OA Mixing Box'
        mixed_air_node_name: '{} Mixed Air Outlet'
        outdoor_air_stream_node_name: 'output_val'
        relief_air_stream_node_name: '{} Relief Air Outlet'
        return_air_stream_node_name: '{} Return Air Loop Inlet'
      output:
        - '{} Mixed Air Outlet'

  HVACTemplate:System:VAV:
    - buildpath:
      - *baseOutdoorAir
      - Coil:Cooling:Water:
        fields:
          name: '{} Cooling Coil'
          air_indlet_node_name : 'output_val'

  HVACTemplate:System:ConstantVolume:
    - buildpath:
      - *baseOutdoorAir
      - Coil:Cooling:Water:
        fields:
          name: '{} Cooling Coil'
          air_indlet_node_name : 'output_val'

.. code-block:: python

  # base
  {'OutdoorAir:NodeList': {'fields': ['{} Outside Air Inlet'], 'output': ['{} Outside Air Inlet']}, 'OutdoorAir:Mixer': {'fields': {'name': '{} OA Mixing Box', 'mixed_air_node_name': '{} Mixed Air Outlet', 'outdoor_air_stream_node_name': 'output_val', 'relief_air_stream_node_name': '{} Relief Air Outlet', 'return_air_stream_node_name': '{} Return Air Loop Inlet'}, 'output': ['{} Mixed Air Outlet']}}
  #HVACTemplate:System:VAV
  [{'buildpath': [{'OutdoorAir:NodeList': {'fields': ['{} Outside Air Inlet'], 'output': ['{} Outside Air Inlet']}, 'OutdoorAir:Mixer': {'fields': {'name': '{} OA Mixing Box', 'mixed_air_node_name': '{} Mixed Air Outlet', 'outdoor_air_stream_node_name': 'output_val', 'relief_air_stream_node_name': '{} Relief Air Outlet', 'return_air_stream_node_name': '{} Return Air Loop Inlet'}, 'output': ['{} Mixed Air Outlet']}}, {'Coil:Cooling:Water': None, 'fields': {'name': '{} Cooling Coil', 'air_indlet_node_name': 'output_val'}}]}]
  #HVACTemplate:System:ConstantVolume
  [{'buildpath': [{'OutdoorAir:NodeList': {'fields': ['{} Outside Air Inlet'], 'output': ['{} Outside Air Inlet']}, 'OutdoorAir:Mixer': {'fields': {'name': '{} OA Mixing Box', 'mixed_air_node_name': '{} Mixed Air Outlet', 'outdoor_air_stream_node_name': 'output_val', 'relief_air_stream_node_name': '{} Relief Air Outlet', 'return_air_stream_node_name': '{} Return Air Loop Inlet'}, 'output': ['{} Mixed Air Outlet']}}, {'Coil:Cooling:Water': None, 'fields': {'name': '{} Cooling Coil', 'air_indlet_node_name': 'output_val'}}]}]




HVT(chilled water, hw, mw)
Same as above for system
Zone: similar but call created object and update for each chw/hw/mw

HVT(packaged)
Zone only

HVT(VRF)?

HVT(Themostat)
same as above (example)
