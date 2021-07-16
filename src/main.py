import argparse
import os
import pathlib

from hvac_template import HVACTemplate
from epjson_handler import EPJSON
import logging
import json

from custom_exceptions import InvalidInputException


def build_parser():  # pragma: no cover
    """
    Build argument parser.
    """
    parser = argparse.ArgumentParser(
        prog='pyExpandObjects',
        description='Automated process that expands HVACTemplate objects into regular EnergyPlus objects.')
    parser.add_argument(
        '--no-schema',
        '-ns',
        action='store_true',
        help='Skip schema validations')
    parser.add_argument(
        "--file",
        '-f',
        nargs='?',
        help='Path of epJSON file to convert'
    )
    parser.add_argument(
        '--output_directory',
        '-o',
        nargs='?',
        help='Specify output directory.  If not provided, then input file directory is used'
    )
    parser.add_argument(
        '--no_backup',
        '-nb',
        action='store_true',
        help='Prevent backup files from being written'
    )
    parser.add_argument(
        '--logger_level',
        '-l',
        nargs='?',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='WARNING',
        help='Specify logger level.'
    )
    return parser


def output_preprocessor_message_formatter(output_stream):
    messages = {}
    for line in output_stream.split('\n'):
        counter = len(messages.keys()) + 1
        messages.update({
            'Output:PreprocessorMessage {}'.format(str(counter)): {
                'preprocessor_name': 'pyExpandObjects'
            }
        })
        if line.startswith('Error:'):
            messages['Output:PreprocessorMessage {}'.format(str(counter))]['error_severity'] = 'Error'
        elif line.startswith('Warning:'):
            messages['Output:PreprocessorMessage {}'.format(str(counter))]['error_severity'] = 'Warning'
        else:
            messages['Output:PreprocessorMessage {}'.format(str(counter))]['error_severity'] = 'Information'
        words = line.split()
        word_groups = [words[i:i + 10] for i in range(0, len(words), 10)]
        word_group_counter = 1
        for wg in word_groups:
            messages['Output:PreprocessorMessage {}'.format(str(counter))][
                'message_line_{}'.format(word_group_counter)] = ' '.join(wg)
            word_group_counter += 1
        if not messages['Output:PreprocessorMessage {}'.format(str(counter))].get('message_line_1'):
            messages.pop('Output:PreprocessorMessage {}'.format(str(counter)))
    return messages


