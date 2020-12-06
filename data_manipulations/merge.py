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

'''Utilities for merging granules from potentially different data sources / sensors / platforms into a single merge
   array.  These modules need a large amount of work before we can entirely remove GeoIPS 1.0 functionality.
   1. Use non-sectorfile object sector information
   2. Implement database for finding existing files rather than using scifile find_files_in_range
   3. Use xarray rather than SciFile for reading / writing files.
'''
# Python Standard Libraries
import logging
from datetime import timedelta

# Third Party Installed Libraries

LOG = logging.getLogger(__name__)


def minrange(start_date, end_date):
    '''Check one min at a time'''
    #log.info('in minrange')
    tr = end_date - start_date
    mins = int((tr.seconds + tr.days * 86400 ) / 60)
    LOG.info('%s', mins)
    for n in range(mins):
        yield start_date + timedelta(seconds = (n*60))


def daterange(start_date, end_date):
    '''Check one day at a time. 
        If end_date - start_date is between 1 and 2, days will be 1,
        and range(1) is 0. So add 2 to days to set range'''
    #log.info('in minrange')
    tr = end_date - start_date
    for n in range(tr.days + 2):
        yield start_date + timedelta(n)


def hourrange(start_date, end_date):
    '''Check one hour at a time. '''
    LOG.info('in hourrange')
    tr = end_date - start_date
    for n in range(tr.days*24 + tr.seconds / 3600 ):
        yield start_date + timedelta(seconds = (n*3600))


def find_datafiles_in_range(sector_name, platform_name, source_name, min_time, max_time,
                            basedir, product_name, every_min=True, verbose=False, time_format='%H%M',
                            actual_datetime=None, single_match=False):
    LOG.info('Finding %s %s %s files between %s and %s', sector_name, platform_name, source_name, min_time, max_time)
    from os.path import exists
    from glob import glob
    from geoips2.filenames.product_filenames import netcdf_write_filename
    fnames = []
    first = True
    min_timediff = 10000000
    if (min_time - max_time) < timedelta(minutes=30) or every_min == True:
        for sdt in minrange(min_time, max_time):
            ncdf_fname = netcdf_write_filename(basedir,
                                               product_name=product_name,
                                               source_name=source_name,
                                               platform_name=platform_name,
                                               sector_name=sector_name,
                                               product_datetime=sdt,
                                               time_format=time_format)
            ncdf_fnames = glob(ncdf_fname)
            if first:
                LOG.info('First path: %s', ncdf_fname)
                first = False
            if verbose:
                LOG.info('Checking %s', ncdf_fname)
            if ncdf_fnames:
                if single_match is True and abs((sdt - actual_datetime).seconds) < min_timediff:
                    min_timediff = (sdt - actual_datetime).seconds
                    LOG.info('    Adding %s, min_timediff now %s', ncdf_fnames, min_timediff)
                    fnames = ncdf_fnames
                if single_match is not True:
                    LOG.info('    Adding %s', ncdf_fnames)
                    fnames += ncdf_fnames
                
    return fnames


