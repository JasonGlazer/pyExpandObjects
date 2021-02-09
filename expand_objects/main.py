import argparse

from expand_objects.hvac_template import HVACTemplate


def build_parser():
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
    return parser


def main(args=None):
    parser = build_parser()
    args = parser.parse_args(args)
    hvt = HVACTemplate(
        no_schema=args.no_schema
    )
    print(hvt)
    return


if __name__ == "__main__":
    main()
