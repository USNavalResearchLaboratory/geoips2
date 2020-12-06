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

'''Read derived surface winds from SAR, SMAP, SMOS, and AMSR netcdf data.'''
import logging
LOG = logging.getLogger(__name__)

MS_TO_KTS = 1.94384
DEG_TO_KM = 111.321


def read_byu_data(wind_xarray):
    ''' Reformat ascat xarray object appropriately
            variables: latitude, longitude, timestamp, wind_speed_kts, wind_dir_deg_met
            attributes: source_name, platform_name, data_provider, interpolation_radius_of_influence'''

    if 'L2B_filename' in wind_xarray.attrs and 'metopa' in wind_xarray.L2B_filename:
        wind_xarray.attrs['source_name'] = 'ascatuhr'
        wind_xarray.attrs['platform_name'] = 'metopa'
    elif 'L2B_filename' in wind_xarray.attrs and 'metopb' in wind_xarray.L2B_filename:
        wind_xarray.attrs['source_name'] = 'ascatuhr'
        wind_xarray.attrs['platform_name'] = 'metopb'
    elif 'L2B_filename' in wind_xarray.attrs and 'metopc' in wind_xarray.L2B_filename:
        wind_xarray.attrs['source_name'] = 'ascatuhr'
        wind_xarray.attrs['platform_name'] = 'metopc'
    elif 'SZF_filenames' in wind_xarray.attrs and 'M02' in wind_xarray.SZF_filenames:
        wind_xarray.attrs['source_name'] = 'ascatuhrsig0'
        wind_xarray.attrs['platform_name'] = 'metopa'
    elif 'SZF_filenames' in wind_xarray.attrs and 'M01' in wind_xarray.SZF_filenames:
        wind_xarray.attrs['source_name'] = 'ascatuhrsig0'
        wind_xarray.attrs['platform_name'] = 'metopb'
    elif 'SZF_filenames' in wind_xarray.attrs and 'M03' in wind_xarray.SZF_filenames:
        wind_xarray.attrs['source_name'] = 'ascatuhrsig0'
        wind_xarray.attrs['platform_name'] = 'metopc'

    wind_xarray.attrs['interpolation_radius_of_influence'] = 20000
    # 1.25km grid, 4km accuracy
    wind_xarray.attrs['sample_distance_km'] = 4
    wind_xarray.attrs['data_provider'] = 'byu'
    import os
    # Store the storm names lower case - only reference to it is in the filename..
    storm_name = os.path.basename(wind_xarray.original_source_filename).split('_')[3].lower()
    expected_yymmdd = os.path.basename(wind_xarray.original_source_filename).split('_')[4]
    expected_hhmn = os.path.basename(wind_xarray.original_source_filename.replace('.WRave3.nc',
                                                                                  '').replace('.avewr.nc',
                                                                                              '')).split('_')[5]
    # from IPython import embed as shell; shell()
    wind_xarray.attrs['storms_with_coverage'] = [storm_name]
    from datetime import datetime
    wind_xarray.attrs['expected_synoptic_time'] = datetime.strptime(expected_yymmdd+expected_hhmn, '%y%m%d%H%M')

    import numpy
    import xarray

    if 'wspeeds' in wind_xarray.variables:
        wind_xarray['wind_speed_kts'] = xarray.where(wind_xarray.ambiguity_select == 1,
                                                     wind_xarray.wspeeds[:, :, 0],
                                                     numpy.nan)
        wind_xarray['wind_speed_kts'] = xarray.where(wind_xarray.ambiguity_select == 2,
                                                     wind_xarray.wspeeds[:, :, 1],
                                                     wind_xarray.wind_speed_kts)
        wind_xarray['wind_speed_kts'] = xarray.where(wind_xarray.ambiguity_select == 3,
                                                     wind_xarray.wspeeds[:, :, 2],
                                                     wind_xarray.wind_speed_kts)
        wind_xarray['wind_speed_kts'] = xarray.where(wind_xarray.ambiguity_select == 4,
                                                     wind_xarray.wspeeds[:, :, 3],
                                                     wind_xarray.wind_speed_kts)
        wind_xarray['wind_speed_kts'] = wind_xarray['wind_speed_kts'] * MS_TO_KTS

        wind_xarray['wind_dir_deg_met'] = xarray.where(wind_xarray.ambiguity_select == 1,
                                                       wind_xarray.wdirs[:, :, 0],
                                                       numpy.nan)
        wind_xarray['wind_dir_deg_met'] = xarray.where(wind_xarray.ambiguity_select == 2,
                                                       wind_xarray.wdirs[:, :, 1],
                                                       wind_xarray.wind_dir_deg_met)
        wind_xarray['wind_dir_deg_met'] = xarray.where(wind_xarray.ambiguity_select == 3,
                                                       wind_xarray.wdirs[:, :, 2],
                                                       wind_xarray.wind_dir_deg_met)
        wind_xarray['wind_dir_deg_met'] = xarray.where(wind_xarray.ambiguity_select == 4,
                                                       wind_xarray.wdirs[:, :, 3],
                                                       wind_xarray.wind_dir_deg_met)
        # Set wind_speed_kts appropriately
        wind_xarray['wind_speed_kts'].attrs = wind_xarray['wspeeds'].attrs.copy()
        wind_xarray['wind_speed_kts'].attrs['units'] = 'kts'
        wind_xarray['wind_speed_kts'].attrs['long_name'] = wind_xarray['wspeeds'].attrs['long_name'].replace('ambiguities', 'ambiguity selection')

        wind_xarray['wind_dir_deg_met'].attrs = wind_xarray['wdirs'].attrs.copy()

        # Set lat/lons/timestamp appropriately
        wind_xarray = wind_xarray.rename({'wspeeds': 'wind_speed_ambiguities_kts',
                                          'wdirs': 'wind_dir_ambiguities_deg_met'})

        wind_xarray['latitude'] = xarray.where(wind_xarray.ambiguity_select == 0,
                                               numpy.nan,
                                               wind_xarray.latitude) - 90

        wind_xarray['longitude'] = xarray.where(wind_xarray.ambiguity_select == 0,
                                                numpy.nan,
                                                wind_xarray.longitude)
    else:
        # bad vals where sigma 0 is -99.0
        wind_xarray['latitude'] = xarray.where(wind_xarray.sig_fore < -98.0,
                                               numpy.nan,
                                               wind_xarray.latitude) - 90

        wind_xarray['longitude'] = xarray.where(wind_xarray.sig_fore < -98.0,
                                                numpy.nan,
                                                wind_xarray.longitude)

    from datetime import datetime
    from numpy import datetime64
    startdt = datetime.strptime(wind_xarray.SZF_start_time[:-1], '%Y%m%d%H%M%S')
    enddt = datetime.strptime(wind_xarray.SZF_stop_time[:-1], '%Y%m%d%H%M%S')
    middt = startdt + (enddt - startdt) / 2
    timearray = numpy.ma.array(numpy.zeros(shape=wind_xarray.latitude.shape).astype(int) + datetime64(middt))
    wind_xarray['timestamp'] = xarray.DataArray(timearray,
                                                name='timestamp',
                                                coords=wind_xarray['latitude'].coords)
    wind_xarray = wind_xarray.set_coords(['timestamp'])

    return [wind_xarray]

