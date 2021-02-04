Create HVACTemplate and ExpandObjects Support for epJSON files
================

**John Grando, GARD Analytics**

 - Original Date: February 1, 2021
 - Revision Date: None (original date)

## Justification for New Feature ##

The addition of epJSON as an input file is impacting current workflows which rely on HVACTemplate objects. Similarly, HVACTemplate is useful for learning EnergyPlus, and provides an aid on projects focused on envelope or lighting measures, simplified interfaces, and scripted workflows.  It is important that model files built in the epJSON format have the same functionality as their equivalents written in IDF format in order to support existing workflows as well as foster future adoption.  The HVACTemplate and ExpandObjects features have proven to be valuable in the previous format, and new implementations of these tools should be developed.  

## E-mail and  Conference Call Conclusions ##

N/A

## Overview ##

In order to achieve greater alignment with other programming initiatives in EnergyPlus, take advantage of the epJSON schema structure, and make use of object-oriented programming methodologies, Python should be the chosen language for this effort.  This updated tool will provide the same deliverable as its predecessor, which is an output file with regular objects that have been mapped from template objects.  However, the epJSON file format will be used for this program.   

## Approach ##

The process for delivering this product will be different in order to better align with Python best practices and provide greater flexibility.  First, validation methods will be incorporated to ensure valid files are read and created.  An external package that performs json schema validation will be used to verify files throughout the process.  Second, an HVACTemplate class will be created in Python which will keep data attributes and methods together in a central location as well as provide the option of using inheritance and mixins for sub-classes.  This structure allows the program to be flexible when creating objects. Third, a process will be created which translates epJSON files with HVACTemplate objects to epJSON files with only regular objects. This step will make use of one-to-many mappings built into the class structure. Finally, a rigorous set of tests will created which verify the functionality and robustness of the program.  With these proposed changes, the ExpandObjects tool will be able to operate in the EnergyPlus file pre-processing pipeline by reading and writing valid epJSON files.

## Testing/Validation/Data Sources ##

Python's built-in unittest package will be used in conjunction with external packages that monitor the areas of code which have tests verifying their functionality (coverage).  Using these modules, multiple small tests (unit) will be created which verify output on the function level.  Coverage reports will be auto-generated with each build and provide confirmation of the package status.  In addition to unit testing, A subset of HVACTemplate-*.idf files will be created in epJSON format, expanded, simulated, and have outputs compared to their idf counterparts.

## Auxiliary Programs Reference Documentation ##

'Chapter 10 ExpandObjects' will be revised to have two main sections, ExpandObjects (10.1) and pyExpandObjects (10.2), The revised sections are as *follows*:

**10.1 ExpandObjects**

- 10.1.1 <- 10.1
- 10.1.2 <- 10.2
- 10.1.3 <- 10.3
- 10.1.4 <- 10.4

**10.2 pyExpandObjects**

***10.2.1 Introduction***  
*Much like the ExpandObjects program in Section 10.1, the pyExpandObjects expands HVACTemplate objects from an input epJSON file into an expanded file that can be directly run in EnergyPlus.  However, pyExpandObjects does not process GroundHeatTransfer objects or provide support for the Slab or Basement executables.*  

