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

''' Routines for outputting formatted text wind speed and vector data files '''
import logging
import os
from datetime import datetime
import numpy

LOG = logging.getLogger(__name__)

# These are required names for ATCF rendering
ATCF_SOURCE_NAMES = {'gcom-w1': 'AMSR',
                     'sen1': 'SEN1',
                     'radarsat2': 'RST2',
                     'smap': 'SMAP',
                     'smos': 'SMOS',
                     'metopa': 'SCT',
                     'metopb': 'SCT',
                     'metopc': 'SCT',
                     'scatsat-1': 'SCT',
                     'coriolis': 'WSAT'}


def atcf_text_windspeeds(fname, speed_array, time_array, lon_array, lat_array, platform_name, dir_array=None,
                         append=False):
    ''' Write out ATCF formatted text file of wind speeds
        +------------------+-----------+-------------------------------------------------------+
        | Parameters:      | Type:     | Description:                                          |
        +==================+===========+=======================================================+
        | fname:           | *str*     | String full path to output filename                   |
        +------------------+-----------+-------------------------------------------------------+
        | speed_array:     | *ndarray* | array of windspeeds                                   |
        +------------------+-----------+-------------------------------------------------------+
        | time_array:      | *ndarray* | array of POSIX time stamps same length as speed_array |
        +------------------+-----------+-------------------------------------------------------+
        | lon_array:       | *ndarray* | array of longitudes of same length as speed_array     |
        +------------------+-----------+-------------------------------------------------------+
        | lat_array:       | *ndarray* | array of latitudes of same length as speed_array      |
        +------------------+-----------+-------------------------------------------------------+
        | platform_name:   | *str*     | String platform name                                  |
        +------------------+-----------+-------------------------------------------------------+
    '''
    output_products = []
    if not isinstance(platform_name, str):
        raise TypeError('Parameter platform_name must be a str')
    if not isinstance(fname, str):
        raise TypeError('Parameter fname must be a str')
    if not isinstance(speed_array, numpy.ndarray):
        raise TypeError('Parameter speed_array must be a numpy.ndarray of wind speeds')
    if not isinstance(lat_array, numpy.ndarray):
        raise TypeError('Parameter lat_array must be a numpy.ndarray of latitudes')
    if not isinstance(lon_array, numpy.ndarray):
        raise TypeError('Parameter lon_array must be a numpy.ndarray of longitudes')
    if not isinstance(time_array, numpy.ndarray):
        raise TypeError('Parameter time_array must be a numpy.ndarray of POSIX timestamps')

    source_name = ATCF_SOURCE_NAMES[platform_name].upper()

    from geoips2.filenames.base_paths import make_dirs
    make_dirs(os.path.dirname(fname))
    if hasattr(speed_array, 'mask'):
        if dir_array is not None:
            newmask = speed_array.mask | time_array.mask | lat_array.mask | lon_array.mask | dir_array.mask
        else:
            newmask = speed_array.mask | time_array.mask | lat_array.mask | lon_array.mask
        inds = numpy.ma.where(~newmask)
        speed_array = speed_array[inds]
        time_array = time_array[inds]
        lon_array = lon_array[inds]
        lat_array = lat_array[inds]
        if dir_array is not None:
            dir_array = dir_array[inds] 

    openstr = 'w'
    if append:
        openstr = 'a'
    startdt_str = datetime.utcfromtimestamp(time_array[0]).strftime('%Y%m%d%H%M')
    header = ''
    if not os.path.exists(fname):
        header = 'METXSCT {0} ASC (FULL DAY)\n'.format(startdt_str)
    with open(fname, openstr) as fobj:
        if dir_array is not None:
            fobj.write(header)
            for speed, time, lon, lat, direction in zip(speed_array, time_array, lon_array, lat_array, dir_array):
                # dtstr = time.strftime('%Y%m%d%H%M')
                dtstr = datetime.utcfromtimestamp(time).strftime('%Y%m%d%H%M')
                # if lon > 180:
                #     lon = lon - 360
                format_string = ' {0:>3s} {1:>8.1f} {2:>6.1f} {3:>3d} {4:>3d} {5:s}\n'
                fobj.write(format_string.format(source_name,
                                                lat,
                                                lon,
                                                int(direction),
                                                int(speed),
                                                dtstr))
        else:
            for speed, time, lon, lat in zip(speed_array, time_array, lon_array, lat_array):
                # dtstr = time.strftime('%Y%m%d%H%M')
                dtstr = datetime.utcfromtimestamp(time).strftime('%Y%m%d%H%M')
                # if lon > 180:
                #     lon = lon - 360
                format_string = '{0:>6s}{1:>8.2f}{2:>8.2f}{3:>4d} {4:s}\n'
                if source_name == 'SMAP' or source_name == 'SMOS':
                    format_string = ' {0:<6s} {1:>5.1f} {2:>5.1f} {3:>3d} {4:s}\n'
                fobj.write(format_string.format(source_name,
                                                lat,
                                                lon,
                                                int(speed),
                                                dtstr))
    import subprocess
    lsfulltime = subprocess.check_output(['ls', '--full-time', fname])
    LOG.info('WINDTEXTSUCCESS wrote out text windspeed file %s', lsfulltime)
    output_products = [fname]
    return output_products
