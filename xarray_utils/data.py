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

''' utilities for manipulating xarray Datasets or DataArrays '''

# Python Standard Libraries
import logging

# Third Party Installed Libraries

LOG = logging.getLogger(__name__)

# scipy.interpolate.griddata requires at least 4 points. Don't bother plotting if fewer than 4.
MIN_POINTS = 4


def get_lat_lon_points(checklat, checklon, diff, sect_xarray, varname):
    '''Utility for pulling the data values a given distance around a specified lat/lon location, from numpy arrays.
    Parameters:
        checklat (float): latitude of interest
        checklon (float): longitude of interest
        diff (float): check +- diff of latitude and longitude
        sect_xarray (Dataset) : xarray dataset containing 'latitude' 'longitude' and varname variables
        varname (str) : variable name of data array to use for returning data values
    Returns:
        (float, float, int) : min value in range, max value in range, and number of points in range
    '''
    xinds = (sect_xarray['longitude'] > checklon - diff)\
             & (sect_xarray['longitude'] < checklon + diff)\
             & (sect_xarray['latitude'] > checklat - diff)\
             & (sect_xarray['latitude'] < checklat + diff)
    import numpy
    return (sect_xarray[varname].where(xinds).min(),
            sect_xarray[varname].where(xinds).max(),
            numpy.ma.count(sect_xarray['B14BT'].where(xinds).to_masked_array()))


def get_lat_lon_points_numpy(checklat, checklon, diff, lat_array, lon_array, data_array):
    '''Utility for pulling the data values a given distance around a specified lat/lon location, from numpy arrays.
    Parameters:
        checklat (float): latitude of interest
        checklon (float): longitude of interest
        diff (float): check +- diff of latitude and longitude
        lat_array (ndarray) : numpy ndarray of latitude locations - same shape as lon_array and data_array
        lon_array (ndarray) : numpy ndarray of longitude locations - same shape as lat_array and data_array
        data_array (ndarray) : numpy ndarray data values - same shape as lat_array and lon_array
    Returns:
        (float, float, int) : min value in range, max value in range, and number of points in range
    '''

    import numpy
    inds = numpy.logical_and(lat_array > checklat - diff,
                             lat_array < checklat + diff) & numpy.logical_and(lon_array > checklon - diff,
                                                                              lon_array < checklon + diff)
   

    return (data_array[inds].min(), data_array[inds].max(), numpy.ma.count(data_array[inds]))
     

    



def sector_xarray_temporal(full_xarray, mindt, maxdt, varnames, verbose=False):
    ''' Sector an xarray object temporally.  If full_xarray is None, return None.
        Parameters:
            full_xarray (xarray.Dataset): xarray object to sector temporally
            mindt (datetime.datetime): minimum datetime of desired data
            maxdt (datetime.datetime): maximum datetime of desired data
            varnames (list of str): list of variable names that should be sectored based on 'timestamp', mindt, maxdt
        Returns:
            None: if full_xarray is None, return None
            full full_xarray: return full original xarray object if 'timestamp' is not included in varnames list
            time_xarray: return sectored xarray object with only the desired times, specified by mindt and maxdt'''

    import numpy

    if full_xarray is None:
        LOG.info('full_xarray is None - not attempting to sector temporally, returning None')
        return None

    # find data that pertains to current time and location
    time_xarray = full_xarray.copy()

    if 'timestamp' not in varnames:
        LOG.info('timestamp variable not included in list - not temporally sectoring, returning all data')
        return time_xarray

    for varname in varnames:
        good_speeds = numpy.ma.count(time_xarray[varname].to_masked_array())
        if verbose:
            LOG.info('STARTED TIME WITH %s points for %s', good_speeds, varname)
    mindt64 = numpy.datetime64(mindt)
    maxdt64 = numpy.datetime64(maxdt)

    time_inds = (full_xarray['timestamp'] > mindt64) & (full_xarray['timestamp'] < maxdt64)
    covg = False
    final_good_points = 0
    for varname in varnames:
        time_xarray[varname] = full_xarray[varname].where(time_inds)
        good_speeds = numpy.ma.count(time_xarray[varname].to_masked_array())
        if good_speeds > final_good_points:
            final_good_points = good_speeds
        if good_speeds < MIN_POINTS:
            if verbose:
                LOG.warning('INSUFFICIENT TIME DATA between %s and %s for var %s, %s points',
                            mindt, maxdt, varname, good_speeds)
        else:
            if verbose:
                LOG.info('MATCHED TIME %s points for var %s', good_speeds, varname)
            covg = True

    if not covg:
        LOG.warning('INSUFFICIENT TIME DATA between %s and %s for any vars, skipping', mindt, maxdt)
        return None
    LOG.info('SUFFICIENT TIME DATA between %s and %s for any var %s points', mindt, maxdt, final_good_points)
    return time_xarray


