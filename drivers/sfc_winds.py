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

''' Workflow for surface winds data processing '''
import logging
from datetime import datetime, timedelta

from geoips2.commandline.args import check_command_line_args
from geoips2.products.windspeed import windspeed
from geoips2.products.template import template
from geoips2.filenames.duplicate_files import remove_duplicates

WSPD_NUM_PIXELS_X = 1400
WSPD_NUM_PIXELS_Y = 1400
WSPD_PIXEL_SIZE_X = 1000
WSPD_PIXEL_SIZE_Y = 1000

LOG = logging.getLogger(__name__)


def write_full_text_file(wind_xarray, first=True, creation_time=None):
    ''' Write out the full text wind file from the data stored in wind_xarray '''
    output_products = []

    # Default to append to existing datafile
    overwrite = False
    append = True

    if hasattr(wind_xarray, 'full_day_file') and wind_xarray.full_day_file:
        # SMAP and WindSat data files get appended to, so just replace the text file with the current version
        # If we are doing multiple SMAP arrays in the same run, must append after the first array
        overwrite = bool(first)
        append = not bool(first)

    # If other than standard appending text files, set directly in reader.  Ie, AMSR is one text file per data file
    # (too big to append a full day of data)
    if hasattr(wind_xarray, 'append_text_file'):
        append = wind_xarray.append_text_file
    if hasattr(wind_xarray, 'overwrite_text_file'):
        overwrite = wind_xarray.overwrite_text_file

    runtextwind = True

    if wind_xarray.source_name == 'ascat' and wind_xarray.sample_distance_km < 20:
        LOG.info('SKIPPING ONLY PRODUCING TEXT FILE FOR 25km ASCAT, this is %skm resolution',
                 wind_xarray.sample_distance_km)
        runtextwind = False
    if runtextwind:
        from geoips2.xarray_utils.outputs import output_windspeed_text
        curr_output_products = output_windspeed_text(wind_xarray, overwrite=overwrite, append=append)
        output_products += curr_output_products

        # Produce an extra text file with the creation time included in the filename
        if wind_xarray.source_name in ['smap-spd', 'smos-spd']:
            curr_output_products = output_windspeed_text(wind_xarray, overwrite=overwrite, append=append,
                                                         creation_time=creation_time)
            output_products += curr_output_products

    return output_products


def run_sector(wind_xarray, area_def):
    from geoips2.sector_utils.utils import is_sector_type
    # if hasattr(wind_xarray, 'storms_with_coverage') and is_sector_type(area_def, 'atcf'):
    #     if area_def.sector_info['storm_name'].lower() not in wind_xarray.storms_with_coverage:
    #         LOG.info('SKIPPING xarray object expects storms "%s", not running storm "%s"',
    #                  wind_xarray.storms_with_coverage, area_def.sector_info['storm_name'].lower())
    #         return False

    # if hasattr(wind_xarray, 'expected_synoptic_time') and is_sector_type(area_def, 'atcf'):
    #     if area_def.sector_start_datetime != wind_xarray.expected_synoptic_time:
    #         LOG.info('SKIPPING xarray object expects synoptic time %s, not running synoptic time %s',
    #                  wind_xarray.expected_synoptic_time, area_def.sector_info['synoptic_time'])
    #         return False

    return True


