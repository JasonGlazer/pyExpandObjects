__version__ = "0.0"
__author__ = "John Grando"

# todo_eo: build yaml handling and verification for basic object structure, like compact_schedule
# todo_eo: rewrite epJSON to use descriptors
# todo_eo: future - import pyExpandObjects.  Call function and then get back dictionary with valid epJSON to run
# todo_eo: simulation - environ variables can be set to spit out just the variables, can be used for testing
# todo_eo: should there be an option to make uncontrolled zones (no schedules or constant setpoints provided)
# todo_eo: Add description of Mappings in documentation
# todo_eo: cleanup error checking to look at message output with self.assertRaisesRegex()
# todo_eo: cleanup setUP to only use minimal classes or mocks
# todo_eo: It might make sense to load the YAML objects as classes.  Use _get_structure() as entry point.
