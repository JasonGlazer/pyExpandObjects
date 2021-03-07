***********************
Code Structure Overview
***********************

------------------------------
Process Flow
------------------------------
Given that pyExpandObject serves a simple overall purpose, the processing path is fairly static.  Outlined below are the general steps that the program takes to perform its operation.

1. A schema file is read and validated using the jsonschema package `Versioned Validator`_ class.  In this case, the Draft4Validator is used.  If the `--no-schema` option has been passed to the program, then no validation will occur at any point in the process.
2. The epJSON file is read, validated, and loaded as a dictionary object.
3. All HVACTemplate objects are loaded into HVACTemplate classes for processing.
4. The template objects are processed to create regular objects for the specific system, zone, plant, or loop.

  i. An `OptionTree` is loaded from the yaml file, which specifies build instructions for a given template.
  ii. EnergyPlus objects are created according to the `BuildPath` provided within the `OptionTree`.  A `BuildPath` is an ordered list of objects that follow a given fluid flow path (e.g. Air, ChilledWaterLoop, HotWaterLoop).  Alternative `BuildPath` can be created from template inputs, which cause the based `BuildPath` to have objects inserted, replaced, or removed.
  iii. Additional objects outside of the build path, but specific to the template, are created.  These are objects such as Controllers, NodeLists, SetpointManagers, etc.
  iv. Objects that connect equipment to each other are created (e.g. Zone:Splitters/Mixers, SupplyPath, Connectors, BranchLists, etc.).  Note, this is one of the few points in the process that relies on scanning the document for statically typed values.  While the values are input by the program, it is still not a preferable method and alternate solutions are under consideration.

5. HVAC:Thermostat objects are handled in a similar, but more simplified way.
6. Checks for data quality (e.g. duplicate values, missing values, malformed objects, etc.) are performed.
7. The original non-template epJSON objects are merged with the newly created objects.
8. The epJSON file is validated against the schema.
9. A dictionary output is provided to the downstream process.  At a minimum, this object will have a key called 'outputPreProcessMessage' which will contain all warnings and errors generated from this process.  On a successful template expansion, a valid epJSON object will also be produced with the file name \<original-file-name\>_expanded.epJSON
10. If the `--backup-files` option has been specified, the optional "\<original-file-name\>_hvac_templates.epJSON" and "\<original-file-name\>_base.epJSON" files will be output.

.. _Versioned Validator: https://python-jsonschema.readthedocs.io/en/stable/validate/#versioned-validators

------------------------------
Yaml Description
------------------------------

**Object Structure**

To hold the necessary information for construction, the Yaml objects which represent EnergyPlus objects have additional higher-level information, and are termed 'super' objects.  These object's standard format is as follows:

.. code-block:: yaml

  EnergyPlusObject:
    Fields:
      field_name: field_value
    Connectors:
      ConnectorPathType:
        Inlet: inlet_node_name
        Outlet: outlet_node_name

* EnergyPlusObject: This value can be entered with the full EnergyPlus object name, or a regular expression may be provided.
* field_name: The exact EnergyPlus field name must be provided.
* field_value: A 'complex reference' may be provided.  Please see below for further details
* ConnectorPathType: Must be a selection of Air, ChilledWaterLoop, CondenserWaterLoop, or MixedWaterLoop
* inlet_node_name, outlet_node_name: Must be a field_name provided from Fields

**BuildPath Objects**

This is a list of EnergyPlus 'super' objects which are in order of their fluid flow path.  Their field names mirror those of EnergyPlus objects while also holding extra information necessary to connect their input/output nodes in an overall path.

    * Fields - key/value pairs of EnergyPlus object fields and values.

        * Key: EnergyPlus field name
        * Value: Value to be inserted as default text.  A unique name, based on the template provided, can be applied by using brackets '{}' in the text.

    * Connectors - object for identifying how the fluid flow loop passes through the object.  This is used to connect nodes between objects in a `BuildPath` as well as identify inlet and outlet nodes for associated objects, like branches.

        * Loop Type [Air, ChilledWater, CondenserWater, MixedWater]

            * Inlet - EnergyPlus inlet node name for the loop type.
            * Outlet - EnergyPlus outlet node name for the loop type.
            * UseInBasePath (Optional) - Boolean value to determine if the object should be used when connecting the loop type.  This value should be set to `false` in cases of parallel equipment, such as bypass pipes or reheat coils in an AirTerminal object.  Note, the default value is `true`, but if any more than one EnergyPlus object is defined as a Base Object, then all but one EnergyPlus object should have this value set to `false` for each loop type. 

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