def read_knmi_data(wind_xarray):
    ''' Reformat ascat xarray object appropriately
            variables: latitude, longitude, timestamp, wind_speed_kts, wind_dir_deg_met
            attributes: source_name, platform_name, data_provider, interpolation_radius_of_influence'''
    # Setting standard geoips attributes
    LOG.info('Reading %s data', wind_xarray.source)
    if wind_xarray.source == 'MetOp-C ASCAT':
        wind_xarray.attrs['source_name'] = 'ascat'
        wind_xarray.attrs['platform_name'] = 'metopc'
    elif wind_xarray.source == 'MetOp-B ASCAT':
        wind_xarray.attrs['source_name'] = 'ascat'
        wind_xarray.attrs['platform_name'] = 'metopb'
    elif wind_xarray.source == 'MetOp-A ASCAT':
        wind_xarray.attrs['source_name'] = 'ascat'
        wind_xarray.attrs['platform_name'] = 'metopa'
    elif wind_xarray.source == 'ScatSat-1 OSCAT':
        wind_xarray.attrs['source_name'] = 'oscat'
        wind_xarray.attrs['platform_name'] = 'scatsat-1'
        
    # Pixel size stored as "25.0 km"
    pixel_size = float(wind_xarray.pixel_size_on_horizontal.replace(' km', ''))

    # Interpolation Radius of Influence 
    wind_xarray.attrs['interpolation_radius_of_influence'] = pixel_size * 1000.0

    wind_xarray.attrs['sample_distance_km'] = pixel_size

    wind_xarray.attrs['data_provider'] = 'knmi'

    # setting wind_speed_kts appropriately
    wind_xarray['wind_speed_kts'] = wind_xarray['wind_speed'] * MS_TO_KTS
    wind_xarray['wind_speed_kts'].attrs = wind_xarray['wind_speed'].attrs
    wind_xarray['wind_speed_kts'].attrs['units'] = 'kts'

    # Directions in netcdf file use oceanography conventions
    wind_xarray['wind_dir_deg_met'] = wind_xarray['wind_dir'] - 180
    wind_xarray['wind_dir_deg_met'].attrs = wind_xarray['wind_dir'].attrs
    wind_xarray['wind_dir_deg_met'] = wind_xarray['wind_dir_deg_met'].where(wind_xarray['wind_dir_deg_met'] >= 0,
                                                                            wind_xarray['wind_dir_deg_met'] + 360)
    wind_xarray.wind_dir_deg_met.attrs['standard_name'] = 'wind_from_direction'
    wind_xarray.wind_dir_deg_met.attrs['valid_max'] = 360

    # Set lat/lons/timestamp appropriately
    wind_xarray = wind_xarray.rename({'lat': 'latitude', 'lon': 'longitude', 'time': 'timestamp'})
                                     
    wind_xarray = wind_xarray.set_coords(['timestamp'])
    return [wind_xarray]