*The pyExpandObjects program works as a preprocessor that maps HVACTemplate objects to regular objects in EnergyPlus.  This processor reads an **epJSON** file and generates and expanded **expepJSON** file.  No further pre-processing should be required after the conversion has been performed.  Unlike ExpandObjects (10.1), a schema validation does occur when the file is read into the program, and error messages will be shown in the usual EnergyPlus error file.  By default, an invalid epJSON file will stop the program, but this requirement can be removed via command line options.  Please see the [documentation](https://epjson-expandobjects.readthedocs.io/en/latest/?badge=latest) or '--help' command line option for further details.  By default, three files are written during this process: an expanded file (expepJSON) with the same name as the original file, a file containing only the HVACTemplate objects (and the minimum objects necessary to run a simulation) which is named "\<original-file-name\>_hvac_templates.epJSON", and a file containing all objects except the HVACTemplate objects which is named "\<original-file-name\>_base.epJSON".  The pyExpandObjects program can recreate the the input file by merging the hvac_templates.epJSON and base.epJSON files.  Please refer to the documentation for further details.*

**10.2.2 HVAC Template Objects Processed**  
All HVACTemplate objects supported by the ExpandObjects program are supported in pyExpandObjects.  Please refer to section 10.1.2 for further details.

**10.2.3 Ground Heat Transfer Processed**  
GroundHeatTransfer objects are not supported by the pyExpandObjects preprocessor.

**10.2.4 Building Surface Objects Processed**  
No building surface objects are modified by the pyExpandObjects preprocessor.

## Input Output Reference Documentation ##

The current HVACTemplate Processing section (2.1) will be revised to directly address how epJSON files will be handled.  The section will be rewritten as *follows*:

**Unlike other EnergyPlus objects, the HVACTemplate objects are not handled by EnergyPlus
directly.** Instead, they are preprocessed by a program called ExpandObjects. If you use EP-Launch or
RunEPlus.bat, this preprocessor step is performed automatically using *one of the following sequences, depending on the input file format*:  

**IDF Files**  
1. The preprocessor program, ExpandObjects, reads your IDF file and converts all of the HVACTemplate objects into other EnergyPlus objects.
2. The ExpandObjects program copies the original idf file with the HVACTemplate objects commented out (i.e., inserts a “!” in front of the object name and its input fields) plus all of the new objects created in Step 1 and writes a new file which is saved with the extension “expidf”. This “expidf” file may be used as a standard EnergyPlus IDF file if the extension is changed to idf; however, for safety’s sake, both filename and extension should be changed.
3. The EnergyPlus simulation proceeds using the expidf file as the input stream.
4. If there are error messages from EnergyPlus, they will refer to the contents of the expidf file. Specific objects referred to in error messages may exist in the original idf, but they may be objects created by ExpandObjects and only exist in the expidf. Remember that the expidf will be overwritten everytime the original idf is run using EP-Launch or RunEPlus.bat  

***epJSON Files***
1. *The preprocessor program, pyExpandObjects, reads your IDF file, verifies it meets the current schema requirements, and converts all of the HVACTemplate objects into other EnergyPlus objects.*
2. *The pyExpandObjects program writes three new files*  
  a. *A file with the extension “expepJSON”. This “expepJSON” file may be used as a standard EnergyPlus epJSON file if the extension is changed to epJSON; however, for safety’s sake, both filename and extension should be changed.  Note, the HVACTemplate objects will be completely removed from the expEPJSON file, so ensure to save a copy of the original file before overwriting!*  
  b. *A file with the the name "\<original-file-name\>_hvac_templates.epJSON" which has all the HVACTemplate objects from the input file as well as the minimum additional fields to run a simulation with only these objects.*  
  c. *A file with the name "\<original-file-name\>_base.epJSON" which has all the HVACTemplate objects removed.*
3. *The EnergyPlus simulation proceeds using the expepJSON file as the input stream.*
4. *If there are error messages from EnergyPlus, they will refer to the contents of the expepJSON file. Specific objects referred to in error messages may exist in the original epJSON, but they may be objects created by pyExpandObjects and only exist in the expepJSON. Remember that the expepJSON, "\<original-file-name\>_hvac_templates.epJSON", and "\<original-file-name\>_base.epJSON" files will be overwritten everytime the original epJSON is run using EP-Launch or RunEPlus.bat.  Also note, the "\<original-file-name\>_hvac_templates.epJSON" and "\<original-file-name\>_base.epJSON" files can be merged to recreate the original epJSON file.*

If you are trying to go beyond the capabilities of the HVACTemplate objects, one strategy you can use is to start your specification using the HVACTemplate objects, run EnergyPlus using EP-Launch and producing an expidf *or epJSON* file, rename that file and start making modifications. This approach may help with getting all of the objects needed and the node names set consistently.  Users need to remember that no objects related to HVAC except for HVAC template objects are needed in the IDF */ epJSON* file. The existence of other objects (unless specifically described in the following sections) may cause unexpected errors to occur. Sizing:Zone, Sizing:System, and Sizing:Plant objects will be generated by the corresponding HVACTemplate objects; the user does not need to create these elsewhere in the input file. There are some exceptions to this rule:  
- HVACTemplate:Plant:Chiller:ObjectReference which requires that the corresponding chiller object be present in the idf */ epJSON* file along with any required curve or performance objects. In this case, the HVACTemplate object does not create the chiller object, but adds all of the connections. HVACTemplate:Plant:Tower:ObjectReference and HVACTemplate:Plant:Boiler;ObjectReferences are similar.  
- For HVACTemplate:Zone:* objects, if Outdoor Air Method = DetailedSpecification, then any referenced DesignSpecification:OutdoorAir and DesignSpecification:ZoneAirDistribution objects must be
present in the idf */ epJSON* file.  
- For HVACTemplate:Zone:VAV and HVACTemplate:Zone:DualDuct, if a Design Specification Outdoor Air Object Name for Control is specified, then the referenced DesignSpecification:OutdoorAir object must be present in the idf */ epJSON* file.

## Engineering Reference ##

None

## Example File and Transition Changes ##

A subset of HVACTemplate-*.idf files in epJSON format will be created as examples.

## References ##

Related information is provided in GitHub:  https://github.com/NREL/EnergyPlus/issues/6865

Current ExpandObjects code: https://github.com/NREL/EnergyPlus/blob/develop/src/ExpandObjects/epfilter.f90

## Design Document ##

To implement the features described above, the following will be done:

- Build epJSON input and output File handlers.
- Document existing HVACTemplate objects and how they are mapped to regular objects in the ExpandObjects process.
- Create HVACTemplate Class hierarchy of objects, using class inheritance and combining common methods wherever meaningful.
- Create testing suite consisting of all HVACTemplate objects to verify outputs.
- Create ExpandObjects file conversion process.
  - Outputs:
    - "\<original-file-name\>.expepJSON" - Expanded epJSON file
    - "\<original-file-name\>_hvac_templates.epJSON" - File containing HVACTemplate objects
    - "\<original-file-name\>_base.epJSON" - Original file without HVACTemplate objects
- Test and refactor code based on findings from above item.
- Create copies of selected HVACTemplate-*.idf files in JSON format and test results against the IDF counterparts.
- Consult with EnergyPlus team on implementation process for new tool.
