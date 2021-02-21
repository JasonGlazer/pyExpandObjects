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
Process Flow
------------------------------
Given that pyExpandObject serves a simple overall purpose, the processing path is fairly static.  Outlined below are the general steps that the program takes to perform its operation.

1. A schema file is read and validated using the jsonschema package `Versioned Validator`_ class.  In this case, the Draft4Validator is used.  If the `--no-schema` option has been passed to the program, then no validation will occur at any point in the process.
2. The epJSON file is read, validated, and loaded as a dictionary object.
3. All HVACTemplate objects are extracted from the epJSON input file object and loaded into an HVACTemplate class for processing.
4. The template objects are organized into groups by their dependencies to the top-level HVACTemplate:System object and stored as a an attribute in the System class.  For HVACTemplate:Zone level objects that require no System class, a special 'NA' system will be created.
5. For each System group a yaml object will be called to construct the necessary EnergyPlus objects.  These build lists have built-in overrides based on selected template options.  Additionally, programming logic is performed to further manipulate these structures and customize the final output.  The result of this process will be a a group of epJSON EnergyPlus objects stored as a class variable as well as the structural elements used to build it.  A detailed description of Yaml file structure can be found in the following section.
6. For each zone in a system group, a yaml object will be called to construct the necessary EnergyPlus objects.  The output will be an epJSON object for all zone objects as well as the structural elements used to build it.
7. For each HVACTemplate:Plant[Chilled,Hot,Mixed]WaterLoop:

  1. Supply side equipment loops are created using a similar process as described above.
  2. The system and zone groups created above are scanned for loop objects.
  3. If water loop equipment is found, yaml objects are used to build the all the elements necessary to connect the demand side water loop system to those objects.
  4. The output will be an epJSON object for all created branches as well as the structural elements used to build them.

8. HVAC:Thermostat objects are handled in a similar, but more simplified way.
9. Controllers, SetpointManagers, Branches, and other objects which do not exist as equipment objects in the air/water loop paths are constructed.
10. Checks for data quality (e.g. duplicate values, missing values, malformed objects, etc.) are performed.
11. All previously created epJSON objects are merged to form a single object.
12. The epJSON file is validated against the schema.
13. A dictionary output is provided to the downstream process.  At a minimum, this object will have a key called 'outputPreProcessMessage' which will contain all warnings and errors generated from this process.  On a successful template expansion, a valid epJSON object will also be produced.
14. If the `--backup-files` option has been specified, the optional "\<original-file-name\>_hvac_templates.epJSON" and "\<original-file-name\>_base.epJSON" files will be output.


.. _Versioned Validator: https://python-jsonschema.readthedocs.io/en/stable/validate/#versioned-validators

**Detailed Yaml Description**

**Base Objects**

These are EnergyPlus 'super' objects.  Their field names mirror those of EnergyPlus objects while also holding extra information necessary to build them in an overall path.

    * Fields

        * Key: EnergyPlus field names
        * Value: Values to be inserted as default text.  if a '{}' is present, then the value is intended to have additional text inserted via the python `.format()` method.

    * Connectors

        * Loop Type [Air, ChilledWater, MixedWater]

            * Inlet - EnergyPlus inlet node name for the loop type.
            * Outlet - EnergyPlus outlet node name for the loop type.

Example:


.. code-block:: yaml

  OutdoorAir:Mixer:
    Fields:
      name: '{} OA Mixing Box'
      mixed_air_node_name: '{} Mixed Air Outlet'
      outdoor_air_stream_node_name: '{} Outside Air Inlet'
      relief_air_stream_node_name: '{} Relief Air Outlet'
      return_air_stream_node_name: '{} Return Air Loop Inlet'
    Connectors:
      Air:
        Inlet: outdoor_air_stream_node_name
        Outlet: mixed_air_node_name

**Sub-system Components**

These are intermediate groupings of base objects which do not fit in the typical hierarchy structures to be reused in more complex systems

.. code-block:: yaml

  SystemConfigOutdoorAirBase: &SystemConfigOutdoorAirBase
  - << : *OutdoorAirMixerBase
  - << : *CoilsCoolingWaterBase
  - << : *CoilsHeatingWaterBase
  - << : *FanVariableVolumeBase

**HVACTemplate**

This object provides a structural hierarchy to the template expansion process.

  * BuildPath - Ordered list of objects to create along the flow path of the network
  * Transitions - Mapping dictionary that transfers HVACTemplate inputs to objects (e.g. fan efficiency)
  * Connectors - System level supply and demand connectors.  The values can be expressed as a special 'complex value type'.  Please see the following section for further explanation.

**Make note that text references to other HVACTemplate objects can happen for recursive builds**

