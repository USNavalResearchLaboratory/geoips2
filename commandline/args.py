# # # DISTRIBUTION STATEMENT A. Approved for public release: distribution unlimited. # # #
# # #  # # #
# # # Author: # # #
# # # Naval Research Laboratory, Marine Meteorology Division # # #
# # #  # # #
# # # This program is free software: you can redistribute it and/or modify it under # # #
# # # the terms of the NRLMMD License included with this program.  If you did not # # #
# # # receive the license, see http://www.nrlmry.navy.mil/geoips for more # # #
# # # information. # # #
# # #  # # #
# # # This program is distributed WITHOUT ANY WARRANTY; without even the implied # # #
# # # warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the # # #
# # # included license for more details. # # #

#!/bin/env python
''' Command line script for kicking off geoips2 based drivers'''

import logging
LOG = logging.getLogger(__name__)


def check_command_line_args(arglist, argdict):
    ''' Check formatting of command line arguments

    Args:
        arglist (list) : List of desired command line arguments to check within argdict for appropriate formatting
        argdict (dict) : Dictionary of command line arguments

    Returns:
        (bool) : Return True if all arguments are of appropriate formatting.

    Raises:
        (TypeError) : Incorrect command line formatting
    '''
    if 'sectorfiles' in arglist:
        if argdict['sectorfiles'] and not isinstance(argdict['sectorfiles'], list):
            raise TypeError('Must pass list of strings for "sectorfiles" dictionary entry')
        LOG.info('COMMANDLINEARG sectorfiles: %s', argdict['sectorfiles'])
    if 'sectorlist' in arglist:
        if argdict['sectorlist'] and not isinstance(argdict['sectorlist'], list):
            raise TypeError('Must pass list of strings for "sectorfiles" dictionary entry')
        LOG.info('COMMANDLINEARG sectorlist: %s', argdict['sectorlist'])
    if 'productlist' in arglist:
        if argdict['productlist'] and not isinstance(argdict['productlist'], list):
            raise TypeError('Must pass list of strings for "productlist" dictionary entry')
        LOG.info('COMMANDLINEARG productlist: %s', argdict['productlist'])
    if 'product_options' in arglist:
        if argdict['product_options'] and not isinstance(argdict['product_options'], str):
            raise TypeError('Must pass string for "product_options" dictionary entry')
        LOG.info('COMMANDLINEARG product_options: %s', argdict['product_options'])
    if 'readername' in arglist:
        if argdict['readername'] and not isinstance(argdict['readername'], str):
            raise TypeError('Must pass string for "readername" dictionary entry')
        LOG.info('COMMANDLINEARG readername: %s', argdict['readername'])
    if 'variables' in arglist:
        if argdict['variables'] and not isinstance(argdict['variables'], list):
            raise TypeError('Must pass list of strings for "variables" dictionary entry')
        LOG.info('COMMANDLINEARG variables: %s', argdict['variables'])

    return True


def get_command_line_args(arglist=None, description=None):
    ''' Parse command line arguments specified by the requested list of arguments

    Args:
        arglist (:obj:`list`, optional) : DEFAULT None.
                                            list of requested arguments to add to the ArgumentParser
                                            if None, include all arguments
        description (:obj:`str`, optional) : DEFAULT None. String description of arguments
    Returns:
        (dict) : Dictionary of command line arguments
    '''
    import argparse
    parser = argparse.ArgumentParser(description=description)
    add_args(parser, arglist)
    return parser.parse_args()


def add_args(parser, arglist=None):
    ''' List of available standard arguments for calling data file processing command line.

    Args:
        parser (ArgumentParser) : argparse ArgumentParser to add appropriate arguments
        arglist (:obj:`list`, optional) : DEFAULT None
                    list of requested arguments to add to the ArgumentParser
                    if None, include all arguments

    Returns:
        No return values (parser modified in place)
    '''

    from os.path import abspath
    if arglist is None or 'filenames' in arglist:
        parser.add_argument('filenames', nargs='*', default=None, type=abspath,
                            help='''Fully qualified paths to data files to be processed.''')
    if arglist is None or 'sectorlist' in arglist:
        parser.add_argument('-s', '--sectorlist', nargs='*', default=None,
                            help='''A list of short sector names over which the data file should be processed.''')
    if arglist is None or 'productlist' in arglist:
        parser.add_argument('-p', '--productlist', nargs='*', default=None,
                            help='''A list of products to generate.''')
    if arglist is None or 'variables' in arglist:
        parser.add_argument('-v', '--variables', nargs='*', default=None,
                            help='''A list of variables to include in the data read.  If this argument is not included,
                                    read all available variables. These should be GeoIPS variable names, not original
                                    datafile variable names.''')
    if arglist is None or 'include_product_substrings' in arglist:
        parser.add_argument('--include_product_substrings', nargs='*', default=None,
                            help='''A list of substrings to INCLUDE in the list of products to run.  This allows you
                                    to turn on an entire "class" of products.''')
    if arglist is None or 'exclude_product_substrings' in arglist:
        parser.add_argument('--exclude_product_substrings', nargs='*', default=None,
                            help='''A list of substrings to EXCLUDE from the list of products to run.  This allows you
                                    to turn off an entire "class" of products. exclude trumps include''')
    if arglist is None or 'sectorfiles' in arglist:
        parser.add_argument('--sectorfiles', nargs='*', default=None,
                            help='''Specify YAML sectorfiles''')
    if arglist is None or 'comparepaths' in arglist:
        parser.add_argument('--comparepaths', nargs='*', default=None,
                            help='''Specify full paths to directories containing output products to compare with
                                    current outputs.''')
    if arglist is None or 'product_options' in arglist:
        parser.add_argument('--product_options', nargs='?', default=None,
                            help='''Specify product specific options (these must be parsed within the
                                    individual product scripts)''')
    if arglist is None or 'driver' in arglist:
        parser.add_argument('--driver', default=None,
                            help='''Specify driver that should be followed for this file. ''')
    if arglist is None or 'readername' in arglist:
        parser.add_argument('--readername', default=None,
                            help='''If --readername is passed, the specific reader will be located in
                                    geoips2*.readers.myreadername.myreadername,
                                    The readername string should be the reader module name (no .py)''')
    if arglist is None or 'bgreadername' in arglist:
        parser.add_argument('--bgreadername', default=None,
                            help='''If --bgreadername is passed, the specific reader will be located in
                                    geoips2*.readers.myreadername.myreadername,
                                    The bgreadername string should be the reader module name (no .py)''')
    if arglist is None or 'bgfnames' in arglist:
        parser.add_argument('--bgfnames', nargs='*', default=None,
                            help='''Specify filenames to use for background imagery''')
