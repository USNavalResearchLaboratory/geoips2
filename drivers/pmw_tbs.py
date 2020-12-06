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
V1.2: add SSMIS, NRL-MRY, 7/31/2020
V1.3: add GMI, NRL-MRY, 8/5/2020
V1.4: add imerg, NRL-MRY, 8/24/2020
'''

import logging

from geoips2.commandline.args import check_command_line_args
from geoips2.geoips2_utils import find_module_in_geoips2_packages
from geoips2.products.pmw_tb import pmw_tb
from geoips2.filenames.duplicate_files import remove_duplicates

PMW_NUM_PIXELS_X = 1400
PMW_NUM_PIXELS_Y = 1400
PMW_PIXEL_SIZE_X = 1000
PMW_PIXEL_SIZE_Y = 1000

LOG = logging.getLogger(__name__)


def pmw_tbs(fnames, command_line_args=None):
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
    from datetime import datetime
    process_datetimes = {}
    process_datetimes['overall_start'] = datetime.utcnow()
    #from IPython import embed as shell
    final_products = []
    removed_products = []
    saved_products = []

    check_command_line_args(['sectorlist', 'productlist', 'sectorfiles', 'readername'],
                            command_line_args)
    sectorfiles = command_line_args['sectorfiles']
    sectorlist = command_line_args['sectorlist']
    productlist = command_line_args['productlist']
    readername = command_line_args['readername']

    reader = find_module_in_geoips2_packages(module_name='readers',
                                             method_name=readername)

    num_jobs = 0
    xobjs = reader(fnames)
    from geoips2.sector_utils.utils import get_area_defs_for_xarray, filter_area_defs_sector
    from geoips2.products.pmw_tb import VARLIST
    from geoips2.xarray_utils.data import get_sectored_xarrays
    area_defs = get_area_defs_for_xarray(xobjs[0], sectorfiles, sectorlist,
                                         pixel_size_x=PMW_PIXEL_SIZE_X, pixel_size_y=PMW_PIXEL_SIZE_Y,
                                         num_pixels_x=PMW_NUM_PIXELS_X, num_pixels_y=PMW_NUM_PIXELS_Y,
                                         track_type='BEST')
    for xobj in xobjs:
        test_varname = VARLIST[xobj.source_name][0]
        if test_varname in xobj.variables:
            LOG.info('Filtering using variable %s', test_varname)
            area_defs = filter_area_defs_sector(area_defs, xobj,
                                                var_for_coverage=test_varname)
    # setup for TC products
    for area_def in area_defs:
        process_datetimes[area_def.name] = {}
        process_datetimes[area_def.name]['start'] = datetime.utcnow()
        sect_xarrays = get_sectored_xarrays(xobjs, area_def, varlist=VARLIST[xobjs[0].source_name],
                                            get_bg_xarrays=True)
        if sect_xarrays:

            curr_products = pmw_tb(sect_xarrays, area_def, productlist)
            final_products += curr_products

            curr_removed_products, curr_saved_products = remove_duplicates(curr_products,
                                                                           area_def,
                                                                           remove_files=True)
            removed_products += curr_removed_products
            saved_products += curr_saved_products

            process_datetimes[area_def.name]['end'] = datetime.utcnow()
            num_jobs += 1
        else:
            LOG.info('SKIPPING No coverage for %s %s', xobjs[0].source_name, area_def.name)

    process_datetimes['overall_end'] = datetime.utcnow()
    from geoips2.geoips2_utils import output_process_times
    output_process_times(process_datetimes, num_jobs)

    return final_products