**HVACTemplate Objects**

This object provides a structural mapping for template expansion process.  Note, the `BuildPath` may contain other HVACTemplate objects, which will be inserted into that location recursively.

  * BuildPath - Ordered list of objects to create along the fluid flow path.
  * Transitions - Mapping of template inputs to object values (e.g. supply_fan_total_efficiency -> Fan Object -> Field [fan efficiency])

.. code-block:: yaml

  HVACTemplate:System:VAV:
    BuildPath:
      - OutdoorAir:Mixer: *OutdoorAirMixer
      - Coil:Cooling:Water: *CoilCoolingWater
      - Coil:Heating:Water: *CoilHeatingWater
      - Fan:VariableVolume: *FanVariableVolume
    Transitions:
      supply_fan_total_efficiency:
        Fan:VariableVolume: fan_total_efficiency

**OptionTree Objects**

This object outlines alternate build instructions and additional objects to be constructed based on user inputs to the HVACTemplate

  * Base - HVACTemplate object with pre-set `BuildPath`
  * ReplaceElements - Replace an object with another object.  For example, selecting an electric heating coil when a water coil is specified in the base build.  The EnergyPlus object references can be of various types, see the 'complex references' section for further details

    * Occurrence: Instance to select, if more than one exists
    * Object: Object to replace specified object
    * FieldNameReplacement: New unique name to be applied to object ('{}' -> '{} New Text)


  * InsertElements - Add an object before or after another object.  For example, specifying that a preheat coil should be included in the build path.

    * Location: Before or after selected object
    * Occurrence: Instance to select, if more than one exists
    * FieldNameReplacement: New unique name to be applied to object ('{}' -> '{} New Text)
    * Transitions: template input to object value mapping

  * RemoveElements - Remove an object. (Not currently in use)

    * Location: Before or after selected object
    * Occurrence: Instance to select, if more than one exists

.. code-block:: yaml

  OptionTree:HVACTemplate:System:VAV:
    Base: *HVACTemplateSystemVAVBaseTemplate
    ReplaceElements:
      heating_coil_type:
        None: None
        Electric:
          - ^Coil:Heating:.*:
              Occurrence: 1
              Object: *CoilsHeatingElectricBase
              FieldNameReplacement: '{} Electric'
    InsertElements:
      preheat_coil_type:
        Electric:
          - OutdoorAir:M.*:
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

**Additional Objects**

Various objects outside of the build path also need to be created, given certain system configurations and template options.  for these objects, `AdditionalObjects` or `AdditionalTemplateObjects` can be specified within the option tree.  Additionally, the transition from HVACTemplate input to object field value can be specified:

  * AdditionalObjects - Group of objects to be created for the specified option tree build path.  This can reference regular objects and assign variables with 'complex references' (see below for details).  Additionally, the input value can reference HVACTemplate objects to be built in parallel to the current group.
  * AdditionalTemplateObjects - Similar to AdditionalObjects, but will on be created if specific template values are selected.
  * Transitions - Dictionary of mappings from the template input variable name to the equipment variable name to be updated.

.. code-block:: yaml

  OptionTree:
    HVACTemplate:
      ...:
        ...:
          AdditionalObjects:
            - ZoneHVAC:AirDistributionUnit: *ZoneHVACAirDistributionUnit
            - ZoneHVAC:EquipmentList:
                <<: *ZoneHVACEquipmentList
          AdditionalTemplateObjects:
            template_thermostat_name:
              .*:
                - ZoneControl:Thermostat:
                    <<: *ZoneControlThermostat
                    Transitions:
                      zone_name: zone_or_zone_list_name
                      template_thermostat_name: control_1_name

**Complex References**

References to object field values may take multiple forms.  This feature is intended to provide greater flexibility for object definition and to link nodes without relying on static text fields.  References may be specified as follows:

* Static value: numeric or string.
    Use a directly typed value.  Note, the use of brackets ({}) will insert a unique name based on the template inputs.

.. code-block:: yaml

  SupplyPlenum:
    name: '{} Supply Plenum'

* Build Path Location Reference: object.
    Reference a node by it's location in the `BuildPath`.  This is only useful for System and Zone templates, not Plant or Loop templates.

  * Location: Location in build path to reference.  A value of -1 is the last object.
  * ConnectorPath: Fluid flow connector to use
  * ValueLocation: Inlet or Outlet of object

.. code-block:: yaml

  OutdoorAir:Nodelist:
    name: '{} Outdoor Air Nodelist'
      nodes:
        - node_or_nodelist_name:
            BuildPath:
              Location: 0
              ConnectorPath: Air
              ValueLocation: Inlet

* Self-Referential: 'self' or 'key'.
    Return either the EnergyPlusObject specified (self) or the unique name of the object (key).

.. code-block:: yaml

  ZoneHVAC:
    AirDistributionUnit:
      Base: &ZoneHVACAirDistributionUnit
        name: '{} ATU'
        air_distribution_unit_outlet_node_name:
          ^AirTerminal:.*: air_outlet_node_name
        air_terminal_object_type:
          ^AirTerminal:.*: self
        air_terminal_name:
          ^AirTerminal:.*: key

* Referenced value: string.
    Return the value of another object by specifying the field name.

.. code-block:: yaml

  Nodelist:
    name:
      ^SetpointManager:MixedAir: setpoint_node_or_nodelist_name

* Transitions
    A template value can be passed directly to an object field

.. code-block:: yaml

  - AvailabilityManager:LowTemperatureTurnOff:
      name: '{} Availability Low Temp TurnOff'
      sensor_node_name: '{} Outside Air Sensor'
      Transitions:
        chilled_water_design_setpoint: temperature

* Transitions with string reformatting
    A string reformat may be specified to mutate the input value.  For example, if the template value provided for `cooling_coil_design_setpoint` is 12.8, then The following code will yield a string value in the schedule_name field of 'HVACTemplate-Always12.8

.. code-block:: yaml

  - SetpointManager:Scheduled:
      name: '{} Cooling Supply Air Temp Manager'
      control_variable: Scheduled
      setpoint_node_or_nodelist_name:
        BuildPath:
        Location: -1
        ConnectorPath: Air
        ValueLocation: Outlet
      Transitions:
        cooling_coil_design_setpoint:
          schedule_name: 'HVACTemplate-Always{}'

The function that performs these operations takes a dictionary of epJSON objects and/or a `BuildPath` object.  Therefore, the references provided can be appropriately applied by scoping the input arguments.  For example, if the objects to be created are for a specific HVACTemplate system, then input arguments consisting only of those dependent objects can be applied.  For most cases, the input arguments are scoped to the system, zone, plant or loop template being created.

----------------------
Command Line Interface
----------------------

`-xb --output-backups     Output separated epJSON`

It is not possible to comment sections of code in JSON formatted files.  Therefore, \<original-file-name\>_expanded.epJSON files do not have the ability to retain the HVACTemplate objects used to create the current document.  If the original file were to be overwritten, then all template data would be lost.  In an attempt to provide and additional layer of backups, this option will output two files: one with HVACTemplate objects, and one with all other objects.  With these files, the original input file can be created, or specific objects can be copied and pasted.

`-ns --no-schema     Skip all schema validation checks`

One benefit of the JSON file format is that files can be validated before simulation.  This means that erroneous inputs can be found before simulation, which saves time debugging output files and reading through logs, unsure of the error source.  This includes syntax errors, values that are out of range, and missing required inputs.  However, situations may occur when the user wishes to skip schema validation, in which case this flag should be used.

------------------------------
Class Inheritance and Overview
------------------------------
The pyExpandObject classes are loosely structured to reflect the hierarchy of the EnergyPlus HVACTemplate naming conventions.  These classes will hold common methods and procedures that can be shared as well as hold high-level variables which will inform child classes.  These classes build the necessary functions to identify and organize the various template objects.  The structural elements that map template to regular objects are mostly held within a yaml file.  While some command line arguments are provided, this program serves a simple static service; it translates epJSON files which contain HVACTemplate objects to expanded, simulation ready, epJSON files with only regular objects.

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