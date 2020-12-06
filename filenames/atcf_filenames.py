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

''' Specifications for output filename formats for atcf product types. '''

import logging

from os.path import join as pathjoin, splitext as pathsplitext
from os.path import dirname as pathdirname, basename as pathbasename
from datetime import datetime, timedelta
from glob import glob
from os import unlink as osunlink

from geoips2.data_manipulations.merge import minrange

LOG = logging.getLogger(__name__)

# These are required names for ATCF
ATCF_SOURCE_NAMES = {'gcom-w1': 'AMSR',
                     'sen1': 'SEN1',
                     'smap': 'SMAP',
                     'smos': 'SMOS',
                     'metopa': 'SCT',
                     'metopb': 'SCT',
                     'metopc': 'SCT',
                     'scatsat-1': 'SCT',
                     'coriolis': 'WSAT',
                     'radarsat2': 'SEN1'}

# ATCF_DATA_PROVIDERS = {'AMSR': 'STAR',
#                        'SEN1': 'CIRA',
#                        'RST2': 'CIRA',
#                        'SMAP': 'RSS',
#                        'SMOS': 'ESA',
#                        'SCT': 'KNMI',
#                        'WSAT': 'FNMOC'}

ATCF_DT_FORMATS = {'AMSR': '%Y%m%d%H%M',
                   'SEN1': '%Y%m%d%H%M%S',
                   'RST2': '%Y%m%d%H%M%S',
                   'AMSRamsr2rss': '%Y%m%d',
                   'SMAP': '%Y%m%d',
                   'SMOS': '%Y%m%d',
                   'SCT': '%Y%m%d',
                   'WSAT': '%Y%m%d'}
                   # 'SCT': '%Y%m%d%p'}


def atcf_web_filename_remove_duplicates(fname, mins_to_remove=10, remove_files=False):
    # 20201010_222325_WP162020_gmi_GPM_89H_40kts_14p16_1p0.png
    # 20201010_222325_WP162020_gmi_GPM_89H_40kts_14p16_1p0.png.yaml
    matching_fnames = []
    removed_fnames = []
    saved_fnames = []
    ext1 = pathsplitext(fname)[-1]
    ext2 = pathsplitext(pathsplitext(fname)[0])[-1]
    ext3 = pathsplitext(pathsplitext(pathsplitext(fname)[0])[0])[-1]
    if (ext1 == '.png') or (ext1 == '.yaml' and ext2 == '.png'):
        LOG.info('MATCHES EXT FORMAT. png or png.yaml. Attempting to remove old_tcweb duplicates')
    else:
        LOG.info('NOT REMOVING DUPLICATES. Not atcf_web filename, not png or png.yaml.')
        return [], []
    dirname = pathdirname(fname) 
    basename = pathbasename(fname)
    parts = basename.split('_')
    if len(parts) != 9:
        LOG.info('NOT REMOVING DUPLICATES. Not atcf_web filename, does not contain 9 fields.')
        return [], []
        
    try:
        # 20201010_222325_WP162020_gmi_GPM_89H_40kts_14p16_1p0.png
        yyyymmdd = parts[0]
        hhmnss = parts[1]
        stormname = parts[2]
        sensor = parts[3]
        platform = parts[4]
        product = parts[5]
        intensity = parts[6]
        coverage = parts[7]
        res = parts[8]
        if 'p' not in coverage or 'p' not in res:
            LOG.info('NOT REMOVING DUPLICATES. Not atcf_web filename, coverage or res not "NNpNN.')
            return [], []
        if 'kts' not in intensity:
            LOG.info('NOT REMOVING DUPLICATES. Not atcf_web filename, intensity does not contain "kts".')
            return [], []
    except IndexError:
        LOG.info('NOT REMOVING DUPLICATES. Unmatched filename format, incorrect number of _ delimited fields')
        return [], []
    try:
        fname_dt = datetime.strptime(yyyymmdd+hhmnss, '%Y%m%d%H%M%S')
    except ValueError:
        LOG.info('NOT REMOVING DUPLICATES. Unmatched filename format, incorrect date time string.')
        return [], []
    timediff = timedelta(minutes=mins_to_remove)
    for currdt in minrange(fname_dt - timediff, fname_dt + timediff):
        # 20201010_222325_WP162020_gmi_GPM_89H_40kts_14p16_1p0.png
        dtstr = currdt.strftime('{0}/%Y%m%d_%H%M*_{1}_{2}_{3}_{4}_*_*_{5}'.format(
                                dirname, stormname, sensor, platform, product, res))
        # print(dtstr)
        matching_fnames += glob(dtstr)
    max_coverage = 0
    for matching_fname in matching_fnames:
        # 20201010_222325_WP162020_gmi_GPM_89H_40kts_14p16_1p0.png
        parts = pathbasename(matching_fname).split('_')
        coverage = float(parts[7].replace('p', '.'))
        max_coverage = max(coverage, max_coverage)

    gotone = False
    LOG.info('CHECKING DUPLICATE FILES')
    for matching_fname in list(set(matching_fnames)):
        # 20201010_222325_WP162020_gmi_GPM_89H_40kts_14p16_1p0.png
        parts = pathbasename(matching_fname).split('_')
        coverage = float(parts[7].replace('p', '.'))
        if coverage < max_coverage or gotone is True:
            removed_fnames += [matching_fname]
            # Test it out for a bit first
            if remove_files is True:
                LOG.info('DELETING DUPLICATE FILE with less coverage %s < %s %s',
                         coverage, max_coverage, matching_fname)
                osunlink(matching_fname)
            else:
                LOG.info('TEST DELETING DUPLICATE FILE with less coverage %s < %s %s',
                         coverage, max_coverage, matching_fname)
        else:
            if len(matching_fnames) == 1:
                LOG.info('SAVING DUPLICATE FILE (only one!) with max coverage %s %s', max_coverage, matching_fname)
            else:
                LOG.info('SAVING DUPLICATE FILE with max coverage %s %s', max_coverage, matching_fname)
            saved_fnames += [matching_fname]
            gotone = True

    return removed_fnames, saved_fnames