def merge_data(matching_fnames, sector_shape, variable_name, merge_samples, merge_lines, satzen_correction=False):

    # The primary sector is the overall sector shape - we will fill in from the various subsectors
    # Allow for subsectors so we don't have to produce the full global image from ALL sensors.
    import numpy as np
    from datetime import datetime

    attrs = {}
    attrs['overall_platform_names'] = []
    attrs['overall_source_names'] = []
    attrs['overall_data_providers'] = []
    attrs['overall_interpolation_radius_of_influences'] = []
    attrs['overall_start_datetime'] = datetime.utcnow()
    attrs['overall_end_datetime'] = datetime.strptime('19000101', '%Y%m%d')

    merged_data_array = np.ma.masked_all(sector_shape)
    partial_data_array = np.ma.masked_all(sector_shape) 
    satzen_array = np.ma.masked_all(sector_shape)

    for fname in matching_fnames:
        # Create a full masked array of the same shape as the primary sector.  We will populate this array
        # with the current subsector.
        currdata = np.ma.masked_all(sector_shape)
        from geoips2.xarray_utils.outputs import read_xarray_netcdf
        curr_xarray = read_xarray_netcdf(fname)
        if curr_xarray.platform_name not in attrs['overall_platform_names']:
            LOG.info('Adding to overall list...')
            attrs['overall_platform_names'] += [curr_xarray.platform_name]
            attrs['overall_source_names'] += [curr_xarray.source_name]
            attrs['overall_data_providers'] += [curr_xarray.data_provider]
            if 'interpolation_radius_of_influence' in curr_xarray.attrs.keys():
                attrs['overall_interpolation_radius_of_influences'] += [curr_xarray.interpolation_radius_of_influence]
            else:
                attrs['overall_interpolation_radius_of_influences'] += ['None']
        if curr_xarray.start_datetime < attrs['overall_start_datetime']:
            LOG.info('New overall_start_datetime...')
            attrs['overall_start_datetime'] = curr_xarray.start_datetime
        if curr_xarray.end_datetime > attrs['overall_end_datetime']:
            LOG.info('New overall_end_datetime...')
            attrs['overall_end_datetime'] = curr_xarray.end_datetime


        # Pull the min/max lines/samples out of the config file for the current subsector.
        # This determines where the current data will go in the primary sector.
        min_sample = merge_samples[curr_xarray.sector_name][0]
        max_sample = merge_samples[curr_xarray.sector_name][1]
        min_line = merge_lines[curr_xarray.sector_name][0]
        max_line = merge_lines[curr_xarray.sector_name][1]

        # Put the subsector data in the appropriate location in the primary sector
        currdata[min_line:max_line, min_sample:max_sample] = np.ma.masked_invalid(curr_xarray[variable_name])

        # Once we have an existing merged data array for the current channel, merge the current subsector
        # data into the existing final data array.  Note this puts the first image we find on top, and
        # it stays there.
        # MLS3 Note this where we would blend the arrays together to make a prettier picture without
        # sharp transitions.  There would be an extra line creating a "blended_data_array" which smooths
        # the transitions between currdata and merged_data_array, then merged_data_array[channame] would be
        # replaced with "blended_data_array" in the np.ma.where call below. Or, use the same line below,
        # and update merged_data_array[channame] with the blended values prior to calling np.ma.where

        LOG.info(' Adding %s %s %s %s %s data, %0.2f coverage ... ',
                 curr_xarray.source_name, curr_xarray.platform_name,
                 curr_xarray.sector_name,
                 curr_xarray.start_datetime,
                 variable_name,
                 np.ma.count(currdata)*1.0 / currdata.size)

        if curr_xarray[variable_name].to_masked_array().shape != currdata.shape:
            LOG.info('     Merging partial array, no satzen correction')
            partial_data_array = np.ma.where(currdata.mask==False,
                                             currdata,
                                             partial_data_array)
        elif satzen_correction and 'SatZenith' in curr_xarray.variables:
            LOG.info('     Applying SatZenith correction to overlapping data')
            overlap_inds = np.ma.where(~currdata.mask & ~merged_data_array.mask)
            currdata_inds = np.ma.where(~currdata.mask & merged_data_array.mask)
            if overlap_inds[0].size > 0:
                satzen_overlap = np.radians(curr_xarray['SatZenith'].to_masked_array()[overlap_inds])
                merged_data_array[overlap_inds] = np.cos(satzen_overlap) * currdata[overlap_inds] \
                                                  + (1 - np.cos(satzen_overlap)) * merged_data_array[overlap_inds]
            merged_data_array[currdata_inds] = currdata[currdata_inds]
            satzen_array[currdata_inds] = np.radians(curr_xarray['SatZenith'].to_masked_array()[currdata_inds])
            satzen_array[overlap_inds] = np.radians(curr_xarray['SatZenith'].to_masked_array()[overlap_inds])
        else:
            LOG.info('     SatZenith array not defined or satzen_correction %s not requested', satzen_correction)
            merged_data_array = np.ma.where(currdata.mask==False,
                                            currdata,
                                            merged_data_array)

        # Tell the user what source, platform, time, channel was just merged.
        # Include the current subsector's percent coverage, as well as the new fully merged array percent
        # coverage.
        LOG.info('     Added %s %s %s %s %s data, %0.2f coverage, partial coverage now %0.2f, total coverage %0.2f',
                 curr_xarray.source_name, curr_xarray.platform_name,
                 curr_xarray.sector_name,
                 curr_xarray.start_datetime,
                 variable_name,
                 np.ma.count(currdata)*1.0 / currdata.size,
                 np.ma.count(partial_data_array)*1.0 / partial_data_array.size,
                 np.ma.count(merged_data_array)*1.0 / merged_data_array.size)

    LOG.info('Merging partial array with full array')
    # overlap_inds = np.ma.where(~satzen_array.mask & ~partial_data_array.mask)
    # if overlap_inds[0].size > 0:
    #     satzen_overlap = np.radians(curr_xarray['SatZenith'].to_masked_array()[overlap_inds])
    #     merged_data_array[overlap_inds] = np.cos(satzen_overlap) * merged_data_array[overlap_inds] \
    #                                       + (1 - np.cos(satzen_overlap)) * partial_data_array[overlap_inds]
    merged_data_array = np.ma.where(merged_data_array.mask==False,
                                    merged_data_array,
                                    partial_data_array)

    LOG.info('     Final coverage %0.2f', np.ma.count(merged_data_array)*1.0 / merged_data_array.size)

    return merged_data_array, attrs


