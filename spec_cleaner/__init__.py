#!/usr/bin/env python
# vim: set ts=4 sw=4 et: coding=UTF-8

# Copyright (c) 2013, SUSE LINUX Products GmbH, Nuernberg, Germany
# All rights reserved.
# See COPYING for details.

__version__ = '0.5.9'

import os
import sys
import argparse

from rpmexception import RpmWrongArgs, RpmException
from rpmcleaner import RpmSpecCleaner


def process_args(argv):
    """
    Process the parsed arguments and return the result
    :param argv: passed arguments
    """

    parser = argparse.ArgumentParser(prog='spec-cleaner',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description='Cleans the given spec file according to style guide and returns the result.')

    # Make the -d, -i, and -o exclusive as we can do only one of those
    output_group = parser.add_mutually_exclusive_group()

    parser.add_argument('spec', metavar='SPEC', type=str,
                        help='spec file to beautify')
    output_group.add_argument('-d', '--diff', action='store_true', default=False,
                        help='run the diff program to show differences between new and orginal specfile.')
    parser.add_argument('--diff-prog', default='vimdiff',
                        help='specify the diff binary to call with diff option.')
    parser.add_argument('-f', '--force', action='store_true', default=False,
                        help='overwrite the output file if already exist.')
    output_group.add_argument('-i', '--inline', action='store_true', default=False,
                        help='inline the changes directly to the parsed file.')
    parser.add_argument('-p', '--pkgconfig', action='store_true', default=False,
                        help='convert dependencies to their pkgconfig counterparts, requires bit of cleanup in spec afterwards.')
    output_group.add_argument('-o', '--output', default='',
                        help='specify the output file for the cleaned spec content.')
    parser.add_argument('-v', '--version', action='version', version=__version__,
                        help='show package version and exit')

    # print help if there is no argument
    if len(argv) < 1:
        parser.print_help()
        sys.exit(0)

    options = parser.parse_args(args=argv)

    # the spec must exist for us to do anything
    if not os.path.exists(options.spec):
        raise RpmWrongArgs('{0} does not exist.'.format(options.spec))

    # the path for output must exist and the file must not be there unless
    # force is specified
    if options.output:
        options.output = os.path.expanduser(options.output)
        if not options.force and os.path.exists(options.output):
                raise RpmWrongArgs('{0} already exists.'.format(options.output))

    return options


def main(argv):
    """
    Main function that calls argument parsing ensures their sanity
    and then creates RpmSpecCleaner object that works with passed spec file.
    :param argv: passed arguments
    """

    try:
        options = process_args(argv)
    except RpmWrongArgs as e:
        sys.stderr.write('ERROR: {0}\n'.format(e))
        return 1

    try:
        cleaner = RpmSpecCleaner(options.spec,
                                 options.output,
                                 options.pkgconfig,
                                 options.inline,
                                 options.diff,
                                 options.diff_prog)
        cleaner.run()
    except RpmException as e:
        sys.stderr.write('ERROR: {0}\n'.format(e))
        return 1

    return 0

if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        pass