def sector_xarray_spatial(full_xarray, extent_lonlat, varnames, lon_pad=3, lat_pad=0, verbose=False):
    ''' Sector an xarray object spatially.  If full_xarray is None, return None.
        Parameters:
            full_xarray (xarray.Dataset): xarray object to sector spatially
            extent_lonlat (list of float): Area to sector: [MINLON, MINLAT, MAXLON, MAXLAT]
            varnames (list of str): list of variable names that should be sectored based on 'timestamp'
        Returns:
            None: if full_xarray is None, return None
            time_xarray: return '''

    if full_xarray is None:
        if verbose:
            LOG.info('full_xarray is None - not attempting to sector spatially, returning None')
        return None

    sector_xarray = full_xarray.copy()

    import numpy
    from pyresample import utils
    if verbose:
        LOG.info('Padding longitudes')
    # convert extent longitude to be within 0-360 range
    extent_lonlat[0] = utils.wrap_longitudes(extent_lonlat[0]) - lon_pad
    extent_lonlat[2] = utils.wrap_longitudes(extent_lonlat[2]) + lon_pad
    if extent_lonlat[0] > extent_lonlat[2] and extent_lonlat[2] < 0:
        extent_lonlat[2] = extent_lonlat[2] + 360
    extent_lonlat[1] = extent_lonlat[1] - lat_pad
    extent_lonlat[3] = extent_lonlat[3] + lat_pad
    if verbose:
        LOG.info('Padding latitudes')
    # Make sure we don't extend latitudes beyond -90 / +90
    if extent_lonlat[1] < -90.0:
        extent_lonlat[1] = -90.0
    if extent_lonlat[3] > 90.0:
        extent_lonlat[3] = 90.0

    if verbose:
        LOG.info('Wrapping longitudes')
    import xarray
    lons = utils.wrap_longitudes(full_xarray['longitude'])

    if verbose:
        LOG.info('Handling dateline')
    if lons.max() > 179.5 and lons.min() < -179.5 and extent_lonlat[2] > 0 and extent_lonlat[0] > 0:
        lons = xarray.where(full_xarray['longitude'] < 0, full_xarray['longitude'] + 360, full_xarray['longitude'])
    lats = full_xarray['latitude']

    for varname in varnames:
        good_speeds = numpy.ma.count(sector_xarray[varname].to_masked_array())
        if verbose:
            LOG.info('STARTED SPATIAL WITH %s points for %s', good_speeds, varname)

    if verbose:
        LOG.info('Getting appropriate sector area lon %s to %s lat %s to %s, minlon %s, maxlon %s, minlat %s, maxlat %s, %s points',
                 extent_lonlat[0], extent_lonlat[2],
                 extent_lonlat[1], extent_lonlat[3],
                 lons.min().data, lons.max().data, lats.min().data, lats.max().data, good_speeds)

    sector_inds = (lons > extent_lonlat[0])\
        & (lons < extent_lonlat[2])\
        & (full_xarray['latitude'] > extent_lonlat[1])\
        & (full_xarray['latitude'] < extent_lonlat[3])

    # from IPython import embed as shell; shell()
    covg = False
    final_good_points = 0
    for varname in varnames:
        sector_xarray[varname] = full_xarray[varname].where(sector_inds)
        good_speeds = numpy.ma.count(sector_xarray[varname].to_masked_array())
        if good_speeds > final_good_points:
            final_good_points = good_speeds

        if sector_xarray['latitude'].size < MIN_POINTS or good_speeds < MIN_POINTS:
            if verbose:
                LOG.warning('INSUFFICIENT SPATIAL DATA between %0.2f and %0.2f lon and %0.2f and %0.2f lat, varname %s, %s points',
                            extent_lonlat[0], extent_lonlat[2], extent_lonlat[1], extent_lonlat[3], varname, good_speeds)
        else:
            if verbose:
                LOG.info('MATCHED SPATIAL %s points for var %s after location sectoring', good_speeds, varname)
            covg = True

    if not covg:
        LOG.warning('OVERALL INSUFFICIENT SPATIAL DATA between %0.2f and %0.2f lon and %0.2f and %0.2f lat',
                    extent_lonlat[0], extent_lonlat[2], extent_lonlat[1], extent_lonlat[3])
        return None

    LOG.warning('OVERALL SUFFICIENT SPATIAL DATA between %0.2f and %0.2f lon and %0.2f and %0.2f lat %s points',
                extent_lonlat[0], extent_lonlat[2], extent_lonlat[1], extent_lonlat[3], final_good_points)
    return sector_xarray


