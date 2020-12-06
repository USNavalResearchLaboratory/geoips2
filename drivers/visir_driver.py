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


def visir_driver(fnames, command_line_args=None):
    ''' Overall visir driver.  This handles reading the datafiles,
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
    from datetime import datetime
    process_datetimes = {}
    process_datetimes['overall_start'] = datetime.utcnow()
    final_products = []
    sectorfiles = command_line_args['sectorfiles']
    sectorlist = command_line_args['sectorlist']
    readername = command_line_args['readername']
    variables = command_line_args['variables']
    if sectorfiles and not isinstance(sectorfiles, list):
        raise TypeError('Must pass list of strings for "sectorfiles" dictionary entry')
    if sectorlist and not isinstance(sectorlist, list):
        raise TypeError('Must pass list of strings for "sectorfiles" dictionary entry')

    reader = find_module_in_geoips2_packages(module_name='readers',
                                             method_name=readername)
    product = find_module_in_geoips2_packages(module_name='products',
                                              method_name='visir')
    LOG.info('fnames: %s', fnames)
    LOG.info('command_line_args: %s', command_line_args)
    LOG.info('reader: %s', reader)
    LOG.info('variables: %s', variables)
    xarrays = reader(fnames, metadata_only=True, chans=variables)
        
    num_jobs = 0
    area_defs = []
    actual_datetime = None
    for curr_xarray in xarrays:
        from geoips2.sector_utils.utils import get_area_defs_for_xarray, filter_area_defs_actual_time
        actual_datetime = curr_xarray.start_datetime
        area_defs += get_area_defs_for_xarray(curr_xarray, sectorfiles, sectorlist)
    area_defs = filter_area_defs_actual_time(area_defs, actual_datetime) 

    LOG.info('Area defs:\n%s', '\n'.join([area_def.name for area_def in area_defs]))
    for area_def in area_defs:
        process_datetimes[area_def.area_id] = {}
        process_datetimes[area_def.area_id]['start'] = datetime.utcnow()
        from geoips2.sector_utils.atcf_tracks import set_atcf_area_def
        from geoips2.sector_utils.utils import is_sector_type
        pad_area_def = area_def
        if is_sector_type(area_def, 'atcf'):
            # Get an extra 10% size for TCs so we can handle recentering and not have missing data.
            num_lines = int(area_def.y_size * 1.10)
            num_samples = int(area_def.x_size * 1.10)
            pad_area_def = set_atcf_area_def(area_def.sector_info,
                                             num_lines=num_lines,
                                             num_samples=num_samples,
                                             pixel_width=area_def.pixel_size_x,
                                             pixel_height=area_def.pixel_size_y)
        try:
            xarrays = reader(fnames, metadata_only=False, area_def=pad_area_def, chans=variables)
        except IndexError as resp:
            LOG.warning('SKIPPING no coverage')
            process_datetimes[area_def.area_id]['fail'] = datetime.utcnow()
            continue
        except TypeError as resp:
            LOG.warning('CONTINUE not sectorable reader, use full dataset')

        LOG.info('Trying area_def %s', area_def)
        final_products += product(xarrays, area_def)
        num_jobs += 1
        process_datetimes[area_def.area_id]['end'] = datetime.utcnow()

    process_datetimes['overall_end'] = datetime.utcnow()
    from geoips2.geoips2_utils import output_process_times
    output_process_times(process_datetimes, num_jobs)

    return final_products