.. code-block:: yaml

  HVACTemplate:System:VAV:
    BuildPath:
      - *SystemConfigOutdoorAirBase
    Transitions:
      supply_fan_total_efficiency:
        Fan:VariableVolume: fan_total_efficiency
    Connectors:
      Supply:
        Inlet:
          OutdoorAir:Mixer: return_air_stream_node_name
      Demand:
        Inlet: '{} Supply Path Inlet'
        Outlet: '{} Return Air Outlet'

**OptionTree**

This object outlines alternate build instructions based on user inputs to the HVACTemplate

  * Base - HVACTemplate object
  * ReplaceElements - mappings from template input selections that result in a replacement operation.  For example, selecting an electric heating coil when a water coil is specified in the base build.  The EnergyPlus object reference names can be regular expressions (e.g. '^Coil:Heating:.*')
  * InsertElements - mappings from template input selections that result in insertion operations.  For example, specifying that a preheat coil should be included in the build path.  The EnergyPlus object reference names can be regular expressions (e.g. '^Fan:.*).
  * RemoveElements - Currently unused, but needs the structure indicated below if it is to be used (i.e Object: _ is necessary for all entries).

.. code-block:: yaml

  OptionTree:HVACTemplate:System:VAV:
    Base: *HVACTemplateSystemVAVBaseTemplate
    ReplaceElements:
      heating_coil_type:
        None: None
        Electric:
          ^Coil:Heating:.*:
            Occurrence: 1
            Object: *CoilsHeatingElectricBase
            FieldNameReplacement: '{} Electric'
    InsertElements:
      preheat_coil_type:
        Electric:
          OutdoorAir:M.*:
            Location: Before
            Occurrence: 1
            Object: *CoilsHeatingElectricBase
            FieldNameReplacement: '{} Preheat Electric'
            Transitions:
              preheat_efficiency: efficiency
    RemoveElements:
      reheat_coil_type:
        None:
          ^Coil:Heating:.*:
            Object: _

**Miscellaneous**

Various objects, outside of the build path, also need to be created given certain system configurations and template options.  for these objects, `AdditionalObjects` or `AdditionalTemplateObjects` can be specified within the option tree.  Additionally, the transition from HVACTemplate input to object field value can be specified:

  * AdditionalObjects - Group of objects to be created for the specified option tree build path.  This can reference regular objects and assign variables with 'complex inputs' (see below for details).  Additionally, the input value can reference HVACTemplate objects to be built in parallel to the current group.
  * AdditionalTemplateObjects - Similar to AdditionalObjects, but will on be created if specific template values are selected.
  * Transitions - Dictionary of mappings from the template input variable name to the equipment variable name to be updated.

.. code-block:: yaml

  OptionTree:
    HVACTemplate:
      ...:
        ...:
          AdditionalObjects: # nested hvac template in AdditionalObjects.
            HVACTemplate:Plant:CondenserWaterLoop: # just an example, doesn't make sense here
              ConnectorPath: CondenserWaterLoop
              UniqueName: 'Main CndW'  #Value is the unique name modifier
            SetpointManager:MixedAir:
              <<: *SetpointManagerMixedAir
              sample_additional_field: sample_transition_value
            Controller:OutdoorAir:
              <<: *ControllerOutdoorAir
          AdditionalTemplateObjects: # template triggered objects
            template_field:
              template_choice:
                object_groups:

**Complex Value Type**

These values can be expressed as either one of two types.

1. static value - Numeric or string.
2. Dictionary mapping :

  * Required Sub-dictionary

    * Key - EnergyPlus Object.  This may be in regular expression format (e.g. '^Fan:.*'
    * Value - the reference node of the object, which can be in three formats:

      * key/value pair where the key is the object and the value is the field name
      * 'self' - returns the key used to find the reference object (useful for regex)

      '^AirTerminal:.*': self - will return the full Air terminal object name

      * 'key' - returns the key of the nested dictionary of the reference object

      '^AirTerminal:.*': key - will return 'Space1-1 VAV Reheat' from {AirTerminal:SingleDuct:VAV:Reheat: 'Space1-1 VAV Reheat': {...}

  * Optional Sub-dictionary

    * Key - 'Occurrence'
    * Value - The nth occurrence of the object match.  Default is first occurrence

----------------------
Command Line Interface
----------------------

`-xb --output-backups     Output separated epJSON`

It is not possible to comment sections of code in JSON formatted files.  Therefore, expepJSON files do not have the ability to retain the HVACTemplate objects used to create the current document.  If the original file were to be overwritten, then all template data would be lost.  In an attempt to provide and additional layer of backups, this option will output two files: one with HVACTemplate objects, and one with all other objects.  With these files, the original input file can be created, or specific objects can be copied and pasted.

`-ns --no-schema     Skip all schema validation checks`

One benefit of the JSON file format is that files can be validated before simulation.  This means that erroneous inputs can be found before simulation, which saves time debugging output files and reading through logs, unsure of the error source.  This includes syntax errors, values that are out of range, and missing required inputs.  However, situations may occur when the user wishes to skip schema validation, in which case this flag should be used.