def sector_xarray_dataset(full_xarray, area_def, varnames, lon_pad=3, lat_pad=0, verbose=False,
                          hours_before_sector_time=18, hours_after_sector_time=6):
    ''' Use the xarray to appropriately sector out data by lat/lon and time '''
    from datetime import timedelta

    LOG.info('Full xarray start/end datetime: %s %s',
             full_xarray.start_datetime,
             full_xarray.end_datetime)
             # numpy.ma.count(full_xarray[varnames[0]].to_masked_array()))

    if area_def is not None:
        if hasattr(area_def, 'sector_start_datetime') and area_def.sector_start_datetime:
            # If it is a dynamic sector, sector temporally to make sure we use the appropriate data
            mindt = area_def.sector_start_datetime - timedelta(hours=hours_before_sector_time)
            maxdt = area_def.sector_start_datetime + timedelta(hours=hours_after_sector_time)
            time_xarray = sector_xarray_temporal(full_xarray, mindt, maxdt, varnames, verbose=verbose)
        else:
            # If it is not a dynamic sector, just return all of the data, because all we care about is spatial coverage.
            time_xarray = full_xarray.copy()

        extent_lonlat = list(area_def.area_extent_ll)
        sector_xarray = sector_xarray_spatial(time_xarray, extent_lonlat, varnames, lon_pad, lat_pad, verbose=verbose)
        if sector_xarray is not None\
           and 'timestamp' in varnames and hasattr(area_def, 'sector_start_datetime') and area_def.sector_start_datetime:
            from geoips2.xarray_utils.timestamp import get_min_from_xarray_timestamp, get_max_from_xarray_timestamp
            sector_xarray.attrs['area_def'] = area_def
            sector_xarray.attrs['start_datetime'] = get_min_from_xarray_timestamp(sector_xarray, 'timestamp')
            sector_xarray.attrs['end_datetime'] = get_max_from_xarray_timestamp(sector_xarray, 'timestamp')
        elif sector_xarray is not None:
            sector_xarray.attrs['area_def'] = area_def
            sector_xarray.attrs['start_datetime'] = full_xarray.start_datetime
            sector_xarray.attrs['end_datetime'] = full_xarray.end_datetime

    else:
        sector_xarray = full_xarray.copy()

    if sector_xarray is not None:
        if verbose:
            LOG.info('Sectored data start/end datetime: %s %s',
                     sector_xarray.start_datetime,
                     sector_xarray.end_datetime)
                     # numpy.ma.count(full_xarray[varnames[0]].to_masked_array()))

    return sector_xarray


def get_vis_ir_bg(sect_xarray):
    ''' Find matching vis/ir background for data in sect_xarray'''
    from geoips2.data_manipulations.merge import get_matching_files
    from geoips2.filenames.base_paths import PATHS as gpaths
    import xarray
    irfnames = get_matching_files(sect_xarray.area_def.area_id,
                                  [sect_xarray.area_def.area_id],
                                  ['himawari8', 'goes16', 'goes17'],
                                  ['ahi', 'abi', 'abi'],
                                  [30, 30, 30],
                                  gpaths['PRECALCULATED_DATA_PATH'],
                                  sect_xarray.start_datetime,
                                  'Infrared-Gray_latitude_longitude',
                                  time_format='%H%M*',
                                  buffer_mins=75,
                                  verbose=False,
                                  single_match=True)
    visfnames = get_matching_files(sect_xarray.area_def.area_id,
                                   [sect_xarray.area_def.area_id],
                                   ['himawari8', 'goes16', 'goes17'],
                                   ['ahi', 'abi', 'abi'],
                                   [30, 30, 30],
                                   gpaths['PRECALCULATED_DATA_PATH'],
                                   sect_xarray.start_datetime,
                                   'Visible-Gray_latitude_longitude',
                                   time_format='%H%M*',
                                   buffer_mins=75,
                                   verbose=False,
                                   single_match=True)
    ret_arr = []
    from geoips2.xarray_utils.outputs import read_xarray_netcdf
    if irfnames:
        ir_bg = read_xarray_netcdf(irfnames[0])
        ret_arr += [ir_bg]
    if visfnames:
        vis_bg = read_xarray_netcdf(visfnames[0])
        ret_arr += [vis_bg]
    return ret_arr


