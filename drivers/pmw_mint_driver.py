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

''' Workflow for TB imagery (or EDR)  products for all PMW sensors
     1) setup to select a reader depending on the pmw sensor
     2) setup to pass variables for products.

V1.0: for SSMI, NRL-MRY, 5/19/2020
V1.1: add AMSU-B, NRL-MRY, 6/3/2020
'''

import logging

from geoips2.geoips2_utils import find_module_in_geoips2_packages
from geoips2.products.pmw_mint import pmw_mint

LOG = logging.getLogger(__name__)


def pmw_mint_driver(fnames, command_line_args=None):
    ''' Workflow for running PMW brightness temperature products, for all sensors.

    Args:
        fnames (list) : List of strings specifying full paths to input file names to process
        command_line_args (dict) : dictionary of command line arguments
                                     'readername': Explicitly request reader
                                                      geoips2*.readers.readername.readername
                                     Optional: 'sectorfiles': list of YAML sectorfiles
                                               'sectorlist': list of desired sectors found in "sectorfiles"
                                                                tc<YYYY><BASIN><NUM><NAME> for TCs,
                                                                ie tc2020sh16gabekile
                                     If sectorfiles and sectorlist not included, looks in database
    Returns:
        (list) : Return list of strings specifying full paths to output products that were produced
    '''
    # from IPython import embed as shell
    final_products = []

    sectorfiles = command_line_args['sectorfiles']
    sectorlist = command_line_args['sectorlist']
    readername = command_line_args['readername']
    variables = command_line_args['variables']
    if sectorfiles and not isinstance(sectorfiles, list):
        raise TypeError('Must pass list of strings for "sectorfiles" dictionary entry')
    if sectorlist and not isinstance(sectorlist, list):
        raise TypeError('Must pass list of strings for "sectorfiles" dictionary entry')
    if readername and not isinstance(readername, str):
        raise TypeError('Must pass string for "readername" dictionary entry')
    if variables and not isinstance(variables, list):
        raise TypeError('Must pass list of strings for "variables" dictionary entry')

    reader = find_module_in_geoips2_packages(module_name='readers',
                                             method_name=readername)

    for fname in fnames:                      # fnames: name list of input data files
        xobjs = reader(fname, variables=variables)

        from geoips2.sector_utils.utils import get_area_defs_for_xarray
        area_defs = get_area_defs_for_xarray(xobjs[0],
                                             command_line_args['sectorfiles'],
                                             command_line_args['sectorlist'])

        # setup for TC products
        for area_def in area_defs:
            for xobj in xobjs:
                final_products += pmw_mint([xobj], area_def, command_line_args)
    return final_products
