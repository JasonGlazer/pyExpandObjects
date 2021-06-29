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
        help='Specify output directory.  If not provided, input '
    )
    return parser


def main(args=None):
    hvt = HVACTemplate(
        no_schema=args.no_schema,
        logger_level='DEBUG')
    output = {'outputPreProcessorMessage': ''}
    if isinstance(args.file, str):
        file_suffix_check = args.file.endswith('.epJSON')
    elif isinstance(args.file, (pathlib.PosixPath, pathlib.WindowsPath)):
        file_suffix_check = args.file.suffix == '.epJSON'
    else:
        raise InvalidInputException('Invalid input file reference')  # pragma: no cover - unlikely to be hit
    if file_suffix_check:
        if os.path.exists(args.file):
            hvt.logger.info('Processing %s', args.file)
            # QA skipped since any unanticipated condition should still get caught and returned to user.
            try:
                hvt_output = hvt.run(input_epjson=args.file)
            except:  # noqa: E722
                hvt_output = {'outputPreProcessorMessage': hvt.stream.getvalue()}
            # merge hvac template output to output dictionary
            for output_key, output_val in hvt_output.items():
                if output_key == 'outputPreProcessorMessage':
                    output['outputPreProcessorMessage'] = '\n'.join([
                        output['outputPreProcessorMessage'],
                        hvt_output['outputPreProcessorMessage']])
                else:
                    output[output_key] = output_val
            # get output directory
            if hasattr(args, 'output_directory') and args.output_directory:
                output_directory = args.output_directory
            else:
                output_directory = os.path.dirname(os.path.abspath(args.file))
            # create file names and raise error if modified name is the same as the base name
            input_file_name = os.path.basename(args.file)
            expanded_file_name = input_file_name.replace('.epJSON', '_expanded.epJSON')
            hvac_templates_file_name = input_file_name.replace('.epJSON', '_hvac_templates.epJSON')
            base_file_name = input_file_name.replace('.epJSON', '_base.epJSON')
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
                        output['outputPreProcessorMessage'] = '\n'.join([
                            output['outputPreProcessorMessage'],
                            'Error: Output epJSON schema validation failed. See output files for details.\n',
                            ej.stream.getvalue()])
                with open(os.path.join(output_directory, expanded_file_name), 'w') as expanded_file:
                    json.dump(output['epJSON'], expanded_file, indent=4, sort_keys=True)
                    output_file_dictionary['expanded'] = os.path.join(output_directory, str(expanded_file_name))
            if output.get('epJSON_hvac_templates'):
                with open(os.path.join(output_directory, hvac_templates_file_name), 'w') as hvac_template_file:
                    json.dump(output['epJSON_hvac_templates'], hvac_template_file, indent=4, sort_keys=True)
                    output_file_dictionary['hvac_templates'] = \
                        os.path.join(output_directory, str(hvac_templates_file_name))
            if output.get('epJSON_base'):
                with open(os.path.join(output_directory, base_file_name), 'w') as base_file:
                    json.dump(output['epJSON_base'], base_file, indent=4, sort_keys=True)
                    output_file_dictionary['base'] = os.path.join(output_directory, str(base_file_name))
            if not output_file_dictionary:
                output['outputPreProcessorMessage'] = '\n'.join([
                    output['outputPreProcessorMessage'],
                    'Error: No output files written'])
            else:
                output['outputPreProcessorMessage'] = r'\n'.join([
                    output['outputPreProcessorMessage'],
                    'Output files written: {}'.format(output_file_dictionary)])
            output['output_files'] = output_file_dictionary
        else:
            output['outputPreProcessorMessage'] = r' '.join([
                output['outputPreProcessorMessage'],
                'Error: File does not exist: {}.  File not processed'.format(args.file)])
    else:
        output['outputPreProcessorMessage'] = r' '.join([
            output['outputPreProcessorMessage'],
            'Error: Bad file extension for {}.  File not processed'.format(args.file)])
    return output


if __name__ == "__main__":
    epJSON_parser = build_parser()
    epJSON_args = epJSON_parser.parse_args()
    main(epJSON_args)
    logging.shutdown()