def sector_xarrays(xobjs, area_def, varlist, verbose=False, hours_before_sector_time=18, hours_after_sector_time=6):
    '''Return list of sectored xarray objects '''
    import numpy
    ret_xobjs = []
    for xobj in xobjs:
        # Compile a list of variables that will be used to sector - the current data variable, and we will add in
        # the appropriate latitude and longitude variables (of the same shape as data), and if it exists the
        # appropriately shaped timestamp array
        vars_to_interp = list(set(varlist) & set(xobj.variables.keys()))
        if not vars_to_interp:
            LOG.info('No required variables, skipping dataset')
            continue

        from geoips2.sector_utils.utils import is_dynamic_sector
        if is_dynamic_sector(area_def):
            LOG.info('Trying to sector %s with dynamic time %s, %s points',
                     area_def.area_id, area_def.sector_start_datetime, xobj['latitude'].size)
        else:
            LOG.info('Trying to sector %s, %s points', area_def.area_id, xobj['latitude'].size)

        vars_to_sect = []
        vars_to_sect += vars_to_interp
        # we have to have 'latitude','longitude" in the full_xarray, and 'timestamp' if we want temporal sectoring
        if 'latitude' in xobj.variables.keys():
            vars_to_sect += ['latitude']
        if 'longitude' in xobj.variables.keys():
            vars_to_sect += ['longitude']
        if 'timestamp' in xobj.variables.keys():
            vars_to_sect += ['timestamp']

        from geoips2.xarray_utils.data import sector_xarray_dataset
        # The list of variables in vars_to_sect must ALL be the same shape
        sect_xarray = sector_xarray_dataset(xobj,
                                            area_def,
                                            vars_to_sect,
                                            verbose=verbose,
                                            hours_before_sector_time=hours_before_sector_time,
                                            hours_after_sector_time=hours_after_sector_time)

        # numpy arrays fail if numpy_array is None, and xarrays fail if x_array == None
        if sect_xarray is None:
            if verbose:
                LOG.info('No coverage - skipping dataset')
            continue

        from geoips2.sector_utils.utils import is_sector_type
        if is_sector_type(area_def, 'atcf'):
            from geoips2.sector_utils.utils import check_center_coverage
            has_covg, covg_xarray = check_center_coverage(sect_xarray,
                                                          area_def,
                                                          varlist=vars_to_sect,
                                                          covg_varname=vars_to_sect[0],
                                                          width_degrees=8, height_degrees=8,
                                                          verbose=verbose)

            if not has_covg:
                LOG.info('SKIPPING NO COVERAGE IN center box - NOT PROCESSING')
                continue

            # If the time within the box is > 50 min, we have two overpasses. ALL PMW sensors are polar orbiters.
            if (covg_xarray.end_datetime - covg_xarray.start_datetime).seconds > 3000:
                LOG.info('Original sectored xarray contains more than one overpass - switching to start/datetime in center')
                sect_xarray.attrs['start_datetime'] = covg_xarray.start_datetime
                sect_xarray.attrs['end_datetime'] = covg_xarray.end_datetime

        sect_xarray.attrs['area_def'] = area_def        # add name of this sector to sector attribute
        if hasattr(sect_xarray, 'timestamp'):
            from geoips2.xarray_utils.timestamp import get_min_from_xarray_timestamp
            from geoips2.xarray_utils.timestamp import get_max_from_xarray_timestamp
            sect_xarray.attrs['start_datetime'] = get_min_from_xarray_timestamp(sect_xarray, 'timestamp')
            sect_xarray.attrs['end_datetime'] = get_max_from_xarray_timestamp(sect_xarray, 'timestamp')
            # Note:  need to test whether above two lines can reselect min and max time_info for this sector

        LOG.info('Sectored data start/end datetime: %s %s, %s points from var %s, all vars %s',
                 sect_xarray.start_datetime,
                 sect_xarray.end_datetime,
                 numpy.ma.count(sect_xarray[vars_to_interp[0]].to_masked_array()),
                 vars_to_interp[0],
                 vars_to_interp)
        ret_xobjs += [sect_xarray]

    return ret_xobjs


def get_sectored_xarrays(xobjs, area_def, varlist, get_bg_xarrays=False):
    ''' Get all xarray objects sectored to area_def, including PMW and VIS/IR overlays '''
    # All datasets will be of the same data type
    sect_xarrays = sector_xarrays(xobjs, area_def, varlist)
    if get_bg_xarrays and sect_xarrays:
        bg_xarrays = get_vis_ir_bg(sect_xarrays[0])
        sect_xarrays += sector_xarrays(bg_xarrays, area_def, ['Infrared-Gray', 'Visible-Gray'])
    else:
        LOG.info('SKIPPING BACKGROUNDS, no coverage for %s %s', xobjs[0].source_name, area_def.name)
    return sect_xarrays
