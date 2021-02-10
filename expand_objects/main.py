import argparse
import os
from expand_objects.hvac_template import HVACTemplate


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
        "files",
        nargs='+',
        help='Paths of epJSON files to convert'
    )
    return parser


def main(args=None):
    hvt = HVACTemplate(
        no_schema=args.no_schema
    )
    for f in args.files:
        output_epjson = None
        if f.endswith('.epJSON'):
            if os.path.exists(f):
                hvt.logger.info('Proceessing %s', f)
                output_epjson = hvt.run(input_epjson=f)
            else:
                hvt.logger.warning('File does not exist: %s. file not processed', f)
        else:
            hvt.logger.warning('Bad file extension for %s.  File not processed', f)
    return output_epjson


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    main(args)
