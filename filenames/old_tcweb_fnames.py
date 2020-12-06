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

# Python Standard Libraries
import logging

import os
from os.path import join as pathjoin, splitext as pathsplitext
from os.path import dirname as pathdirname, basename as pathbasename
from datetime import datetime, timedelta
from glob import glob
from os import unlink as osunlink

from geoips2.data_manipulations.merge import minrange

LOG = logging.getLogger(__name__)


def old_tcweb_fnames_remove_duplicates(fname, mins_to_remove=10, remove_files=False):
    # 20201010.222325.WP162020.gmi.GPM.37V.40kts.14p2.1p0.jpg
    # 20201010.222325.WP162020.gmi.GPM.89H.40kts.14p2.1p0.jpg.yaml
    matching_fnames = []
    removed_fnames = []
    saved_fnames = []
    ext1 = pathsplitext(fname)[-1]
    ext2 = pathsplitext(pathsplitext(fname)[0])[-1]
    ext3 = pathsplitext(pathsplitext(pathsplitext(fname)[0])[0])[-1]
    if (ext1 == '.jpg') or (ext1 == '.yaml' and ext2 == '.jpg'):
        LOG.info('MATCHES EXT FORMAT. jpg or jpg.yaml. Attempting to remove old_tcweb duplicates')
    else:
        LOG.info('NOT REMOVING DUPLICATES. Not old_tcweb filename, not jpg or jpg.yaml.')
        return [], []

    dirname = pathdirname(fname) 
    basename = pathbasename(fname)
    # 20201010.222325.WP162020.gmi.GPM.37V.40kts.14p2.1p0.jpg
    parts = basename.split('.')
    if (len(parts) == 10 and ext1 == '.yaml') or (len(parts) == 9 and ext1 == '.jpg'):
        LOG.info('NOT REMOVING DUPLICATES. Not old_tcweb filename, does not contain 9 or 10 fields.')
        return [], []
        
    try:
        # 20201010.222325.WP162020.gmi.GPM.37V.40kts.14p2.1p0.jpg
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
            LOG.info('NOT REMOVING DUPLICATES. Not old_tcweb filename, coverage or res not "NNpN.')
            return [], []
        if 'kts' not in intensity:
            LOG.info('NOT REMOVING DUPLICATES. Not old_tcweb filename, intensity does not contain "kts".')
            return [], []
    except IndexError:
        LOG.info('NOT REMOVING DUPLICATES. Unmatched filename format, incorrect number of . delimited fields')
        return [], []
    try:
        fname_dt = datetime.strptime(yyyymmdd+hhmnss, '%Y%m%d%H%M%S')
    except ValueError:
        LOG.info('NOT REMOVING DUPLICATES. Unmatched old_tcweb filename format, incorrect date time string.')
        return [], []
    timediff = timedelta(minutes=mins_to_remove)
    for currdt in minrange(fname_dt - timediff, fname_dt + timediff):
        # 20201010.222325.WP162020.gmi.GPM.37V.40kts.14p2.1p0.jpg
        # 20201010.222325.WP162020.gmi.GPM.37V.*.*.1p0.jpg*
        dtstr = currdt.strftime('{0}/%Y%m%d.%H%M*.{1}.{2}.{3}.{4}.*.*.{5}.jpg*'.format(
                                dirname, stormname, sensor, platform, product, res))
        # print(dtstr)
        matching_fnames += glob(dtstr)
    max_coverage = 0
    for matching_fname in matching_fnames:
        # 20201010.222325.WP162020.gmi.GPM.37V.40kts.14p2.1p0.jpg
        parts = pathbasename(matching_fname).split('.')
        coverage = float(parts[7].replace('p', '.'))
        max_coverage = max(coverage, max_coverage)

    gotone = False
    LOG.info('CHECKING DUPLICATE FILES')
    for matching_fname in list(set(matching_fnames)):
        # 20201010.222325.WP162020.gmi.GPM.37V.40kts.14p2.1p0.jpg
        parts = pathbasename(matching_fname).split('.')
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


