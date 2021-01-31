Create HVACTemplate and ExpandObjects Support for epJSON files
================

**John Grando, GARD Analytics**

 - January 28, 2021

## Justification for New Feature ##

The addition of epJSON as an input system along with the IDF file are impacting current workflows which rely on HVACTemplate and other pre-processor features. Similarly, HVACTemplate is useful for learning EnergyPlus, and provides an aid on projects focused on envelope or lighting measures, simplified interfaces, and scripted workflows.  It is important that model files built in the epJSON format have, at a minimum, the same functionality as their equivalents written in IDF format in order to support existing workflows as well as foster future adoption.  The HVACTemplate and ExpandObjects features have proven to be valuable in the previous format, and new implementations of these tools should be developed.  

## E-mail and  Conference Call Conclusions ##

N/A

## Overview ##

In order to achieve greater alignment with other programming initiatives in EnergyPlus, take advantage of the epJSON schema structure, and make use of object-oriented programming methodologies, Python should be the chosen language for this effort.  This updated tool will provide the same deliverable as its predecessor, which is an output file with detailed components that have been mapped from template objects.  However, the epJSON file format will be used for this program.   

## Approach ##

The process for delivering this product will be different in order to better align with Python best practices, and provide greater flexibility.  First, object validation will be built into the core of the program.  Second, the various existing templates will be structured as objects which will allow for natural hierarchies and common attributes to be built in and shared.  As a part of this effort, a mapping diagram will be provided which demonstrates which regular objects are created from specific templates.  Third, a process will be created which translates epJSON files with HVACTemplate objects to epJSON files with only regular objects.  Finally, a rigorous set of tests will created which verify the functionality and robustness of the program.  With these proposed changes, the ExpandObjects process can operate in the EnergyPlus file pre-processing pipeline by reading and writing epJSON files.

## Testing/Validation/Data Sources ##

A duplicated set of HVACTemplate-*.idf in epJSON format will be created and used as the source files for testing.

## Auxiliary Programs Reference Documentation ##

No new text will be added.  As there are no current epJSON references, this effort should not result in any additional text in this document.

## Input Output Reference Documentation ##

No new fields will be added.  As there are no current epJSON references, this effort should not result in any additional text in this document.

## Engineering Reference ##

None

## Example File and Transition Changes ##

A duplicated set of HVACTemplate-*.idf in epJSON format will be created as examples.

## References ##

Related information is provided in GitHub:  https://github.com/NREL/EnergyPlus/issues/6865

Current ExpandObjects code: https://github.com/NREL/EnergyPlus/blob/develop/src/ExpandObjects/epfilter.f90

## Design Document ##

To implement the features described above, the following will be done:

*Work in progress*

For ExpandObjects, the Subcontractor shall document all of its capabilities and operations first. Then, all those operations shall be mapped into JSON field mappings.

- Build epJSON input and output File handlers
- Document existing HVACTemplate objects and how they are mapped to regular objects in the ExpandObjects process
- Create HVACTemplate Class hierarchy of objects, using class inheritance and combinining common methods wherever meaningful
- Create testing suite consisting of all HVACTemplate example files in epJSON format
- Create ExpandObjects file conversion process
- Test and refactor code based on findings from above item
- Consult with EnergyPlus team on implementation items.