def atcf_web_filename(basedir, tc_year, tc_basin, tc_stormnum, output_type,
                      product_name, source_name, platform_name, coverage,
                      product_datetime, intensity=None, extra=None, output_type_dir=None, product_dir=None):
    ''' Produce full output product path from product / sensor specifications.
        atcf web paths are of the format:
        <basedir>/tc<tc_year>/<tc_basin>/<tc_basin><tc_stormnum><tc_year>/<output_type>/<product_name>/<platform_name>/
        atcf web filenames are of the format:
        <date{%Y%m%d%H%M>_<tc_basin><tc_stormnum><tc_year>_<source_name>_<platform_name>_<product_name>_<intensity>_<coverage>_<extra>.<output_type>
    +------------------+-----------+---------------------------------------------------+
    | Parameters:      | Type:     | Description:                                      |
    +==================+===========+===================================================+
    | basedir:         | *str*     |                                                   |
    +------------------+-----------+---------------------------------------------------+
    | tc_year:         | *int*     | Full 4 digit storm year                           |
    +------------------+-----------+---------------------------------------------------+
    | tc_basin:        | *str*     | 2 character basin designation                     |
    |                  |           |   SH Southern Hemisphere                          |
    |                  |           |   WP West Pacific                                 |
    |                  |           |   EP East Pacific                                 |
    |                  |           |   CP Central Pacific                              |
    |                  |           |   IO Indian Ocean                                 |
    |                  |           |   AL Atlantic                                     |
    +------------------+-----------+---------------------------------------------------+
    | tc_stormnum:     | *int*     | 2 digit storm number                              |
    |                  |           |   90 through 99 for invests                       |
    |                  |           |   01 through 69 for named storms                  |
    +------------------+-----------+---------------------------------------------------+
    | output_type:     | *str*     | file extension type                               |
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
    | output_type_dir: | *str*     | Default output_type, dir name                     |
    +------------------+-----------+---------------------------------------------------+
    | product_dir:     | *str*     | Default product_name, dir name                     |
    +------------------+-----------+---------------------------------------------------+

        Return values
        ---------------
        str to full path of output filename
    '''
    if not output_type_dir:
        output_type_dir = output_type
    if not product_dir:
        product_dir = product_name
    path = pathjoin(atcf_storm_basedir(basedir, tc_year, tc_basin, tc_stormnum),
                    output_type_dir,
                    product_dir,
                    platform_name)
    fname = '_'.join([product_datetime.strftime('%Y%m%d'),
                      product_datetime.strftime('%H%M%S'),
                      '{0}{1:02d}{2:04d}'.format(tc_basin, tc_stormnum, tc_year),
                      source_name,
                      platform_name,
                      product_name,
                      str(intensity),
                      '{0:0.2f}'.format(coverage).replace('.', 'p'),
                      str(extra)])
    fname = '{0}.{1}'.format(fname, output_type)
    return pathjoin(path, fname)


