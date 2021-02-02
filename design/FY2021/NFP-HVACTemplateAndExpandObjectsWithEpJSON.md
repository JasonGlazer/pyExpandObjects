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

The process for delivering this product will be different in order to better align with Python best practices and provide greater flexibility.  First, validation methods will be incorporated to ensure valid files are read and created.  An external package that performs json schema validation will be used to verify files throughout the process.  Second, an HVACTemplate class will be created in Python which will keep data attributes and methods together in a central location as well as provide the option of using inheritance with other classes.  This structure allows the program to hold all HVACTemplate objects in list and dictionary format, which can be used to optimize and modify the creation of individual template objects. Third, a process will be created which translates epJSON files with HVACTemplate objects to epJSON files with only regular objects. This step will make use of one-to-many mappings built into the class structure. Finally, a rigorous set of tests will created which verify the functionality and robustness of the program.  With these proposed changes, the ExpandObjects tool will be able to operate in the EnergyPlus file pre-processing pipeline by reading and writing valid epJSON files.  Python's built-in unittest package will be used in conjunction with an external package that monitors the areas of code that have tests verifying their functionality (coverage).  Using these modules, multiple small tests will be created which verify output on the function level.  Additionally, larger tests will be added verifying overall functionality of the tool by verifying the outputs are approximately the same compared to an equivalent IDF file input.  The coverage reports will identify any sections of code that were not tested.

## Testing/Validation/Data Sources ##

A subset of HVACTemplate-*.idf files will be created in epJSON format and used as the source files for testing.

## Auxiliary Programs Reference Documentation ##

*Work in Progress*

A new section will be added in 'Chapter 10 ExpandObjects' which outlines the usage of the python version of ExpandObjects (pyExpandObjects).  The proposed text is:


## Input Output Reference Documentation ##

*Work in Progress*

The current HVACTemplate Processing section (2.1) will be revised to directly address how epJSON files will be handled.  The section will be rewritten as folows:

**Unlike other EnergyPlus objects, the HVACTemplate objects are not handled by EnergyPlus
directly.** Instead, they are preprocessed by a program called ExpandObjects. If you use EP-Launch or
RunEPlus.bat, this preprocessor step is performed automatically using *one of the following sequences, depending on the input file format*:  

**IDF Files**  
1. The preprocessor program, ExpandObjects, reads your IDF file and converts all of the HVACTemplate objects into other EnergyPlus objects.
2. The ExpandObjects program copies the original idf file with the HVACTemplate objects commented
out (i.e., inserts a “!” in front of the object name and its input fields) plus all of the new objects
created in Step 1 and writes a new file which is saved with the extension “expidf”. This “expidf”
file may be used as a standard EnergyPlus IDF file if the extension is changed to idf; however, for
safety’s sake, both filename and extension should be changed.
3. The EnergyPlus simulation proceeds using the expidf file as the input stream.
4. If there are error messages from EnergyPlus, they will refer to the contents of the expidf file. Specific
objects referred to in error messages may exist in the original idf, but they may be objects created by
ExpandObjects and only exist in the expidf. Remember that the expidf will be overwritten everytime
the original idf is run using EP-Launch or RunEPlus.bat  

***epJSON Files***
1. *The preprocessor program, pyExpandObjects, reads your IDF file and converts all of the HVACTemplate objects into other EnergyPlus objects.*
2. *The pyExpandObjects program writes a new file which is saved with the extension “expepJSON”. This “expepJSON”
file may be used as a standard EnergyPlus epJSON file if the extension is changed to epJSON; however, for
safety’s sake, both filename and extension should be changed.  Note, the HVACTemplate objects will be completely removed from the expEPJSON file, so ensure to save a copy of the original file before overwriting!*
3. *The EnergyPlus simulation proceeds using the expepJSON file as the input stream.*
4. **

No new fields will be added.  As there are no current epJSON references, this effort should not result in any additional text in this document.

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
- Test and refactor code based on findings from above item.
- Create copies of selected HVACTemplate-*.idf files in JSON format and test results against the IDF counterparts.
- Consult with EnergyPlus team on implementation process for new tool.