def read_sar_data(wind_xarray):
    ''' Reformat SAR xarray object appropriately
            variables: latitude, longitude, timestamp, wind_speed_kts
            attributes: source_name, platform_name, data_provider, interpolation_radius_of_influence'''
    # Setting standard geoips attributes
    LOG.info('Reading SAR data')
    wind_xarray.attrs['source_name'] = 'sar-spd'
    wind_xarray.attrs['platform_name'] = 'sen1'
    if 'platform' in wind_xarray.attrs and wind_xarray.platform.lower() == 'radarsat-2':
        wind_xarray.attrs['platform_name'] = 'radarsat2'
    wind_xarray.attrs['interpolation_radius_of_influence'] = 3000
    # For resampling to a minimum-sized grid
    wind_xarray.attrs['sample_distance_km'] = 3.0
    wind_xarray.attrs['sample_pixels_x'] = 300
    wind_xarray.attrs['sample_pixels_y'] = 300
    wind_xarray.attrs['minimum_coverage'] = 0
    wind_xarray.attrs['granule_minutes'] = 0.42
    wind_xarray.attrs['data_provider'] = 'star'
    if 'acknowledgment' in wind_xarray.attrs and 'NOAA' in wind_xarray.acknowledgment:
        wind_xarray.attrs['data_provider'] = 'star'
    # Used for atcf filenames / text files

    LOG.info('Shape: %s', wind_xarray['sar_wind'].shape)
    # setting wind_speed_kts appropriately
    wind_xarray['wind_speed_kts'] = wind_xarray['sar_wind'] * MS_TO_KTS
    wind_xarray['wind_speed_kts'].attrs = wind_xarray['sar_wind'].attrs
    wind_xarray['wind_speed_kts'].attrs['units'] = 'kts'
    import xarray
    import numpy
    wind_xarray['wind_speed_kts'] = xarray.where(wind_xarray.mask == -1, wind_xarray.wind_speed_kts, numpy.nan)

    # Set lat/lons appropriately
    wind_xarray = wind_xarray.rename({'latitude': 'latitude', 'longitude': 'longitude'})

    # Set timestamp appropriately
    # Get the full array of timestamps.  pandas is much better with time series.
    wind_pandas = wind_xarray.to_dataframe()
    wind_xarray['timestamp'] = wind_pandas['acquisition_time'][:, 5, :].to_xarray().transpose()
    wind_xarray = wind_xarray.set_coords(['timestamp'])
    return [wind_xarray]