def sfc_winds(fnames, command_line_args=None):
    ''' Overall driver for all surface winds products.  This handles reading the datafiles, writing out the full
    text file, determining appropriate sectors based on file time, then calling the windspeed product on each
    sector.

    Parameters:
        fnames (list): list of strings specifying the files on disk to process
        command_line_args (dict) : dictionary of command line arguments
                                     * Optional: 
                                               * 'product_options': 'notextwinds' - disable outputing text wind file
                                               * 'sectorfiles': list of YAML sectorfiles
                                               * 'sectorlist': list of desired sectors found in "sectorfiles"
                                                                tc<YYYY><BASIN><NUM><NAME> for TCs,
                                                                ie tc2020sh16gabekile
                                     * If sectorfiles and sectorlist not included, looks in database

    Returns:
        list: List of strings containing successfully produced products

    '''
    process_datetimes = {}
    process_datetimes['overall_start'] = datetime.utcnow()
    output_products = []
    removed_products = []
    saved_products = []
    creation_time = datetime.utcnow()
    LOG.info('Starting sfc_winds: %s %s', fnames, command_line_args)
    check_command_line_args(['sectorlist', 'sectorfiles', 'product_options'],
                            command_line_args)
    sectorfiles = command_line_args['sectorfiles']
    sectorlist = command_line_args['sectorlist']
    product_options = command_line_args['product_options']

    from geoips2.sector_utils.utils import get_area_defs_for_xarray
    from geoips2.xarray_utils.data import get_sectored_xarrays
    from geoips2.readers.sfc_winds_ncdf import sfc_winds_ncdf
    LOG.info('Filenames: %s', fnames)
    wind_xarrays = sfc_winds_ncdf(fnames)

    num_jobs = 0
    xarray_num = 0
    first = True
    for wind_xarray in wind_xarrays:
        xarray_num = xarray_num + 1
        # If we tell driver NOT to produce text wind files, then don't produce them. For reprocessing
        if product_options and 'notextwinds' in product_options:
            LOG.info('NOT PRODUCING TEXT FILE for %s winds, requested notextwinds on command line call',
                     wind_xarray.source_name)
        else:
            LOG.info('PRODUCING TEXT FILE FOR XARRAY NUMBER %s', xarray_num)
            output_products += write_full_text_file(wind_xarray, first=first, creation_time=creation_time)
            first = False

        if wind_xarray.source_name == 'ascat' and wind_xarray.sample_distance_km > 15:
            LOG.info('SKIPPING NOT PRODUCING IMAGERY FOR ASCAT 25km, this is %skm resolution',
                     wind_xarray.sample_distance_km)
            return output_products

        from geoips2.sector_utils.utils import get_area_defs_for_xarray, filter_area_defs_sector
        area_defs = get_area_defs_for_xarray(wind_xarray, sectorfiles, sectorlist,
                                             pixel_size_x=WSPD_PIXEL_SIZE_X, pixel_size_y=WSPD_PIXEL_SIZE_Y,
                                             num_pixels_x=WSPD_NUM_PIXELS_X, num_pixels_y=WSPD_NUM_PIXELS_Y,
                                             track_type='BEST')
        # from IPython import embed as shell; shell()
        area_defs = filter_area_defs_sector(area_defs, wind_xarray, var_for_coverage='wind_speed_kts')
        LOG.info('Area defs:\n%s', '\n'.join([area_def.name for area_def in area_defs]))

        for area_def in area_defs:
            process_datetimes[area_def.name] = {}
            process_datetimes[area_def.name]['start'] = datetime.utcnow()
            if 'wind_dir_deg_met' in wind_xarray.variables: 
                varlist = ['wind_speed_kts', 'wind_dir_deg_met']
            else:
                varlist = ['wind_speed_kts']
            sect_xarrays = get_sectored_xarrays([wind_xarray], area_def, varlist=varlist, get_bg_xarrays=True)
            if sect_xarrays and run_sector(sect_xarrays[0], area_def):

                curr_products = windspeed(sect_xarrays, area_def)
                output_products += curr_products

                curr_removed_products, curr_saved_products = remove_duplicates(curr_products,
                                                                               area_def,
                                                                               remove_files=False)
                removed_products += curr_removed_products
                saved_products += curr_saved_products

                num_jobs += 1
                process_datetimes[area_def.name]['end'] = datetime.utcnow()

            else:
                LOG.info('SKIPPING No coverage for %s %s', wind_xarray.source_name, area_def.name)

    process_datetimes['overall_end'] = datetime.utcnow()
    from geoips2.geoips2_utils import output_process_times
    output_process_times(process_datetimes, num_jobs)

    return output_products