def get_matching_files(primary_sector_name, subsector_names, platforms, sources, max_time_diffs,
                       basedir, merge_datetime, product_name, time_format='%H%M', buffer_mins=30,
                       verbose=False, single_match=False):
    '''Given the current primary sector, and associated subsectors/platforms/sources, find all matching files
    Parameters:
        primary_sector_name (str): The final sector that all data will be stitched into
                                   ie 'GlobalGlobal'
        subsector_names (list of str): List of all subsectors that will be merged into the final sector (potentially
                                       including the full primary_sector_name.)
                                       ie ['GlobalGlobal', 'GlobalAntarctic', 'GlobalArctic']
        platforms (list of str): List of all desired platforms - platforms, sources, and max_time_diffs correspond to
                                 one another and should be the same length, in the same order.  
        sources (list of str): List of all desired sources - platforms, sources, and max_time_diffs correspond to
                               one another and should be the same length, in the same order.  
        max_time_diffs (list of int): Minutes. List of allowed time diffs for given platform/source. Matches
                                      max_time_diff before the requested merge_datetime argument - platforms, sources,
                                      and max_time_diffs correspond to one another and should be the same length,
                                      in the same order.  
        basedir (str): Base directory in which to look for the matching files
        merge_datetime (datetime.datetime): Attempt matching max_time_diff prior to merge_datetime
        product_name (str): product_name string found in matching files
        time_format (str): Requested time format for filenames (strptime format string)

    Returns: (list of str) List of file names that matched requested paramters.
    '''
                      

    from geoips2.filenames.base_paths import PATHS as gpaths
    from datetime import timedelta

    # MLS1 prev_files should be a dictionary with primary sector names as keys - otherwise it will not work.
    prev_files = []
    actual_datetime = None
    if single_match is True:
        actual_datetime = merge_datetime

    # Go through the list of platforms / sources / allowed time diffs to find the appropriate files for each 
    # data type
    for platform, source, time_diff in zip(platforms,
                                           sources,
                                           max_time_diffs):

        # Go through the list of all subsectors needed to merge into the primary sector listed above
        for currsectname in subsector_names:

            # Get the sector name from the current subsector.
            LOG.info('Checking %s %s %s %s', currsectname, platform, source, time_diff)
            curr_verbose=verbose
            # if platform == 'npp':
            #     curr_verbose=False

            # Use the time/source/platform/sector name to find the desired matching files.
            # MLS1 This should be prev_files[primary_sector_name]
            prev_files += find_datafiles_in_range(currsectname,
                                                  platform,
                                                  source,
                                                  merge_datetime - timedelta(minutes=time_diff),
                                                  merge_datetime + timedelta(minutes=buffer_mins),
                                                  basedir=basedir,
                                                  product_name=product_name,
                                                  every_min=True,
                                                  verbose=curr_verbose,
                                                  time_format=time_format,
                                                  actual_datetime=actual_datetime,
                                                  single_match=single_match)
    return prev_files


#     # Find previous datafiles within range.
#     # THIS SHOULD BE REPLACED BY A DATABASE!
#     # We are using ONLY pre-existing registered data files, not the currently processed data file (that has already 
#     # been written out as a pre-registered datafile, and it will be included here)
#     sectdatas = {}

#     # MLS1 At this stage, we would have to loop through the primary sector name keys of prev_files, and have another
#     # level for sectdatas with the primary sector name as key. sectdatas[primary_sector_name][secttag]
#     for prev_file in sorted(prev_files, reverse=True):
# 
#         from geoips2.xarray_utils.outputs import read_xarray_netcdf
#         # We are opening the current data file in order to determine what source and platform it is.
#         sectdata = read_xarray_netcdf(prev_file)
#         source_name = sectdata.source_name
#         platform_name = sectdata.platform_name
# 
#         # Produce the key for the dictionary of all scifile objects.  Each scifile object that will go into
#         # the merged data file is uniquely identified by the source, platform, and time.
#         secttag = '{0}_{1}_{2}'.format(source_name, platform_name, sectdata.start_datetime.strftime('%Y%m%d.%H%M%S'))
# 
#         # If we have not included the current data file yet, add to the dictionary of files to be merged.
#         # I have no idea why there would be duplicates, but don't include them if there are.
#         if secttag not in sectdatas.keys():
#             sectdatas[secttag] = sectdata
# 
#     outdata = {}
#     # Loop through required primary sectors, merge data.
#     # MLS1 We should be passing sectdatas[primary_sect_name]
#     for sectname in cfg['sectors'].keys():
#         outdata = merge_data(outdata, sectdatas, sectname, cfg)
# 