''' Specifications for output filename formats for the old TC Web structure. '''
def old_tcweb_fnames(basedir, tc_year, tc_basin, tc_stormnum, tc_stormname, output_type,
                     product_name, source_name, platform_name, coverage,
                     product_datetime, intensity=None, extra=None):
    ''' Produce full output product path from product / sensor specifications.
        tc web paths for IR/VIS products are of the format:
        <basedir>/<continent>/<area>/<subarea>/<mapped_productname>/<source_name>/<resolution>
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
    | tc_stormname:    | *str*     | Storm name                                        |
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
    '''
    basin_names = {'SH': 'SHEM',
                   'WP': 'WPAC',
                   'EP': 'EPAC',
                   'CP': 'CPAC',
                   'IO': 'IO',
                   'AL': 'ATL', }

    basin_letters = {'ATL': ['L'],
                     'CPAC': ['C'],
                     'EPAC': ['E'],
                     'IO': ['A', 'B'],
                     'SHEM': ['S', 'P'],
                     'WPAC': ['W']}

    product_dir_names = {
                         'Infrared': 'ir',
                         'Visible': 'vis',
                         'Vapor': 'vapor',
                         '37H': '36h',
                         '37V': '36v',
                         '89H': '89h',
                         '89V': '89',
                         'windspeed': 'wind',
                         '89pct': 'pct',
                         'color37': 'color36',
                         'color89': 'color',
                         'metoctiff': 'atcf',
                         'Rain': 'rain',
                         'ssmi37H': '37h',
                         'ssmi37V': '37v',
                         'ssmi89H': '85h',
                         'ssmicolor37': 'color37',
                         'ssmis37H': '37h',
                         'ssmis37V': '37v',
                         'ssmis89H': '91h',
                         'ssmiscolor37': 'color37',
                         'windsatcolor37': 'color37',
                         }
    source_dir_names = {'amsr2': 'amsr2',
                        'gmi': 'gmi',
                        'windsat': 'windsat',
                        'wsat': 'windsat',
                        'imerg': 'gmi',
                        'ssmi': 'ssmi',
                        'amsub': 'amsub',
                        'ssmis': 'tc_ssmis'}
    product_subdir_names = {'37H': '',
                            '37V': '',
                            '89pct': '',
                            'color37': '',
                            'windspeed': '2degreeticks',
                            'color89': '2degreeticks',
                            '89H': '2degreeticks',
                            '89V': '2degreeticks',
                            'Rain': ''
                            }

    mapped_tc_year = '{0:4s}'.format(str(tc_year))[2:4] 
    if product_name not in product_dir_names\
       or source_name not in source_dir_names\
       or product_name not in product_subdir_names:
        LOG.info('Product / Source not supported for old TC web output, add to dictionaries: %s %s',
                 product_name, source_name)
        return None

    basin_letter = None
    for curr_basin_letter in basin_letters[basin_names[tc_basin]]:
        curr_path = pathjoin(basedir,
                            'tc{0}'.format(mapped_tc_year),
                            basin_names[tc_basin],
                            '{0:02d}{1}.{2}'.format(tc_stormnum, curr_basin_letter, tc_stormname.upper()))
        if os.path.exists(curr_path):
            basin_letter = curr_basin_letter

    if not basin_letter:
        LOG.info('Path does not exist %s, not trying to output to old tc web', curr_path)
        return None

    product_dir_name = product_dir_names[product_name]
    if source_name+product_name in product_dir_names:
        product_dir_name = product_dir_names[source_name+product_name]
    
    path = pathjoin(basedir,
                    'tc{0}'.format(mapped_tc_year),
                    basin_names[tc_basin],
                    '{0:02d}{1}.{2}'.format(tc_stormnum, basin_letter, tc_stormname.upper()),
                    source_dir_names[source_name],
                    product_dir_name,
                    product_subdir_names[product_name])
    fname = '.'.join([product_datetime.strftime('%Y%m%d'),
                      product_datetime.strftime('%H%M%S'),
                      '{0}{1:02d}{2:04d}'.format(tc_basin, tc_stormnum, tc_year),
                      source_name,
                      platform_name,
                      product_name,
                      str(intensity),
                      '{0:0.1f}'.format(coverage).replace('.', 'p'),
                      str(extra)])
    fname = '{0}.{1}'.format(fname, output_type)
    return pathjoin(path, fname)