def metoctiff_filename_remove_duplicates(fname, mins_to_remove=10, remove_files=False):
    # 20201010.222325.GPM.gmi.89H.WP162020.14pc.jif.gz
    # 20201010.222325.GPM.gmi.89H.WP162020.14pc.jif.gz.yaml
    matching_fnames = []
    removed_fnames = []
    saved_fnames = []
    ext1 = pathsplitext(fname)[-1]
    ext2 = pathsplitext(pathsplitext(fname)[0])[-1]
    ext3 = pathsplitext(pathsplitext(pathsplitext(fname)[0])[0])[-1]
    if (ext1 == '.gz' and ext2 == '.jif') or (ext1 == '.yaml' and ext2 == '.gz' and ext3 == '.jif'):
        LOG.info('MATCHES EXT FORMAT. .jif.gz or .jif.gz.yaml. Attempting to remove metoctiff duplicates')
    else:
        LOG.info('NOT REMOVING DUPLICATES. Not metoctiff filename, not .jif.gz or .jif.gz.yaml.')
        return [], []
    dirname = pathdirname(fname) 
    basename = pathbasename(fname)
    parts = basename.split('.')
    if (len(parts) == 10 and ext1 == '.yaml') or (len(parts) == 9 and ext1 == '.gz'):
        LOG.info('MATCHES NUMBER FIELDS. 9 or 10 fields. Attempting to remove metoctiff duplicates')
    else:
        LOG.info('NOT REMOVING DUPLICATES. Not metoctiff filename, does not contain 9 or 10 fields.')
        return [], []
        
    try:
        # 20201010.222325.GPM.gmi.89H.WP162020.14pc.jif.gz
        yyyymmdd = parts[0]
        hhmnss = parts[1]
        platform = parts[2]
        sensor = parts[3]
        product = parts[4]
        stormname = parts[5]
        coverage = parts[6]
        if 'pc' not in coverage:
            LOG.info('NOT REMOVING DUPLICATES. Not metoctiff filename, coverage not "NNpc.')
            return []
    except IndexError:
        LOG.info('NOT REMOVING DUPLICATES. Unmatched metoctiff filename format, incorrect number of . delimited fields')
        return [], []
    try:
        fname_dt = datetime.strptime(yyyymmdd+hhmnss, '%Y%m%d%H%M%S')
    except ValueError:
        LOG.info('NOT REMOVING DUPLICATES. Unmatched metoctiff filename format, incorrect date time string.')
        return [], []
    timediff = timedelta(minutes=mins_to_remove)
    for currdt in minrange(fname_dt - timediff, fname_dt + timediff):
        # 20201010.222325.GPM.gmi.19H.WP162020.14pc.jif.gz
        # Matches
        # 20201010.222325.GPM.gmi.19H.WP162020.*.jif.gz*
        dtstr = currdt.strftime('{0}/%Y%m%d.%H%M*.{1}.{2}.{3}.{4}.*.jif.gz*'.format(
                                dirname, platform, sensor, product, stormname))
        # print(dtstr)
        matching_fnames += glob(dtstr)
    max_coverage = 0
    for matching_fname in matching_fnames:
        # 20201010.222325.GPM.gmi.89H.WP162020.14pc.jif.gz
        parts = pathbasename(matching_fname).split('.')
        coverage = float(parts[6].replace('pc', ''))
        max_coverage = max(coverage, max_coverage)

    gotone = False
    LOG.info('CHECKING DUPLICATE FILES')
    for matching_fname in list(set(matching_fnames)):
        # 20201010.222325.GPM.gmi.89H.WP162020.14pc.jif.gz
        parts = pathbasename(matching_fname).split('.')
        coverage = float(parts[6].replace('pc', ''))
        if coverage < max_coverage or gotone is True:
            removed_fnames += [matching_fname]
            # Test it out for a bit first
            if remove_files is True:
                LOG.info('DELETING DUPLICATE FILE with less coverage %s < %s %s',
                         coverage, max_coverage, matching_fname)
                osunlink(matching_fname)
            else:
                LOG.info('TEST DELETING DUPLICATE FILE with less coverage %s < %s %s',
                         coverage, max_coverage, matching_fname)
        else:
            saved_fnames += [matching_fname]
            if len(matching_fnames) == 1:
                LOG.info('SAVING DUPLICATE FILE (only one!) with max coverage %s %s', max_coverage, matching_fname)
            else:
                LOG.info('SAVING DUPLICATE FILE with max coverage %s %s', max_coverage, matching_fname)
            gotone = True

    return removed_fnames, saved_fnames