def read_remss_data(wind_xarray, data_type):
    ''' Reformat SMAP or WindSat xarray object appropriately
            variables: latitude, longitude, timestamp, wind_speed_kts
            attributes: source_name, platform_name, data_provider, interpolation_radius_of_influence'''
    import xarray
    import numpy
    from datetime import datetime
    # Set attributes appropriately
    wind_xarray.attrs['interpolation_radius_of_influence'] = 20000
    wind_xarray.attrs['sample_distance_km'] = DEG_TO_KM / 4
    if data_type == 'smap':
        LOG.info('Reading SMAP data')
        wind_xarray.attrs['source_name'] = 'smap-spd'
        wind_xarray.attrs['platform_name'] = 'smap'
        wind_xarray.attrs['data_provider'] = 'rss'
        wind_varname = 'wind'
        day_of_month_varname = 'day_of_month_of observation'
        minute_varname = 'minute'
    elif data_type == 'windsat':
        LOG.info('Reading WindSat data')
        wind_xarray.attrs['source_name'] = 'wsat'
        wind_xarray.attrs['platform_name'] = 'coriolis'
        wind_xarray.attrs['data_provider'] = 'rss'
        wind_varname = 'wind_speed_TC'
        day_of_month_varname = 'day_of_month_of_observation'
        minute_varname = 'time'
        wind_xarray.attrs['minimum_coverage'] = 10
    elif data_type == 'amsr2':
        LOG.info('Reading AMSR2 data')
        wind_xarray.attrs['source_name'] = 'amsr2rss'
        wind_xarray.attrs['platform_name'] = 'gcom-w1'
        wind_xarray.attrs['data_provider'] = 'rss'
        wind_varname = 'wind_speed_TC'
        day_of_month_varname = 'day_of_month_of_observation'
        minute_varname = 'time'
        wind_xarray.attrs['minimum_coverage'] = 10
    wind_xarray.attrs['full_day_file'] = True

    wind_xarray_1 = xarray.Dataset()
    wind_xarray_1.attrs = wind_xarray.attrs.copy()
    wind_xarray_1.attrs['current_node_dimension'] = 'node_dimension = 1'

    wind_xarray_2 = xarray.Dataset()
    wind_xarray_2.attrs = wind_xarray.attrs.copy()
    wind_xarray_2.attrs['current_node_dimension'] = 'node_dimension = 2'

    # Set wind_speed_kts appropriately
    winds_1 = numpy.flipud(wind_xarray[wind_varname].values[:, :, 0])
    winds_2 = numpy.flipud(wind_xarray[wind_varname].values[:, :, 1])

    # Full dataset is 720x1440x2, break that up into ascending and descending nodes.
    wind_xarray_1['wind_speed_kts'] = xarray.DataArray(winds_1 * MS_TO_KTS,
                                                       name='wind_speed_kts')
    wind_xarray_1['wind_speed_kts'].attrs = wind_xarray[wind_varname].attrs
    wind_xarray_1['wind_speed_kts'].attrs['units'] = 'kts'

    wind_xarray_2['wind_speed_kts'] = xarray.DataArray(winds_2 * MS_TO_KTS,
                                                       name='wind_speed_kts')
    wind_xarray_2['wind_speed_kts'].attrs = wind_xarray[wind_varname].attrs
    wind_xarray_2['wind_speed_kts'].attrs['units'] = 'kts'

    # Set lat/lons appropriately
    # These are (1440x720)
    lats2d, lons2d = numpy.meshgrid(wind_xarray.lat, wind_xarray.lon)
    # lats2d = numpy.dstack([lats2d.transpose(), lats2d.transpose()])
    # lons2d = numpy.dstack([lons2d.transpose(), lons2d.transpose()])
    lats2d = lats2d.transpose()
    lons2d = lons2d.transpose()
    wind_xarray_1['latitude'] = xarray.DataArray(data=numpy.flipud(lats2d))
    wind_xarray_1['longitude'] = xarray.DataArray(data=lons2d)
    wind_xarray_2['latitude'] = xarray.DataArray(data=numpy.flipud(lats2d))
    wind_xarray_2['longitude'] = xarray.DataArray(data=lons2d)
    wind_xarray_1 = wind_xarray_1.set_coords(['latitude', 'longitude'])
    wind_xarray_2 = wind_xarray_2.set_coords(['latitude', 'longitude'])

    from numpy import datetime64
    # Set timestamp appropriately
    year = wind_xarray.year_of_observation
    month = wind_xarray.month_of_observation
    day = wind_xarray.attrs[day_of_month_varname]
    basedt = datetime.strptime('{0:04d}{1:02d}{2:02d}'.format(year, month, day), '%Y%m%d')
    # minarr = wind_xarray.minute
    minarr = numpy.flipud(wind_xarray[minute_varname])
    # This is a hack to get latest version of numpy to work with masked datetime64 arrays.
    if hasattr(numpy, 'isnat') and numpy.isnat(minarr.max()):
        minarr = (minarr.astype(numpy.int64)/1000).astype(numpy.int64)
        minarr = numpy.ma.where(minarr < 0, numpy.nan, minarr)
        minarr = minarr.astype('timedelta64[us]')
    timearr = datetime64(basedt) + minarr
    wind_xarray_1['timestamp'] = xarray.DataArray(timearr[:, :, 0])
    wind_xarray_2['timestamp'] = xarray.DataArray(timearr[:, :, 1])
    wind_xarray_1 = wind_xarray_1.set_coords(['timestamp'])
    wind_xarray_2 = wind_xarray_2.set_coords(['timestamp'])
    return [wind_xarray_1, wind_xarray_2]


