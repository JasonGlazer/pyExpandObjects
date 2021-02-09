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
5. For each System group a yaml file object will be called for each HVACTemplate:System:* object which contains a group of objects to create the necessary EnergyPlus objects.  Customized build lists based on HVACTemplate:System inputs are provided.  Additionally, programming logic is performed to overwrite any defaults with the user input.  The output will be a list of EnergyPlus objects stored as a class variable.  Detailed explanation of Yaml file structure:

    * buildPath - list of objects to create along the flow path of the network.  Each object contains:

      * fields - key-pairs of variable names and values to populate the object.  Values with '{}' will have the system name inserted to ensure unique entries.
      * connectors - hierarchical dictionary of variable names that serve as the loop inlets and outlets.  Note, values that are written by default in the object['fields'][variable name] will be overridden in some cases to ensure all objects are connected.

        * [air, hotWater, coldWater, mixedWater]

          * inlet - variable name of input node to next object
          * outlet - variable name of output node to next object

    * controllers - Dictionary of Controller objects to use as and node locations for input values.  These objects will be created after the buildPath.
    * setpointManagers - Dictionary of SetpointManager objects to use and node locations for input values.  These objects will be created after the buildPath.
    * transitions - Dictionary of mappings from the template input variable name to the equipment variable name to be updated.

6. For each System, a yaml file object will be called for each HVACTemplate:Zone:* object which contains a group of objects to create the necessary EnergyPlus objects.  The output will be a list of lists (one per system branch) of EnergyPlus objects stored as a class variable.
7. Template user-provided input variables are passed to the created objects.
8. Controllers and SetpointManagers are created.
9. For each HVACTemplate:Plant[Chilled,Hot,Mixed]WaterLoop

  1. Systems are created using a similar process as described above.
  2. For each system group created by HVACTemplate:System:

    1. The class attributes are scanned for possible inclusion of water loop objects.
    2. If present, each system and zone list will is scanned for water loop objects.
    3. If water loop objects are found, then yaml file objects are called to build the supporting objects to connect the water loop system to those elements.
    4. The output is saved as a list of lists (one per system branch) in the class.

  3. Controllers and SetpointMnaagers are create for the water loop.

10. HVAC:Template objects are handled in a similar, but more simplified way.
11. For each system loop, additional required objects will be created based on the class structure (e.g. Branch, BranchList, Connector:\*)

12. All created objects are checked for duplicate keys and merged to one epJSON object.
13. The original template objects are removed from the input file and new objects are merged after checking for duplicate keys.
14. epJSON file validation is performed.
15. Errors and warnings are written to the standard error file.
16. If validated, the epJSON object is output as result for the downstream pipeline.

.. _Versioned Validator: https://python-jsonschema.readthedocs.io/en/stable/validate/#versioned-validators

**Sample Yaml Configuration**