def metoctiff_filename(basedir, tc_year, tc_basin, tc_stormnum,
                       product_name, source_name, platform_name, coverage,
                       product_datetime, atcf_dir='atcf'):
    ''' Produce full output product path from product / sensor specifications.
        metoctiff paths are of the format:
          <basedir>/tc<tc_year>/<tc_basin>/<tc_basin><tc_stormnum><tc_year>/atcf
        Some Terascan metoctiff filenames are of the format:
          <date{%Y%m%d>.<time{%H%M%S}>.<platform_name>.<source_name>.<product_name>.<tc_basin><tc_stormnum><tc_year>.<coverage>pc.jif
        Others are of the format:
          <date{%Y%m%d>.<time{%H%M%S}>.<platform_name>.<product_name>.<tc_basin><tc_stormnum><tc_year>.<coverage>pc.jif
        Let's go with platform and source in the filename
    +------------------+-----------+---------------------------------------------------+
    | Parameters:      | Type:     | Description:                                      |
    +==============----+===========+===================================================+
    | basedir:         | *str*     |                                                   |
    +------------------+-----------+---------------------------------------------------+
    | tc_year:         | *int*     | Full 4 digit storm year                           |
    +------------------+-----------+---------------------------------------------------+
    | tc_basin:        | *str*     | 2 character basin designation                     |
    |                  |           |   SH Southern Hemisphere                          |
    |                  |           |   WP West Pacific                                 |
    |                  |           |   EP East Pacific                                 |
    |                  |           |   CP Central Pacific                              |
    |                  |           |   IO Indian Ocean                                 |
    |                  |           |   AL Atlantic                                     |
    +------------------+-----------+---------------------------------------------------+
    | tc_stormnum:     | *int*     | 2 digit storm number                              |
    |                  |           |   90 through 99 for invests                       |
    |                  |           |   01 through 69 for named storms                  |
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
    | atcf_dir:        | *str*     | DEFAULT 'atcf': subdirectory for mtifs, 'atcf' is |
    |                  |           |   the "operational" directory                     |
    +------------------+-----------+---------------------------------------------------+

        Return values
        ---------------
        str to full path of output filename
    '''

    path = pathjoin(atcf_storm_basedir(basedir, tc_year, tc_basin, tc_stormnum),
                    atcf_dir)
    fname = '.'.join([product_datetime.strftime('%Y%m%d'),
                      product_datetime.strftime('%H%M%S'),
                      platform_name,
                      source_name,
                      product_name,
                      '{0}{1:02d}{2:04d}'.format(tc_basin, tc_stormnum, tc_year),
                      '{0:0.0f}pc'.format(coverage),
                      'jif'])
    return pathjoin(path, fname)


def atcf_full_text_windspeeds_filename(basedir, source_name, platform_name,
                                       data_provider, product_datetime,
                                       creation_time=None): 
    ''' Produce full output product path from product / sensor specifications.

        Parameters:
            basedir (str) :  base directory
            num_points(int) :  Number of points (lines) included in the text file
            source_name (str) : Name of source (sensor)
            platform_name (str) : Name of platform (satellite)
            data_provider (str) : Name of data provider
            product_datetime (datetime) : Start time of data used to generate product
            creation_time (datetime) : Default None: Include given creation_time of file in filename

        Returns:
            str: to full path of output filename of the format:
              <basedir>/<ATCF_SOURCE_NAME>_winds_<DATA_PROVIDER>_<YYYYMMDDHHMN>
             
            NOTE: ATCF_SOURCE_NAME is based off of the platform name
                gcom-w1 = AMSR
                sen1    = SEN1
                smap    = SMAP
                smos    = SMOS

            NOTE: DATA_PROVIDER is based of of ATCF_SOURCE_NAME
                AMSR    = STAR
                SMAP    = RSS
                SMOS    = ESA
                SEN1    = CIRA

        Usage:
            >>> startdt = datetime.strptime('20200216T001412', '%Y%m%dT%H%M%S')
            >>> atcf_storm_text_windspeeds_filename('/outdir', 'smap', startdt)
            '/outdir/SMAP_winds_RSS_202002160014'
    '''

    atcf_source_name = ATCF_SOURCE_NAMES[platform_name]
    atcf_dt_str = ATCF_DT_FORMATS[atcf_source_name]
    if atcf_source_name+source_name in ATCF_DT_FORMATS:
        atcf_dt_str = ATCF_DT_FORMATS[atcf_source_name+source_name]

    fname = '_'.join([atcf_source_name,
                      data_provider,
                      platform_name,
                      'surface_winds',
                      product_datetime.strftime(atcf_dt_str)])
    from datetime import datetime
    if creation_time is not None:
        fname = fname+'_creationtime_'+creation_time.strftime('%Y%m%dT%H%MZ')
                      
    return pathjoin(basedir, fname)