def read_smos_data(wind_xarray, fname):
    ''' Reformat SMOS xarray object appropriately
            variables: latitude, longitude, timestamp, wind_speed_kts
            attributes: source_name, platform_name, data_provider, interpolation_radius_of_influence'''
    import xarray
    import numpy
    from datetime import datetime, timedelta
    LOG.info('Reading SMOS data')
    # Set attributes appropriately
    wind_xarray.attrs['source_name'] = 'smos-spd'
    wind_xarray.attrs['platform_name'] = 'smos'
    wind_xarray.attrs['data_provider'] = 'esa'
    wind_xarray.attrs['interpolation_radius_of_influence'] = 25000
    # wind_xarray.attrs['sample_distance_km'] = DEG_TO_KM / 4
    wind_xarray.attrs['sample_distance_km'] = 25.0

    wind_xarray['wind_speed_kts'] = wind_xarray['wind_speed'].where(wind_xarray['quality_level'] < 2)[0, :, :]
    wind_xarray['wind_speed_kts'] = xarray.DataArray(data=numpy.flipud(wind_xarray.wind_speed_kts) * MS_TO_KTS,
                                                     name='wind_speed_kts',
                                                     coords=wind_xarray['wind_speed_kts'].coords)

    # Set lat/lons appropriately
    # These are (1440x720)
    lats2d, lons2d = numpy.meshgrid(wind_xarray.lat, wind_xarray.lon)
    # Full dataset is 720x1440x2
    wind_xarray['latitude'] = xarray.DataArray(data=numpy.flipud(lats2d.transpose()),
                                               name='latitude',
                                               coords=wind_xarray['wind_speed_kts'].coords)
    wind_xarray['longitude'] = xarray.DataArray(data=lons2d.transpose(),
                                                name='longitude',
                                                coords=wind_xarray['wind_speed_kts'].coords)
    wind_xarray = wind_xarray.set_coords(['latitude', 'longitude'])
    # timearray = numpy.zeros(wind_xarray.wind_speed_kts.shape).astype(int) + wind_xarray.time.values[0]

    timearray = numpy.ma.masked_array(data=numpy.zeros(wind_xarray.wind_speed_kts.shape).astype(int)
                                      + wind_xarray.time.values[0],
                                      mask=True)
    from numpy import datetime64, timedelta64
    from netCDF4 import Dataset
    ncobj = Dataset(fname)
    basedt = datetime64(datetime.strptime('19900101', '%Y%m%d'))
    nctimearray = numpy.flipud(ncobj.variables['measurement_time'][...][0, :, :])
    timeinds = numpy.ma.where(nctimearray)
    timedata = nctimearray[timeinds].data.tolist()
    timevals = numpy.ma.masked_array([basedt + timedelta64(timedelta(days=xx)) for xx in timedata])
    timearray[timeinds] = timevals
    wind_xarray['timestamp'] = xarray.DataArray(data=timearray,
                                                name='timestamp',
                                                coords=wind_xarray['wind_speed_kts'].coords)
    return [wind_xarray]