.. code-block:: yaml

  # Objects
  OutdoorAir:NodeLists:
    BaseConfig: &OutdoorAirNodeListBase
      OutdoorAir:NodeList:
        Fields:
          - '{} Outside Air Inlet'
        Connectors:
          Air:
            Outlet: '{} Outside Air Inlet'

  OutdoorAir:Mixers: # structure might be unnecessary but is being used for example
    CommonFields: &OutdoorAirMixersCommonFields
      name: '{} OA Mixing Box'
      mixed_Air_node_name: '{} Mixed Air Outlet'
      outdoor_Air_stream_node_name: '{} Outside Air Inlet' #will be overridden
      relief_Air_stream_node_name: '{} Relief Air Outlet'
      return_Air_stream_node_name: '{} Return Air Loop Inlet'
    CommonConnectors: &OutdoorAirMixersCommonConnectors
      Air:
        inlet: outdoor_Air_stream_node_name
        Outlet: mixed_Air_node_name
    BaseConfig: &OutdoorAirMixerBase
      OutdoorAir:Mixer:
        Fields:
          << : *OutdoorAirMixersCommonFields
        Connectors:
          << : *OutdoorAirMixersCommonConnectors

  Coils:
    CommonFields: &CoilsCommonFields
      name: '{} Cooling Coil'
    Cooling:
      Water:
        CommonFields: &CoilsCoolingCommonFields
          Air_inlet_node_name: '{} Cooling Coil Inlet'
          Air_Outlet_node_name: '{} Cooling Coil Outlet'
          water_inlet_node_name: '{} Cooling Coil Chw Inlet'
          water_Outlet_node_name: '{} Cooling Coil Chw Outlet'
        CommonConnectors: &CoilsCoolingCommonConnectors
          Air:
            inlet: Air_inlet_node_name
            Outlet: Air_Outlet_node_name
          ChilledWater:
            inlet: water_inlet_node_name
            Outlet: water_Outlet_node_name
        Base: &CoilsCoolingWaterBase
          Coil:Cooling:Water:
            Fields:
              << : *CoilsCommonFields
              << : *CoilsCoolingCommonFields
            Connectors:
              << : *CoilsCoolingCommonConnectors
        DetailedGeometry: &CoilsCoolingWaterDetailedGeometry
          Coil:Cooling:Water:DetailedGeometry:
            Fields:
              << : *CoilsCommonFields
              << : *CoilsCoolingCommonFields
            Connectors:
              << : *CoilsCoolingCommonConnectors

  # Basic Systems
  SystemConfigOutdoorAirBase: &SystemConfigOutdoorAirBase
    - << : *OutdoorAirNodeListBase
    - << : *OutdoorAirMixerBase

  #HVAC System Templates
  HVACTemplate:System:VAV:
    buildPath:
      - *SystemConfigOutdoorAirBase
      - *CoilsCoolingWaterBase
    transitions:
      supply_fan_total_efficiency:
        Fan:VariableVolume: fan_total_efficiency
    setpointManagers:
      SetpointManager:MixedAir:
        name: '{} Cooling Coil Air Temp Manager'
        control_variable: 'Temperature'
        reference_setpoint_node_name:
          AirLoopHVAC: 'supply_side_Outlet_node_names'
    controllers:
      Controller:OutdoorAir:
        name: '{} OA Controller'
        revief_Air_Outlet_node_name:
          OutdoorAir:Mixer: relief_Air_stream_node_name
        return_Air_node_name:
          OutdoorAir:Mixer: return_Air_stream_node_name
        minimum_outdoor_Air_flow_rate: autosize
        maximum_outdoor_Air_flow_rate: autosize

**Sample Output**

.. code-block:: python

  {
    'buildPath': [
      [
        {
          'OutdoorAir:NodeList': {
            'Fields': [
              '{} Outside Air Inlet'
            ],
            'Connectors': {
              'Air': {
                'Outlet': '{} Outside Air Inlet'
              }
            }
          }
        },
        {
          'OutdoorAir:Mixer': {
            'Fields': {
              'name': '{} OA Mixing Box',
              'mixed_Air_node_name': '{} Mixed Air Outlet',
              'outdoor_Air_stream_node_name': '{} Outside Air Inlet',
              'relief_Air_stream_node_name': '{} Relief Air Outlet',
              'return_Air_stream_node_name': '{} Return Air Loop Inlet'
            },
            'Connectors': {
              'Air': {
                'inlet': 'outdoor_Air_stream_node_name',
                'Outlet': 'mixed_Air_node_name'
              }
            }
          }
        }
      ],
      {
        'Coil:Cooling:Water': {
          'Fields': {
            'name': '{} Cooling Coil',
            'Air_inlet_node_name': '{} Cooling Coil Inlet',
            'Air_Outlet_node_name': '{} Cooling Coil Outlet',
            'water_inlet_node_name': '{} Cooling Coil Chw Inlet',
            'water_Outlet_node_name': '{} Cooling Coil Chw Outlet'
          },
          'Connectors': {
            'Air': {
              'inlet': 'Air_inlet_node_name',
              'Outlet': 'Air_Outlet_node_name'
            },
            'ChilledWater': {
              'inlet': 'water_inlet_node_name',
              'Outlet': 'water_Outlet_node_name'
            }
          }
        }
      }
    ],
    'transitions': {
      'supply_fan_total_efficiency': {
        'Fan:VariableVolume': 'fan_total_efficiency'
      }
    },
    'setpointManagers': {
      'SetpointManager:MixedAir': {
        'name': '{} Cooling Coil Air Temp Manager',
        'control_variable': 'Temperature',
        'reference_setpoint_node_name': {
          'AirLoopHVAC': 'supply_side_Outlet_node_names'
        }
      }
    },
    'controllers': {
      'Controller:OutdoorAir': {
        'name': '{} OA Controller',
        'revief_Air_Outlet_node_name': {
          'OutdoorAir:Mixer': 'relief_Air_stream_node_name'
        },
        'return_Air_node_name': {
          'OutdoorAir:Mixer': 'return_Air_stream_node_name'
        },
        'minimum_outdoor_Air_flow_rate': 'autosize',
        'maximum_outdoor_Air_flow_rate': 'autosize'
      }
    }
  }

----------------------
Command Line Interface
----------------------

... in progress...