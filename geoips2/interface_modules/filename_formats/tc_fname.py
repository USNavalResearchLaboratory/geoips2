# # # DISTRIBUTION STATEMENT A. Approved for public release: distribution unlimited.
# # # 
# # # Author:
# # # Naval Research Laboratory, Marine Meteorology Division
# # # 
# # # This program is free software: you can redistribute it and/or modify it under
# # # the terms of the NRLMMD License included with this program.  If you did not
# # # receive the license, see http://www.nrlmry.navy.mil/geoips for more
# # # information.
# # # 
# # # This program is distributed WITHOUT ANY WARRANTY; without even the implied
# # # warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# # # included license for more details.

'''Standard TC filename production'''

# Python Standard Libraries
import logging

from os.path import join as pathjoin, splitext as pathsplitext
from os.path import dirname as pathdirname, basename as pathbasename, exists as pathexists
from datetime import datetime, timedelta
from glob import glob
from os import unlink as osunlink

from geoips2.filenames.base_paths import PATHS as gpaths
from geoips2.data_manipulations.merge import minrange

LOG = logging.getLogger(__name__)

filename_type = 'standard'


def tc_fname(area_def, xarray_obj, product_name, coverage, output_type='png', output_type_dir=None,
             product_dir=None, product_subdir=None, source_dir=None, basedir=gpaths['TCWWW'],
             extra_field=None, output_dict=None):

    from geoips2.sector_utils.utils import is_sector_type
    if area_def and not is_sector_type(area_def, 'tc'):
        LOG.warning('NOT a TC sector, skipping TC output')
        return None

    if not product_dir:
        product_dir = product_name

    if not output_type_dir:
        output_type_dir = output_type

    # This allows you to explicitly set matplotlib parameters (colorbars, titles, etc).  Overrides were placed in
    # geoimgbase.py to allow using explicitly set values rather than geoimgbase determined defaults.
    # Return reused parameters (min/max vals for normalization, colormaps, matplotlib Normalization)
    from geoips2.filenames.base_paths import PATHS as gpaths
    from geoips2.xarray_utils.timestamp import get_min_from_xarray_timestamp

    # start_dt = get_min_from_xarray_timestamp(xarray_obj, 'timestamp')
    start_dt = xarray_obj.start_datetime

    resolution = max(area_def.pixel_size_x, area_def.pixel_size_y) / 1000.0

    if area_def.sector_info['vmax']:
        intensity = '{0:0.0f}kts'.format(area_def.sector_info['vmax'])
    else:
        # This is pulling intensity directly from the deck file, and sometimes it is not defined - if empty, just 
        # use "unknown" for intensity
        intensity = 'unknown'
    extra = '{0:0.1f}'.format(resolution).replace('.', 'p')
    from geoips2.dev.product import get_covg_args_from_product

    if 'source_names' in xarray_obj.attrs:
        for source_name in xarray_obj.source_names:
            try:
                covg_args = get_covg_args_from_product(product_name, source_name,
                                                       output_dict=output_dict)
            except KeyError:
                continue
    else:
        covg_args = get_covg_args_from_product(product_name, xarray_obj.source_name,
                                               output_dict=output_dict)

    if 'radius_km' in covg_args or ('filename_extra_fields' in xarray_obj.attrs and xarray_obj.filename_extra_fields):
        extra = f"res{extra}"
    if 'radius_km' in covg_args:
        extra = f"{extra}-cr{covg_args['radius_km']}"
    if 'filename_extra_fields' in xarray_obj.attrs and xarray_obj.filename_extra_fields:
        for field in xarray_obj.filename_extra_fields:
            extra = f"{extra}-{xarray_obj.filename_extra_fields[field]}"

    if extra_field:
        extra = f'{extra}-{extra_field}'

    web_fname = assemble_tc_fname(basedir=basedir,
                                  tc_year=int(area_def.sector_info['storm_year']),
                                  tc_basin=area_def.sector_info['storm_basin'],
                                  tc_stormnum=int(area_def.sector_info['storm_num']),
                                  output_type=output_type,
                                  product_name=product_name,
                                  product_dir=product_dir,
                                  product_subdir=product_subdir,
                                  source_name=xarray_obj.source_name,
                                  platform_name=xarray_obj.platform_name,
                                  coverage=coverage,
                                  product_datetime=start_dt,
                                  intensity=intensity,
                                  extra=extra,
                                  output_type_dir=output_type_dir)
    return web_fname


def tc_fname_remove_duplicates(fname, mins_to_remove=10, remove_files=False):
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
        LOG.info('NOT REMOVING DUPLICATES. Not tc_web filename, not png or png.yaml.')
        return [], []
    dirname = pathdirname(fname) 
    basename = pathbasename(fname)
    parts = basename.split('_')
    if len(parts) != 9:
        LOG.info('NOT REMOVING DUPLICATES. Not tc_web filename, does not contain 9 fields.')
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
            LOG.info('NOT REMOVING DUPLICATES. Not tc_web filename, coverage or res not "NNpNN.')
            return [], []
        if 'kts' not in intensity:
            LOG.info('NOT REMOVING DUPLICATES. Not tc_web filename, intensity does not contain "kts".')
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
                try:
                    osunlink(matching_fname)
                except FileNotFoundError as resp:
                    LOG.warning('FAILDELETE %s: File %s did not exist, someone must have deleted it for us?',
                                matching_fname, str(resp))

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


def assemble_tc_fname(basedir, tc_year, tc_basin, tc_stormnum, output_type,
                      product_name, source_name, platform_name, coverage,
                      product_datetime, intensity=None, extra=None, output_type_dir=None,
                      product_dir=None, product_subdir=None):
    ''' Produce full output product path from product / sensor specifications.
        tc web paths are of the format:
        <basedir>/tc<tc_year>/<tc_basin>/<tc_basin><tc_stormnum><tc_year>/<output_type>/<product_name>/<platform_name>/
        tc web filenames are of the format:
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
    if not product_subdir:
        product_subdir = platform_name

    from geoips2.interface_modules.filename_formats.utils.tc_file_naming import tc_storm_basedir
    path = pathjoin(tc_storm_basedir(basedir, tc_year, tc_basin, tc_stormnum),
                    output_type_dir,
                    product_dir,
                    product_subdir)
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