def sfc_winds_ncdf(fnames, metadata_only=False):
    ''' Read one of SAR, SMAP, SMOS, AMSR derived winds from netcdf data.
        Parameters:
            fnames (list): Required list of strings to full paths of netcdf files to read
        Returns:
            xarray.Dataset with required Variables and Attributes:
                Variables: 'latitude', 'longitude', 'timestamp', 'wind_speed_kts'
                Attributes: 'source_name', 'platform_name', 'data_provider', 'interpolation_radius_of_influence'
                            'start_datetime', 'end_datetime'
                Optional Attrs: 'original_source_filename', 'filename_datetime'
    '''

    from geoips2.xarray_utils.timestamp import get_min_from_xarray_timestamp, get_max_from_xarray_timestamp
    import xarray
    # Only SAR reads multiple files
    fname = fnames[0]
    wind_xarray = xarray.open_dataset(str(fname))
    wind_xarray.attrs['data_provider'] = 'unknown'
    wind_xarray.attrs['source_name'] = 'unknown'
    wind_xarray.attrs['platform_name'] = 'unknown'
    wind_xarray.attrs['interpolation_radius_of_influence'] = 'unknown'
    wind_xarray.attrs['original_source_filename'] = fname
    wind_xarray.attrs['sample_distance_km'] = 'unknown'

    LOG.info('Read data from %s', fname)

    if hasattr(wind_xarray, 'source') and 'SAR' in wind_xarray.source\
       and hasattr(wind_xarray, 'title') and 'SAR' in wind_xarray.title:
        wind_xarrays = []
        columns = None
        for fname in fnames:
            LOG.info('    Reading file %s', fname)
            wind_xarray = xarray.open_dataset(str(fname))
            LOG.info('        rows: %s, columns: %s', wind_xarray.rows, wind_xarray.columns)
            if columns is None:
                columns = wind_xarray.columns
            if columns == wind_xarray.columns:
                wind_xarrays += read_sar_data(wind_xarray)
            else:
                LOG.info('            COLUMNS DOES NOT MATCH, NOT APPENDING')
        final_xarray = xarray.Dataset()
        import numpy
        lat_array = xarray.DataArray(numpy.vstack([curr_xarray.latitude.to_masked_array()
                                                   for curr_xarray in wind_xarrays]))
        lon_array = xarray.DataArray(numpy.vstack([curr_xarray.longitude.to_masked_array()
                                                   for curr_xarray in wind_xarrays]))
        timestamp_array = xarray.DataArray(numpy.vstack([curr_xarray.timestamp.to_masked_array()
                                                         for curr_xarray in wind_xarrays]))
        wspd_array = xarray.DataArray(numpy.vstack([curr_xarray.wind_speed_kts.to_masked_array()
                                                   for curr_xarray in wind_xarrays]))
        final_xarray['latitude'] = lat_array
        final_xarray['longitude'] = lon_array
        final_xarray['timestamp'] = timestamp_array
        final_xarray['wind_speed_kts'] = wspd_array
        final_xarray.attrs = wind_xarrays[0].attrs

        wind_xarrays = [final_xarray]

    if hasattr(wind_xarray, 'institution') and 'Remote Sensing Systems' in wind_xarray.institution:
        if hasattr(wind_xarray, 'title') and 'SMAP' in wind_xarray.title:
            wind_xarrays = read_remss_data(wind_xarray, 'smap')

        if hasattr(wind_xarray, 'title') and 'WindSat' in wind_xarray.title:
            wind_xarrays = read_remss_data(wind_xarray, 'windsat')

        if hasattr(wind_xarray, 'title') and 'AMSR2' in wind_xarray.title:
            wind_xarrays = read_remss_data(wind_xarray, 'amsr2')

    if hasattr(wind_xarray, 'platform') and 'SMOS' in wind_xarray.platform:
        # SMOS timestamp is not read in correctly natively with xarray - must pass fname so we can get time
        # information directly from netCDF4.Dataset open
        wind_xarrays = read_smos_data(wind_xarray, fname)

    if hasattr(wind_xarray, 'title') and 'AMSR2_OCEAN' in wind_xarray.title:
        from geoips2.readers.amsr2_ncdf import read_amsr_winds
        wind_xarrays = read_amsr_winds(wind_xarray)

    if hasattr(wind_xarray, 'title_short_name') and 'ASCAT' in wind_xarray.title_short_name:
        wind_xarrays = read_knmi_data(wind_xarray)

    if hasattr(wind_xarray, 'title_short_name') and 'OSCAT' in wind_xarray.title_short_name:
        wind_xarrays = read_knmi_data(wind_xarray)

    if hasattr(wind_xarray, 'institution') and 'Brigham Young University' in wind_xarray.institution:
        wind_xarrays = read_byu_data(wind_xarray)

    for wind_xarray in wind_xarrays:

        if not hasattr(wind_xarray, 'minimum_coverage'):
            wind_xarray.attrs['minimum_coverage'] = 20

        LOG.info('Setting standard metadata')
        wind_xarray.attrs['start_datetime'] = get_min_from_xarray_timestamp(wind_xarray, 'timestamp')
        wind_xarray.attrs['end_datetime'] = get_max_from_xarray_timestamp(wind_xarray, 'timestamp')

        if 'wind_speed_kts' in wind_xarray.variables:
            # These text files store wind speeds natively in kts
            wind_xarray['wind_speed_kts'].attrs['units'] = 'kts'

        LOG.info('Read data %s start_dt %s source %s platform %s data_provider %s roi %s native resolution',
                 wind_xarray.attrs['start_datetime'],
                 wind_xarray.attrs['source_name'],
                 wind_xarray.attrs['platform_name'],
                 wind_xarray.attrs['data_provider'],
                 wind_xarray.attrs['interpolation_radius_of_influence'],
                 wind_xarray.attrs['sample_distance_km'])

    return wind_xarrays
