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

''' Template driver for generalized data processing '''
import logging

from geoips2.geoips2_utils import find_module_in_geoips2_packages

LOG = logging.getLogger(__name__)


def template_driver(fnames, command_line_args=None):
    ''' Overall template driver.  This handles reading the datafiles,
    determining appropriate sectors based on file time, then calling the appropriate products on each
    sector.

    Parameters:
        fnames (list): list of strings specifying the files on disk to process
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
    final_products = []
    sectorfiles = command_line_args['sectorfiles']
    sectorlist = command_line_args['sectorlist']
    readername = command_line_args['readername']
    if sectorfiles and not isinstance(sectorfiles, list):
        raise TypeError('Must pass list of strings for "sectorfiles" dictionary entry')
    if sectorlist and not isinstance(sectorlist, list):
        raise TypeError('Must pass list of strings for "sectorfiles" dictionary entry')

    reader = find_module_in_geoips2_packages(module_name='readers',
                                             method_name=readername)
    product = find_module_in_geoips2_packages(module_name='products',
                                              method_name='template')
    LOG.info('Running fnames %s for template', fnames)
    xarrays = reader(fnames, metadata_only=False)
    for curr_xarray in xarrays:
        from geoips2.sector_utils.utils import get_area_defs_for_xarray
        area_defs = get_area_defs_for_xarray(curr_xarray, sectorfiles, sectorlist)
    for area_def in area_defs:
        final_products += product(xarrays, area_def)
    return final_products