def main(args=None):
    # set the arg defaults for testing when Namespace is used
    if not hasattr(args, 'logger_level'):
        args.logger_level = 'WARNING'
    if not hasattr(args, 'no_backup'):
        args.no_backup = False
    if not hasattr(args, 'no_schema'):
        args.no_schema = False
    hvt = HVACTemplate(
        no_schema=args.no_schema,
        logger_level=args.logger_level)
    if isinstance(args.file, str):
        file_suffix_check = args.file.endswith('.epJSON')
    elif isinstance(args.file, (pathlib.PosixPath, pathlib.WindowsPath)):
        file_suffix_check = args.file.suffix == '.epJSON'
    else:
        raise InvalidInputException('Invalid input file reference')  # pragma: no cover - unlikely to be hit
    output = {}
    raw_output = {'Output:PreprocessorMessage': ''}
    if file_suffix_check:
        if os.path.exists(args.file):
            hvt.logger.info('Processing %s', args.file)
            # QA skipped since any unanticipated condition should still get caught and returned to user.
            try:
                output = hvt.run(input_epjson=args.file)
                output['Output:PreprocessorMessage'] = hvt.stream.getvalue()
            except:  # noqa: E722
                output = {'Output:PreprocessorMessage': hvt.stream.getvalue()}
            raw_output['Output:PreprocessorMessage'] = output['Output:PreprocessorMessage']
            # merge hvac template output to output dictionary
            # for output_key, output_val in hvt_output.items():
            #     if output_key == 'Output:PreprocessorMessage':
            #         output['Output:PreprocessorMessage'] = '\n'.join([
            #             output['Output:PreprocessorMessage'],
            #             hvt_output['Output:PreprocessorMessage']])
            #     else:
            #         output[output_key] = output_val
            # get output directory
            if hasattr(args, 'output_directory') and args.output_directory:
                output_directory = args.output_directory
            else:
                output_directory = os.path.dirname(os.path.abspath(args.file))
            # create file names and raise error if modified name is the same as the base name
            input_file_name = os.path.basename(args.file)
            expanded_file_name = input_file_name.replace('.epJSON', '_expanded.epJSON')
            hvac_templates_file_name = input_file_name.replace('.epJSON', '_hvac_templates.epJSON') \
                if not args.no_backup else None
            base_file_name = input_file_name.replace('.epJSON', '_base.epJSON') \
                if not args.no_backup else None
            # check that file names are not the same as the original
            if input_file_name in [expanded_file_name, hvac_templates_file_name, base_file_name]:
                raise InvalidInputException('file could not be renamed')  # pragma: no cover - unlikely to be hit
            # write output and keep list of written files
            output_file_dictionary = {}
            if output.get('epJSON'):
                # verify expanded epJSON is valid if schema validation is turned on.
                if not args.no_schema:
                    ej = EPJSON(no_schema=False)
                    try:
                        ej.epjson_process(epjson_ref=output['epJSON'])
                    except:  # noqa: E722
                        output['Output:PreprocessorMessage'] = '\n'.join([
                            output['Output:PreprocessorMessage'],
                            'Error: Output epJSON schema validation failed. See output files for details.\n',
                            ej.stream.getvalue()])
                raw_output['Output:PreprocessorMessage'] = output['Output:PreprocessorMessage']
                output['epJSON']['Output:PreprocessorMessage'] = \
                    output_preprocessor_message_formatter(output['Output:PreprocessorMessage'])
                with open(os.path.join(output_directory, expanded_file_name), 'w') as expanded_file:
                    json.dump(output['epJSON'], expanded_file, indent=4, sort_keys=True)
                    output_file_dictionary['expanded'] = os.path.join(output_directory, str(expanded_file_name))
            if not args.no_backup and output.get('epJSON_hvac_templates'):
                with open(os.path.join(output_directory, hvac_templates_file_name), 'w') as hvac_template_file:
                    json.dump(output['epJSON_hvac_templates'], hvac_template_file, indent=4, sort_keys=True)
                    output_file_dictionary['hvac_templates'] = \
                        os.path.join(output_directory, str(hvac_templates_file_name))
            if not args.no_backup and output.get('epJSON_base'):
                with open(os.path.join(output_directory, base_file_name), 'w') as base_file:
                    json.dump(output['epJSON_base'], base_file, indent=4, sort_keys=True)
                    output_file_dictionary['base'] = os.path.join(output_directory, str(base_file_name))
            if not output_file_dictionary:
                raw_output['Output:PreprocessorMessage'] = '\n'.join([
                    raw_output['Output:PreprocessorMessage'],
                    'Error: No output files written'])
            else:
                raw_output['Output:PreprocessorMessage'] = r'\n'.join([
                    raw_output['Output:PreprocessorMessage'],
                    'Output files written: {}'.format(output_file_dictionary)])
            output['output_files'] = output_file_dictionary
        else:
            raw_output['Output:PreprocessorMessage'] = r'\n'.join([
                raw_output['Output:PreprocessorMessage'],
                'Error: File does not exist: {}.  File not processed'.format(args.file)])
    else:
        raw_output['Output:PreprocessorMessage'] = r'\n'.join([
            raw_output['Output:PreprocessorMessage'],
            'Error: Bad file extension for {}.  File not processed'.format(args.file)])
    output.update({'Output:PreprocessorMessage': raw_output['Output:PreprocessorMessage']})
    return output


if __name__ == "__main__":
    epJSON_parser = build_parser()
    epJSON_args = epJSON_parser.parse_args()
    main(epJSON_args)
    logging.shutdown()
