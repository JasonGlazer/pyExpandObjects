import os
from tests.simulations import BaseSimulationTest

base_project_path = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__))))


def main():
    """
    Convert IDF Template files to various formats
    :return: None
    """
    file_directory = os.path.join(base_project_path, 'simulation', 'ExampleFiles')
    template_files = [
        i for i in os.listdir(file_directory)
        if i.startswith('HVACTemplate') and 'expanded' not in i.lower() and i.endswith('.idf')]
    for tf in template_files:
        print('Transforming template file: {}'.format(tf))
        test_file = BaseSimulationTest.convert_file(
            file_location=os.path.join(file_directory, tf),
            working_dir=file_directory)
        print('Converted epJSON template file: {}'.format(test_file))
        expanded_file = BaseSimulationTest.expand_idf(
            file_location=os.path.join(file_directory, tf),
            working_dir=file_directory)
        print('Expanded idf file: {}'.format(expanded_file))
        expanded_epjson_file = BaseSimulationTest.convert_file(
            file_location=os.path.join(file_directory, expanded_file),
            working_dir=file_directory)
        print('Expanded epJSON file: {}'.format(expanded_epjson_file))
    return


if __name__ == "__main__":
    main()
