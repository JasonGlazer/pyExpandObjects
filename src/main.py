import argparse
import os
from hvac_template import HVACTemplate
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
        action='store_false',
        help='Skip schema validations')
    parser.add_argument(
        "--file",
        nargs='?',
        help='Path of epJSON file to convert'
    )
    parser.add_argument(
        '--output_directory',
        '-o',
        nargs='?',
        help='Specify output directory'
    )
    return parser


def main(args=None):
    hvt = HVACTemplate(
        no_schema=args.no_schema
    )
    output = {'outputPreProcessorMessage': ''}
    if args.file.endswith('.epJSON'):
        if os.path.exists(args.file):
            hvt.logger.info('Proceessing %s', args.file)
            hvt_output = hvt.run(input_epjson=args.file)
            # merge hvac template output to output dictionary
            if hvt_output.get('outputPreProcessorMessage'):
                output['outputPreProcessorMessage'] = r' '.join([
                    output['outputPreProcessorMessage'],
                    hvt_output['outputPreProcessorMessage']])
                # get output directory
                if hasattr(args, 'output_directory'):
                    output_directory = args.output_directory
                else:
                    output_directory = os.path.dirname(os.path.abspath(args.file))
                # create file names and raise error if modified name is the same as the base name
                input_file_name = os.path.basename(args.file)
                expanded_file_name = input_file_name.replace('.epJSON', '_expanded.epJSON')
                hvac_templates_file_name = input_file_name.replace('.epJSON', '_hvac_templates.epJSON')
                base_file_name = input_file_name.replace('.epJSON', '_base.epJSON')
                if input_file_name in [expanded_file_name, hvac_templates_file_name, base_file_name]:
                    raise InvalidInputException('file could not be renamed')
                with open(os.path.join(output_directory, expanded_file_name), 'w') as expanded_file:
                    json.dump(hvt_output['epJSON'], expanded_file, indent=4, sort_keys=True)
                with open(os.path.join(output_directory, hvac_templates_file_name), 'w') as hvac_template_file:
                    json.dump(hvt_output['epJSON_hvac_templates'], hvac_template_file, indent=4, sort_keys=True)
                with open(os.path.join(output_directory, base_file_name), 'w') as base_file:
                    json.dump(hvt_output['epJSON_base'], base_file, indent=4, sort_keys=True)
        else:
            hvt.logger.error('File does not exist: %s. file not processed', args.file)
            output['outputPreProcessorMessage'] = r' '.join([
                output['outputPreProcessorMessage'],
                'Error: File does not exist: {}.  File not processed'.format(args.file)])
    else:
        hvt.logger.error('Bad file extension for %s.  File not processed', args.file)
        output['outputPreProcessorMessage'] = r' '.join([
            output['outputPreProcessorMessage'],
            'Error: Bad file extension for {}.  File not processed'.format(args.file)])
    return output


if __name__ == "__main__":
    epJSON_parser = build_parser()
    epJSON_args = epJSON_parser.parse_args()
    main(epJSON_args)
    logging.shutdown()
