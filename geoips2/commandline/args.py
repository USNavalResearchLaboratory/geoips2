# # # DISTRIBUTION STATEMENT A. Approved for public release: distribution unlimited.
# # # 
# # # Author:
# # # Naval Research Laboratory, Marine Meteorology Division
# # # 
# # # This program is free software: you can redistribute it and/or modify it under
# # # the terms of the NRLMMD License included with this program.  If you did not
# # # receive the license, see http://www.nrlmry.navy.mil/geoips for more
# # # information.
# # # 
# # # This program is distributed WITHOUT ANY WARRANTY; without even the implied
# # # warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# # # included license for more details.

#!/bin/env python
''' Command line script for kicking off geoips2 based procflows'''

import logging
from os.path import abspath, exists
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
    if arglist is None:
        return True
    if 'filenames' in arglist:
        if argdict['filenames'] and not isinstance(argdict['filenames'], list):
            raise TypeError('Must pass list of strings for "filenames" dictionary entry')
        for fname in argdict['filenames']:
            if not exists(fname):
                raise IOError(f'Filename {fname} does not exist - all requested files must exist on disk')
        LOG.info('COMMANDLINEARG filenames: %s', argdict['filenames'])
    if 'sectorfiles' in arglist:
        if argdict['sectorfiles'] and not isinstance(argdict['sectorfiles'], list):
            raise TypeError('Must pass list of strings for "sectorfiles" dictionary entry')
        LOG.info('COMMANDLINEARG sectorfiles: %s', argdict['sectorfiles'])
    if 'sector_list' in arglist:
        if argdict['sector_list'] and not isinstance(argdict['sector_list'], list):
            raise TypeError('Must pass list of strings for "sectorfiles" dictionary entry')
        LOG.info('COMMANDLINEARG sector_list: %s', argdict['sector_list'])
    if 'tcdb_sector_list' in arglist:
        if argdict['tcdb_sector_list'] and not isinstance(argdict['tcdb_sector_list'], list):
            raise TypeError('Must pass list of strings for "tcdb_sector_list" dictionary entry')
        LOG.info('COMMANDLINEARG tcdb_sector_list: %s', argdict['tcdb_sector_list'])
    if 'tcdb' in arglist:
        if argdict['tcdb'] not in [True, False]:
            raise TypeError('tcdb dictionary entry must be bool (True or False)')
        LOG.info('COMMANDLINEARG tcdb: %s', argdict['tcdb'])
    if 'product_name' in arglist:
        if argdict['product_name'] and not isinstance(argdict['product_name'], str):
            raise TypeError('Must pass a single string for "product_name" dictionary entry')
        LOG.info('COMMANDLINEARG product_name: %s', argdict['product_name'])
    if 'product_options' in arglist:
        if argdict['product_options'] and not isinstance(argdict['product_options'], str):
            raise TypeError('Must pass string for "product_options" dictionary entry')
        LOG.info('COMMANDLINEARG product_options: %s', argdict['product_options'])
    if 'reader_name' in arglist:
        if argdict['reader_name'] and not isinstance(argdict['reader_name'], str):
            raise TypeError('Must pass string for "reader_name" dictionary entry')
        LOG.info('COMMANDLINEARG reader_name: %s', argdict['reader_name'])
    if 'output_config' in arglist:
        if argdict['output_config'] and not isinstance(argdict['output_config'], str):
            raise TypeError('Must pass a single string for "output_config" dictionary entry')
        LOG.info('COMMANDLINEARG output_config: %s', argdict['output_config'])
    if 'adjust_area_def' in arglist:
        if argdict['adjust_area_def'] and not isinstance(argdict['adjust_area_def'], str):
            raise TypeError('Must pass a single string for "adjust_area_def" dictionary entry')
        LOG.info('COMMANDLINEARG adjust_area_def: %s', argdict['adjust_area_def'])
    if 'reader_defined_area_def' in arglist:
        if argdict['reader_defined_area_def'] and not isinstance(argdict['reader_defined_area_def'], str):
            raise TypeError('Must pass a single string for "reader_defined_area_def" dictionary entry')
        LOG.info('COMMANDLINEARG reader_defined_area_def: %s', argdict['reader_defined_area_def'])

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
    argdict = parser.parse_args()
    check_command_line_args(['filenames', 'procflow'], argdict.__dict__)
    return argdict


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

    if arglist is None or 'filenames' in arglist:
        parser.add_argument('filenames', nargs='*', default=None, type=abspath,
                            help='''Fully qualified paths to data files to be processed.''')

    sect_group = parser.add_argument_group(title='Sector Requests: General arguments for sectors')
    if arglist is None or 'adjust_area_def' in arglist:
        sect_group.add_argument('--adjust_area_def', nargs='?', default=None,
                                help='''Specify area def adjuster to be used within processing, located in:
                                          <package>.interface_modules.area_def_adjusters.<myadjuster>.<myadjuster>''')

    tc_group = parser.add_argument_group(title='Sector Requests: General arguments for TC sectors')
    if arglist is None or 'tc_template_yaml' in arglist:
        tc_group.add_argument('--tc_template_yaml', nargs='?', default=None,
                                help='''YAML template for creating appropriate TC sector shape/resolution from
                                        current storm location''')


    trackfile_group = parser.add_argument_group(title='Sector Requests: TC trackfile-based sectors')
    if arglist is None or 'trackfiles' in arglist:
        trackfile_group.add_argument('--trackfiles', nargs='*', default=None,
                                     help='''Specify TC trackfiles to include in processing
                                             If --trackfile_sector_list is included, limit to the storms in list
                                             If --trackfile_sector_list is not included, process all storms''')
    if arglist is None or 'trackfile_parser' in arglist:
        trackfile_group.add_argument('--trackfile_parser', nargs='?', default=None,
                                     help='''Specify TC trackfile parser to use with trackfiles, located in:
                                                geoips2*.interface_modules.trackfile_parsers.myparsername.myparsername,
                                                The trackfile_parser string should be the parser module
                                                name (no .py)''')
    if arglist is None or 'trackfile_sector_list' in arglist:
        trackfile_group.add_argument('--trackfile_sector_list', nargs='*', default=None,
                                     help='''A list of sector names found specified trackfiles to include in processing.
                                             Of format: tc2020io01amphan''')

    tcdb_group = parser.add_argument_group(title='Sector Requests: TC tracks database')
    if arglist is None or 'tcdb_sector_list' in arglist:
        tcdb_group.add_argument('--tcdb_sector_list', nargs='*', default=None,
                                help='''A list of sector names found in tc database to include in processing.
                                         Of format: tc2020io01amphan''')
    if arglist is None or 'tcdb' in arglist:
        tcdb_group.add_argument('--tcdb', action='store_true',
                                help='''Call with --tcdb to include the matching TC database sectors within processing
                                         If --tcdb_sector_list is also included, limit the storms to those in list
                                         If --tcdb_sector_list is not included, process all matching storms.''')

    static_group = parser.add_argument_group(title='Sector Requests: Static YAML sectorfiles')
    if arglist is None or 'reader_defined_area_def' in arglist:
        static_group.add_argument('--reader_defined_area_def', nargs='?', default=None,
                                     help='''Specify to use only area_definition defined within the reader
                                                This option supercedes all other sector-specifying options.''')
    if arglist is None or 'sectorfiles' in arglist:
        static_group.add_argument('--sectorfiles', nargs='*', default=None,
                                help='''Specify YAML sectorfiles''')
    if arglist is None or 'sector_list' in arglist:
        static_group.add_argument('-s', '--sector_list', nargs='*', default=None,
                                help='''A list of short sector names found within YAML sectorfiles over which the
                                         data file should be processed.''')

    prod_group = parser.add_argument_group(title='Product specification options')
    if arglist is None or 'product_name' in arglist:
        prod_group.add_argument('--product_name', nargs='?', default=None,
                            help='''Name of product to produce.''')
    if arglist is None or 'product_options' in arglist:
        prod_group.add_argument('--product_options', nargs='?', default=None,
                                help='''Specify product specific options (these must be parsed within the
                                         individual product scripts)''')


    comp_group = parser.add_argument_group(title='Options for specifying output comparison')
    if arglist is None or 'compare_paths' in arglist:
        comp_group.add_argument('--compare_paths', nargs='*', default=None,
                            help='''Specify full paths to directories containing output products to compare with
                                    current outputs.''')

    if arglist is None or 'compare_outputs_module' in arglist:
        comp_group.add_argument('--compare_outputs_module', nargs='?', default='compare_outputs',
                            help='''Specify module to use for comparing outputs.  Defaults to geoips2.compare_outputs
                                    internally if not specified.''')

    procflow_group = parser.add_argument_group(title='Processing workflow specifications')
    if arglist is None or 'procflow' in arglist:
        procflow_group.add_argument('--procflow', default=None,
                                  help='''Specify procflow that should be followed for this file, located in:
                                          geoips2*.interface_modules.procflows.myprocflowname.myprocflowname,
                                          The procflow string should be the procflow module name (no .py)''')
    if arglist is None or 'filename_format' in arglist:
        procflow_group.add_argument('--filename_format', nargs='?', default='geoips_fname',
                                  help='''Specify filename format module_name that should be used for this file, where
                                          Each filename_module_name is 'myfilemodule' where 
                                              from geoips2*.filenames.myfilemodule import myfilemodule
                                          would be the appropriate import statement''')
    if arglist is None or 'output_format' in arglist:
        procflow_group.add_argument('--output_format', nargs='?', default='imagery_annotated',
                                  help='''Specify output format module_name that should be used for this file,
                                          each output_format is 'output_formats.imagery_annotated' where
                                              from geoips2*.output_formats.imagery_annotated import imagery_annotated
                                          would be the appropriate import statement''')
    if arglist is None or 'output_config' in arglist:
        procflow_group.add_argument('--output_config', nargs='?', default=None,
                                  help='''Specify YAML config file holding output modile names and 
                                          their respective filename modules''')

    rdr_group = parser.add_argument_group(title='Data reader specifications')

    if arglist is None or 'reader_name' in arglist:
        rdr_group.add_argument('--reader_name', default=None,
                               help='''If --reader_name is passed, the specific reader will be located in
                                       geoips2*.readers.myreader_name.myreader_name,
                                       The reader_name string should be the reader module name (no .py)''')

    if arglist is None or 'bg_product_name' in arglist:
        rdr_group.add_argument('--bg_product_name', default=None,
                               help='''Product to use for background imagery''')
    if arglist is None or 'bg_reader_name' in arglist:
        rdr_group.add_argument('--bg_reader_name', default=None,
                               help='''If --bg_reader_name is passed, the specific reader will be located in
                                    geoips2*.readers.myreader_name.myreader_name,
                                    The bg_reader_name string should be the reader module name (no .py)''')
    if arglist is None or 'bg_fnames' in arglist:
        rdr_group.add_argument('--bg_fnames', nargs='*', default=None,
                               help='''Specify filenames to use for background imagery.
                                    If --bg_reader_name included, use specific reader for reading background
                                    datafiles.''')

    plt_group = parser.add_argument_group(title='Plotting parameter specifications')
    if arglist is None or 'gridlines_params' in arglist:
        plt_group.add_argument('--gridlines_params', default=None,
                               help='''If --gridlines_params is passed, the specific gridline params will be located in
                                    geoips2*.image_utils.plotting_params.gridlines.gridlines_params,
                                    The gridlines_params string should be the base gridline name (no .yaml)''')
    if arglist is None or 'boundaries_params' in arglist:
        plt_group.add_argument('--boundaries_params', default=None,
                               help='''If --boundaries_params is passed, the specific boundary params will be located in
                                    geoips2*.image_utils.plotting_params.boundaries.<boundaries_params>,
                                    The boundaries_params string should be the base boundaries name (no .yaml)''')

    if arglist is None or 'model_reader_name' in arglist:
        rdr_group.add_argument('--model_reader_name', default=None,
                               help='''If --model_reader_name is passed, the specific reader will be located in
                                    geoips2*.readers.my_reader_name.my_reader_name,
                                    The model_reader_name string should be the reader module name (no .py)''')
    if arglist is None or 'model_fnames' in arglist:
        rdr_group.add_argument('--model_fnames', nargs='*', default=None,
                               help='''Specify filenames to use for NWP model data.
                                    If --model_reader_name included, use specific reader for reading model
                                    datafiles.''')
    if arglist is None or 'buoy_reader_name' in arglist:
        rdr_group.add_argument('--buoy_reader_name', default=None,
                               help='''If --buoy_reader_name is passed, the specific reader will be located in
                                    geoips2*.readers.my_reader_name.my_reader_name,
                                    The buoyreadername string should be the reader module name (no .py)''')
    if arglist is None or 'buoy_fnames' in arglist:
        rdr_group.add_argument('--buoy_fnames', nargs='*', default=None,
                               help='''Specify filenames to use for buoy data.
                                    If --buoy_reader_name included, use specific reader for reading buoy
                                    datafiles.''')
        
    fusion_group = parser.add_argument_group(title='Options for specifying fusion products')
    if arglist is None or 'fuse_files' in arglist:
        fusion_group.add_argument('--fuse_files', action='append', nargs='+', default=None,
                                  help='''Provide additional files required for fusion product. Files passed under 
                                       this flag MUST be from the same source. fuse_files may be passed multiple times.
                                       Reader name for these files is specified with the fuse_reader flag.''')
        fusion_group.add_argument('--fuse_reader', action='append', default=None,
                                  help='''Provide the reader name for files passed under the fuse_files flag.
                                       Only provide one reader to this flag. If multiple fuse_files flags are passed,
                                       the same number of fuse_readers must be passed in the same order.''')
        fusion_group.add_argument('--fuse_product', action='append', default=None,
                                  help='''Provide the product name for files passed under the fuse_files flag.
                                       Only provide one product to this flag. If multiple fuse_files flags are passed,
                                       the same number of fuse_products must be passed in the same order.''')