def atcf_metadata_dir(basedir, tc_year, tc_basin, tc_stormnum, metadata_type, metadata_datetime,
                      metadata_dir='metadata'):
    ''' Produce ATCF metadata directory

    Args:
        basedir (str) :  base directory
        tc_year (int) :  Full 4 digit storm year
        tc_basin (str) :  2 character basin designation
                               SH Southern Hemisphere
                               WP West Pacific
                               EP East Pacific
                               CP Central Pacific
                               IO Indian Ocean
                               AL Atlantic
        tc_stormnum (int) : 2 digit storm number
                               90 through 99 for invests
                               01 through 69 for named storms
        metadata_type (str) : metadata subdirectory to contain metadata files - same basename as product filename
                                One of ['sector', 'archer', 'storm']
        metadata_datetime (datetime) : datetime associated with the metadata
        metadata_dir (str) : DEFAULT 'metadata'. Directory name for all metadata - using non-default allows for a
                                                 separate directory for "non-operational" test products.
    Returns:
        (str) : Path to metadata directory
    '''

    allowed_metadata_types = ['sector_information', 'archer_information', 'storm_information']

    if metadata_type not in allowed_metadata_types:
        raise TypeError('Unknown metadata type {0}, allowed {1}'.format(metadata_type, allowed_metadata_types))

    path = pathjoin(atcf_storm_basedir(basedir, tc_year, tc_basin, tc_stormnum),
                    metadata_dir,
                    metadata_type,
                    metadata_datetime.strftime('%Y%m%d'))
    return path


def atcf_storm_basedir(basedir, tc_year, tc_basin, tc_stormnum):
    ''' Produce base storm directory for ATCF web output

    Args:
        basedir (str) :  base directory
        tc_year (int) :  Full 4 digit storm year
        tc_basin (str) :  2 character basin designation
                               SH Southern Hemisphere
                               WP West Pacific
                               EP East Pacific
                               CP Central Pacific
                               IO Indian Ocean
                               AL Atlantic
        tc_stormnum (int) : 2 digit storm number
                               90 through 99 for invests
                               01 through 69 for named storms
    Returns:
        (str) : Path to base storm web directory
    '''
    path = pathjoin(basedir,
                    'tc{0:04d}'.format(tc_year),
                    tc_basin,
                    '{0}{1:02d}{2:04d}'.format(tc_basin, tc_stormnum, tc_year))
    return path


def atcf_storm_text_windspeeds_filename(basedir, tc_year, tc_basin, tc_stormnum,
                                        platform_name, product_datetime, data_provider):
    ''' Produce full output product path from product / sensor specifications.

        Args:
            basedir (str) :  base directory
            tc_year (int) :  Full 4 digit storm year
            tc_basin (str) :  2 character basin designation
                                   SH Southern Hemisphere
                                   WP West Pacific
                                   EP East Pacific
                                   CP Central Pacific
                                   IO Indian Ocean
                                   AL Atlantic
            tc_stormnum (int) : 2 digit storm number
                                   90 through 99 for invests
                                   01 through 69 for named storms
            platform_name (str) : Name of platform (satellite)
            product_datetime (datetime) : Start time of data used to generate product

        Returns:
            str: to full path of output filename of the format:
              <basedir>/tc<tc_year>/<tc_basin>/<tc_basin><tc_stormnum><tc_year>/txt/
              <ATCF_SOURCE_NAME>_winds_<DATA_PROVIDER>_<YYYYMMDDHHMN>

            NOTE: ATCF_SOURCE_NAME is based off of the platform name
                gcom-w1 = AMSR
                sen1    = SEN1
                smap    = SMAP
                smos    = SMOS

        Usage:
            >>> startdt = datetime.strptime('20200216T001412', '%Y%m%dT%H%M%S')
            >>> atcf_storm_text_windspeeds_filename('/outdir', 2020, 'SH', 16, 'smap', startdt)
            '/outdir/tc2020/SH/SH162020/txt/
    '''

    atcf_source_name = ATCF_SOURCE_NAMES[platform_name]
    # atcf_data_provider = data_provider
    # if data_provider is None:
    #     atcf_data_provider = ATCF_DATA_PROVIDERS[atcf_source_name]

    path = pathjoin(atcf_storm_basedir(basedir, tc_year, tc_basin, tc_stormnum),
                    'txt')
    fname = '_'.join([atcf_source_name,
                      'winds',
                      data_provider,
                      platform_name,
                      '{0}{1:02d}'.format(tc_basin, tc_stormnum),
                      product_datetime.strftime('%Y%m%d%H%M')])
    return pathjoin(path, fname)
