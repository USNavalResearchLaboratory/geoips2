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

''' Specifications for output filename formats for various product types. '''

import logging
from os.path import join as pathjoin

LOG = logging.getLogger(__name__)


def standard_geoips_filename_remove_duplicates(fname, mins_to_remove=10, remove_files=False):
    LOG.info('MUST ADD LOGIC TO REMOVE STANDARD GEOIPS FILENAME DUPLICATES')
    return [], []


def standard_geoips_filename(basedir, product_name, source_name, platform_name, sector_name,
                             coverage, resolution, product_datetime,
                             output_type='png', data_provider=None, extra=None, product_dir=None, source_dir=None,
                             continent=None, country=None, area=None, subarea=None, state=None, city=None):
                            
    ''' Produce full output product path from product / sensor specifications.
        standard web paths are of the format:
       '<basedir>/<continent>-<country>-<area>/<subarea>-<state>-<city>/<productname>/<sensorname>
        standard filenames are of the format:
        <date{%Y%m%d}>.<time{%H%M%S}>.<satname>.<sensorname>.<productname>.<sectorname>.<coverage>.<dataprovider>.<extra>
    +------------------+-----------+---------------------------------------------------+
    | Parameters:      | Type:     | Description:                                      |
    +==================+===========+===================================================+
    | basedir:         | *str*     |                                                   |
    +------------------+-----------+---------------------------------------------------+
    | product_name:    | *str*     | Name of product                                   |
    +------------------+-----------+---------------------------------------------------+
    | source_name:     | *str*     | Name of data source (sensor)                      |
    +------------------+-----------+---------------------------------------------------+
    | platform_name:   | *str*     | Name of platform (satellite)                      |
    +------------------+-----------+---------------------------------------------------+
    | coverage:        | *float*   | Image coverage, float between 0.0 and 100.0       |
    +------------------+-----------+---------------------------------------------------+
    | resolution:      | *float*   | Image resolution, float greater than 0.0          |
    +------------------+-----------+---------------------------------------------------+
    | product_datetime:| *datetime*| Datetime object - start time of data used to      |
    |                  |           |     generate product                              |
    +------------------+-----------+---------------------------------------------------+

    +------------------+-----------+---------------------------------------------------+
    | Key Word Args:   | Type:     | Description:                                      |
    +==================+===========+===================================================+
    | output_type:     | *str*     | file extension type                               |
    +------------------+-----------+---------------------------------------------------+
    | data_provider:   | *str*     |                                                   |
    +------------------+-----------+---------------------------------------------------+
    | extra:           | *str*     |                                                   |
    +------------------+-----------+---------------------------------------------------+
    | continent:       | *str*     |                                                   |
    +------------------+-----------+---------------------------------------------------+
    | country:         | *str*     |                                                   |
    +------------------+-----------+---------------------------------------------------+
    | area:            | *str*     |                                                   |
    +------------------+-----------+---------------------------------------------------+
    | subarea:         | *str*     |                                                   |
    +------------------+-----------+---------------------------------------------------+
    | state:           | *str*     |                                                   |
    +------------------+-----------+---------------------------------------------------+
    | city:            | *str*     |                                                   |
    +------------------+-----------+---------------------------------------------------+
    '''
    fillval = 'x'
    if continent is None:
        continent = fillval
    if country is None:
        country = fillval
    if area is None:
        area = fillval
    if subarea is None:
        subarea = fillval
    if state is None:
        state = fillval
    if city is None:
        city = fillval
    if data_provider is None:
        data_provider = fillval
    if extra is None:
        extra = fillval
    if product_dir is None:
        product_dir = product_name
    if source_dir is None:
        source_dir = source_name
    path = pathjoin(basedir,
                    '{0}-{1}-{2}'.format(continent, country, area),
                    '{0}-{1}-{2}'.format(subarea, state, city),
                    product_dir,
                    source_dir)
                    # source_dir,
                    # '{0:0.1f}'.format(resolution).replace('.', 'p'))
    # fname = '<date{%Y%m%d}>.<time{%H%M%S}>.<satname>.<sensorname>.<productname>.<sectorname>.
    #          <coverage>.<dataprovider>.<extra>'
    fname = '.'.join([product_datetime.strftime('%Y%m%d'),
                      product_datetime.strftime('%H%M%S'),
                      platform_name,
                      source_name,
                      product_name,
                      sector_name,
                      '{0:0.2f}'.format(coverage).replace('.', 'p'),
                      data_provider,
                      str(extra)])
    fname = '{0}.{1}'.format(fname, output_type)
    return pathjoin(path, fname)


def netcdf_write_geolocation_filename(basedir, sector_name):
                                     
    ''' Produce full output path for sector-based netcdf files of geolocation information
        netcdf geolocation paths are of the format:
          <basedir>/<sector_name>.nc
    +------------------+-----------+---------------------------------------------------+
    | Parameters:      | Type:     | Description:                                      |
    +==============----+===========+===================================================+
    | basedir:         | *str*     |                                                   |
    +------------------+-----------+---------------------------------------------------+
    | sector_name:     | *str*     | Name of sector                                    |
    +------------------+-----------+---------------------------------------------------+
    '''

    path = pathjoin(basedir,
                    sector_name+'.nc')
    return path


def netcdf_write_filename(basedir, product_name, source_name, platform_name,
                          sector_name,product_datetime,set_subpath=None, time_format='%H%M%S'):
    ''' Produce full output product path from product / sensor specifications.
        netcdf paths are of the format:
          <basedir>/<product_name>/<source_name>/<platform_name>/<sector_name>/date{%Y%m%d}
        netcdf filenames are of the format:
          <date{%Y%m%d>.<time{%H%M%S}>.<platform_name>.<product_name>.<sector_name>.nc
    +------------------+-----------+---------------------------------------------------+
    | Parameters:      | Type:     | Description:                                      |
    +==============----+===========+===================================================+
    | basedir:         | *str*     |                                                   |
    +------------------+-----------+---------------------------------------------------+
    | product_name:    | *str*     | Name of product                                   |
    +------------------+-----------+---------------------------------------------------+
    | source_name:     | *str*     | Name of data source (sensor)                      |
    +------------------+-----------+---------------------------------------------------+
    | platform_name:   | *str*     | Name of platform (satellite)                      |
    +------------------+-----------+---------------------------------------------------+
    | coverage:        | *float*   | Image coverage, float between 0.0 and 100.0       |
    +------------------+-----------+---------------------------------------------------+
    | product_datetime:| *datetime*| Datetime object - start time of data used to      |
    |                  |           |     generate product                              |
    +------------------+-----------+---------------------------------------------------+
    '''

    if set_subpath:
        path = pathjoin(basedir,set_subpath)
    else:
        path = pathjoin(basedir,
                        product_name,
                        source_name,
                        platform_name,
                        sector_name,
                        product_datetime.strftime('%Y%m%d'))
    fname = '.'.join([product_datetime.strftime('%Y%m%d'),
                      product_datetime.strftime(time_format),
                      platform_name,
                      product_name,
                      sector_name,
                      'nc'])
    return pathjoin(path, fname)
