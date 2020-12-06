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

'''Output file generation based on xarray objects '''

# Python Standard Libraries
import logging

# Third Party Installed Libraries
import numpy

from geoips2.filenames.base_paths import PATHS as gpaths

LOG = logging.getLogger(__name__)

MTIF_TAG_DATA_PLATFORM_LIST = {'himawari8': 'himawari-8'}
# DATA_NAME tag depends on platform and product
MTIF_TAG_DATA_NAME_LIST = {'himawari8Infrared-Gray': 'svissr_ir1',
                           'himawari8Visible-Gray': 'svissr_vis',
                           'amsr2tb89hA': 'amsr2_89h'}
# product description  in DATA_RANGE tag depends on platform and product
MTIF_TAG_PRODUCT_DESCRIPTION_LIST = {'himawari8Infrared-Gray': 'HIMAWARI-8 IR image',
                                     'himawari8Visible-Gray': 'HIMAWARI-8 VIS image'}
MTIF_TAG_SENSORLIST = {'ahi': 'AHI'}

MTIF_FNAME_SATLIST = {'himawari8': 'hm8',
                      'gcom-w1': 'gcomw1'}
MTIF_FNAME_SENSORLIST = {'ahi': 'AHI',
                         'amsr2': 'AMSR2'}
MTIF_FNAME_PRODLIST = {'Infrared-Gray': 'ir{0:d}km',
                       'Visible-Gray': 'vis{0:d}km',
                       'tb89hA': '89hbt'}


def output_metoctiff(product_name, area_def, sect_xarray, interp_data,
                     requested_data_min=None, requested_data_max=None,
                     scale_data_min=1, scale_data_max=255, missing_value=0,
                     units=None, coverage=None, mpl_cmap=None, product_key='',
                     existing_image=None, atcf_dir='atcf'):

    output_products = []
    from geoips2.sector_utils.utils import is_sector_type
    if not is_sector_type(area_def, 'atcf'):
        LOG.warning('NOT a TC sector, skipping ATCF output')
        return output_products

    resolution = int(max(area_def.pixel_size_x, area_def.pixel_size_y) / 1000)

    from geoips2.output_formats.metoctiff import metoctiff
    from geoips2.filenames.atcf_filenames import metoctiff_filename, atcf_web_filename
    from geoips2.filenames.base_paths import PATHS as gpaths
    prodname = '{0}{1}'.format(product_name, product_key)
    start_dt = sect_xarray.start_datetime
    end_dt = sect_xarray.end_datetime

    # resolution = max(area_def.pixel_size_x, area_def.pixel_size_y) / 1000.0
    platform_filename = sect_xarray.platform_name
    source_filename = sect_xarray.source_name
    prod_filename = prodname
    mtif_tag_data_name = prodname
    mtif_tag_data_platform = sect_xarray.platform_name
    mtif_tag_product_description = 'None'
    if platform_filename in MTIF_FNAME_SATLIST.keys():
        platform_filename = MTIF_FNAME_SATLIST[sect_xarray.platform_name]
    if source_filename in MTIF_FNAME_SENSORLIST.keys():
        source_filename = MTIF_FNAME_SENSORLIST[sect_xarray.source_name]
    if prod_filename in MTIF_FNAME_PRODLIST.keys():
        if '{0:d}' in MTIF_FNAME_PRODLIST[prodname]:
            prod_filename = MTIF_FNAME_PRODLIST[prodname].format(resolution)
        else:
            prod_filename = MTIF_FNAME_PRODLIST[prodname]
    if sect_xarray.platform_name+prodname in MTIF_TAG_DATA_NAME_LIST.keys():
        # These are based off of satellite and product
        mtif_tag_data_name = MTIF_TAG_DATA_NAME_LIST[sect_xarray.platform_name+prodname]
    if mtif_tag_data_platform in MTIF_TAG_DATA_PLATFORM_LIST.keys():
        mtif_tag_data_platform = MTIF_TAG_DATA_PLATFORM_LIST[mtif_tag_data_platform]
    if sect_xarray.platform_name+prodname in MTIF_TAG_PRODUCT_DESCRIPTION_LIST.keys():
        # These are based off of satellite and product
        mtif_tag_product_description = MTIF_TAG_PRODUCT_DESCRIPTION_LIST[sect_xarray.platform_name+prodname]

    if area_def.sector_type == 'atcf':
        # Create metoctiffs from the Nearest Neighbor interpolation
        mtif_fname = metoctiff_filename(basedir=gpaths['TCWWW'],
                                        tc_year=int(area_def.sector_info['storm_year']),
                                        tc_basin=area_def.sector_info['storm_basin'],
                                        tc_stormnum=int(area_def.sector_info['storm_num']),
                                        product_name=prod_filename,
                                        source_name=source_filename,
                                        platform_name=platform_filename,
                                        coverage=coverage,
                                        product_datetime=start_dt,
                                        atcf_dir=atcf_dir)

        import math
        # I think corners may NOT be ordered.  area_extent_ll is explicitly (LL_Lon, LL_Lat, UR_Lon, UR_Lat)
        minlat = area_def.area_extent_ll[1]
        maxlat = area_def.area_extent_ll[3]
        minlon = area_def.area_extent_ll[0]
        maxlon = area_def.area_extent_ll[2]

        ullat_radians = math.radians(maxlat)
        urlat_radians = math.radians(maxlat)
        lllat_radians = math.radians(minlat)
        lrlat_radians = math.radians(minlat)

        ullon_radians = math.radians(minlon)
        urlon_radians = math.radians(maxlon)
        lllon_radians = math.radians(minlon)
        lrlon_radians = math.radians(maxlon)


        uclat_radians = ullat_radians
        lclat_radians = lllat_radians
        uclon_radians = math.radians(area_def.proj_dict['lon_0'])
        lclon_radians = math.radians(area_def.proj_dict['lon_0'])

        # 0 to 360
        # import math
        # if lllon_rad > lrlon_rad and lrlon_rad < 0:
        #     lrlon_rad = lrlon_rad + 2 * math.pi
        # if ullon_rad > urlon_rad and urlon_rad < 0:
        #     urlon_rad = urlon_rad + 2 * math.pi
        if not units:
            units = 'unk'

        if not coverage:
            coverage = 'unk'

        output_products += metoctiff(interp_data,
                                     ullat_radians,
                                     urlat_radians,
                                     lllat_radians,
                                     lrlat_radians,
                                     uclat_radians,
                                     lclat_radians,
                                     ullon_radians,
                                     urlon_radians,
                                     lllon_radians,
                                     lrlon_radians,
                                     uclon_radians,
                                     lclon_radians,
                                     data_start_datetime=start_dt,
                                     data_end_datetime=end_dt,
                                     product_name=mtif_tag_data_name,
                                     platform_name=mtif_tag_data_platform,
                                     data_units=units,
                                     output_filename=mtif_fname,
                                     requested_data_min=requested_data_min,
                                     requested_data_max=requested_data_max,
                                     scale_data_min=scale_data_min,
                                     scale_data_max=scale_data_max,
                                     missing_value=missing_value,
                                     mpl_cmap=mpl_cmap,
                                     product_description=mtif_tag_product_description,
                                     existing_image=existing_image,
                                     gzip_output=True)
    # lons, lats = area_def.get_lonlats()
    # from geoips2.xarray_utils.data import get_lat_lon_points, get_lat_lon_points_numpy
    # LOG.info('min/max lon %s %s min/max lat %s %s', lons.min(), lons.max(), lats.min(), lats.max())
    # checklat = -10; checklon = 163; diff = 0.01
    # get_lat_lon_points(checklat, checklon, diff, sect_xarray, 'B14BT')
    # get_lat_lon_points_numpy(checklat, checklon, diff, lats, lons, interp_data)
    # from IPython import embed as shell; shell()
    return output_products


def copy_standard_attrs(old_xarray, new_xarray, extra_attrs=None):
    ''' Copy the standard xarray attributes from old_xarray to new_xarray
    Args:
        old_xarray (xarray.Dataset) : Original xarray dataset
        new_xarray (xarray.Dataset) : New xarray dataset
        extra_attrs (list) : DEFAULT None, list of strings specifying desired attributes
    Returns:
        No Return, new_xarray attrs modified in place
    '''
    attrs = ['start_datetime', 'end_datetime', 'platform_name', 'source_name', 'area_def', 'data_provider',
             'interpolation_radius_of_influence']
    if extra_attrs:
        attrs += extra_attrs

    for attr in attrs:
        if attr in old_xarray.attrs.keys():
            new_xarray.attrs[attr] = old_xarray.attrs[attr]

def write_xarray_netcdf(xarray_obj, ncdf_fname):
    ''' Write out xarray_obj to netcdf file named ncdf_fname '''

    def check_attr(xobj, attr):
        if isinstance(xobj.attrs[attr], datetime):
            xobj.attrs[attr] = xobj.attrs[attr].strftime('%c')
        if xobj.attrs[attr] is None:
            xobj.attrs[attr] = str(xobj.attrs[attr])
        if isinstance(xobj.attrs[attr], bool):
            xobj.attrs[attr] = str(xobj.attrs[attr])

    from geoips2.filenames.base_paths import make_dirs
    from os.path import dirname
    make_dirs(dirname(ncdf_fname))


    orig_attrs = xarray_obj.attrs.copy()
    orig_var_attrs = {}

    from datetime import datetime
    for attr in xarray_obj.attrs.keys():
        check_attr(xarray_obj, attr)
    for varname in xarray_obj.variables.keys():
        orig_var_attrs[varname] = xarray_obj[varname].attrs.copy()
        for attr in xarray_obj[varname].attrs.keys():
            check_attr(xarray_obj[varname], attr)

    roi_str = 'none'
    if 'interpolation_radius_of_influence' in xarray_obj.attrs.keys():
        roi_str = xarray_obj.interpolation_radius_of_influence

    sdt_str = 'none'
    if 'start_datetime' in xarray_obj.attrs.keys():
        sdt_str = xarray_obj.attrs['start_datetime']

    edt_str = 'none'
    if 'end_datetime' in xarray_obj.attrs.keys():
        edt_str = xarray_obj.attrs['end_datetime']

    dp_str = 'none'
    if 'data_provider' in xarray_obj.attrs.keys():
        dp_str = xarray_obj.attrs['data_provider']

    area_def_str = 'none'
    if 'area_def' in xarray_obj.attrs.keys():
        area_def = xarray_obj.attrs.pop('area_def')
        area_def_str = repr(area_def)
        xarray_obj.attrs['area_def_str'] = area_def_str

    LOG.info('Writing xarray obj to file %s, source %s, platform %s, start_dt %s, end_dt %s, %s %s, %s %s, %s %s',
             ncdf_fname, xarray_obj.source_name, xarray_obj.platform_name, sdt_str, edt_str,
             'provider', dp_str,
             'roi', roi_str,
             'area_def', area_def_str)

    xarray_obj.to_netcdf(ncdf_fname)
    xarray_obj.attrs = orig_attrs
    for varname in xarray_obj.variables.keys():
        xarray_obj[varname].attrs = orig_var_attrs[varname]

    return [ncdf_fname]


def read_xarray_netcdf(ncdf_fname):
    import xarray
    from datetime import datetime
    xarray_obj = xarray.open_dataset(ncdf_fname)
    for attr in xarray_obj.attrs.keys():
        if 'datetime' in attr:
            xarray_obj.attrs[attr] = datetime.strptime(xarray_obj.attrs[attr], '%c')
        if attr == 'None':
            xarray_obj.attrs[attr] = None
        if attr == 'True':
            xarray_obj.attrs[attr] = True
        if attr == 'False':
            xarray_obj.attrs[attr] = False
    return xarray_obj


def output_windspeed_text(wind_xarray, area_def=None, overwrite=True, append=False, creation_time=None):
    ''' Output windspeed text file to the appropriate location, based on attributes of wind_xarray object
    Parameters:
        wind_xarray (xarray.Dataset): Required to determine attributes and data to write to text file
        sector (geoips.Sector): Optional to determine dynamic TC file location
    Returns:
        (list) list of text products generated
    '''

    output_products = []
    from geoips2.sector_utils.utils import is_sector_type
    if area_def and not is_sector_type(area_def, 'atcf'):
        LOG.warning('NOT a TC sector, skipping ATCF output')
        return output_products
    from geoips2.filenames.atcf_filenames import atcf_storm_text_windspeeds_filename, atcf_full_text_windspeeds_filename
    from geoips2.filenames.base_paths import PATHS as gpaths
    from geoips2.xarray_utils.timestamp import get_min_from_xarray_timestamp
    # start_dt = get_min_from_xarray_timestamp(wind_xarray, 'timestamp')
    start_dt = wind_xarray.start_datetime
    if area_def:
        text_fname = atcf_storm_text_windspeeds_filename(basedir=gpaths['TCWWW'],
                                                         tc_year=int(area_def.sector_info['storm_year']),
                                                         tc_basin=area_def.sector_info['storm_basin'],
                                                         tc_stormnum=int(area_def.sector_info['storm_num']),
                                                         platform_name=wind_xarray.platform_name,
                                                         product_datetime=start_dt,
                                                         data_provider=wind_xarray.data_provider)
    else:
        text_fname = atcf_full_text_windspeeds_filename(basedir=gpaths['ATCFDROPBOX'],
                                                        source_name=wind_xarray.source_name,
                                                        platform_name=wind_xarray.platform_name,
                                                        data_provider=wind_xarray.data_provider,
                                                        product_datetime=start_dt,
                                                        creation_time=creation_time)
    from os.path import exists
    if exists(text_fname) and not overwrite and not append:
        LOG.info('File already exists, not overwriting %s', text_fname)
        return output_products

    from geoips2.output_formats.text_winds import atcf_text_windspeeds

    # NOTE long does not exist in Python 3, so changed this to int.  This will
    # limit us to 32 bit integers within Python 2
    # time_array = wind_xarray['timestamp'].to_masked_array().astype(long).flatten()
    time_array = wind_xarray['timestamp'].to_masked_array().astype(int).flatten()
    # This results in an array of POSIX timestamps - seconds since epoch.
    time_array = time_array / 10**9
    wind_dir = None
    if hasattr(wind_xarray, 'wind_dir_deg_met'):
        wind_dir = wind_xarray['wind_dir_deg_met'].to_masked_array().flatten()
    atcf_text_windspeeds(text_fname,
                         wind_xarray['wind_speed_kts'].to_masked_array().flatten(),
                         time_array,
                         wind_xarray['longitude'].to_masked_array().flatten(),
                         wind_xarray['latitude'].to_masked_array().flatten(),
                         wind_xarray.platform_name,
                         dir_array=wind_dir,
                         append=append)
    output_products = [text_fname]
    return output_products


def output_geoips_fname(area_def, xarray_obj, prodname, covg, basedir=gpaths['GEOIPSFINAL'], output_type='png',
                        product_dir=None, source_dir=None):

    from geoips2.xarray_utils.timestamp import get_min_from_xarray_timestamp
    # start_dt = get_min_from_xarray_timestamp(xarray_obj, 'timestamp')
    start_dt = xarray_obj.start_datetime

    resolution = max(area_def.pixel_size_x, area_def.pixel_size_y) / 1000.0

    from geoips2.filenames.product_filenames import standard_geoips_filename
    extra = '{0:0.1f}'.format(resolution).replace('.', 'p')
    web_fname = standard_geoips_filename(basedir=basedir,
                                         product_name=prodname,
                                         source_name=xarray_obj.source_name,
                                         platform_name=xarray_obj.platform_name,
                                         sector_name=area_def.area_id,
                                         coverage=covg,
                                         resolution=resolution,
                                         product_datetime=start_dt,
                                         output_type=output_type,
                                         data_provider=xarray_obj.data_provider,
                                         extra=extra,
                                         product_dir=product_dir,
                                         source_dir=source_dir,
                                         continent=area_def.sector_info['continent'],
                                         country=area_def.sector_info['country'],
                                         area=area_def.sector_info['area'],
                                         subarea=area_def.sector_info['subarea'],
                                         state=area_def.sector_info['state'],
                                         city=area_def.sector_info['city'])
    return web_fname


def output_atcf_fname(area_def, wind_xarray, prodname, covg, output_type='png', output_type_dir=None, product_dir=None,
                      output_old_tc_web=False):

    from geoips2.sector_utils.utils import is_sector_type
    if area_def and not is_sector_type(area_def, 'atcf'):
        LOG.warning('NOT a TC sector, skipping ATCF output')
        return None

    if not product_dir:
        product_dir = prodname

    if not output_type_dir:
        output_type_dir = output_type

    # This allows you to explicitly set matplotlib parameters (colorbars, titles, etc).  Overrides were placed in
    # geoimgbase.py to allow using explicitly set values rather than geoimgbase determined defaults.
    # Return reused parameters (min/max vals for normalization, colormaps, matplotlib Normalization)
    from geoips2.output_formats.metoctiff import metoctiff
    from geoips2.filenames.atcf_filenames import metoctiff_filename, atcf_web_filename
    from geoips2.filenames.old_tcweb_fnames import old_tcweb_fnames
    from geoips2.filenames.base_paths import PATHS as gpaths
    from geoips2.xarray_utils.timestamp import get_min_from_xarray_timestamp

    # start_dt = get_min_from_xarray_timestamp(wind_xarray, 'timestamp')
    start_dt = wind_xarray.start_datetime

    resolution = max(area_def.pixel_size_x, area_def.pixel_size_y) / 1000.0

    if area_def.sector_info['wind_speed']:
        intensity = '{0:0.0f}kts'.format(area_def.sector_info['wind_speed'])
    else:
        # This is pulling intensity directly from the deck file, and sometimes it is not defined - if empty, just 
        # use "unknown" for intensity
        intensity = 'unknown'
    extra = '{0:0.1f}'.format(resolution).replace('.', 'p')

    web_fname = atcf_web_filename(basedir=gpaths['TCWWW'],
                                  tc_year=int(area_def.sector_info['storm_year']),
                                  tc_basin=area_def.sector_info['storm_basin'],
                                  tc_stormnum=int(area_def.sector_info['storm_num']),
                                  output_type=output_type,
                                  product_name=prodname,
                                  product_dir=product_dir,
                                  source_name=wind_xarray.source_name,
                                  platform_name=wind_xarray.platform_name,
                                  coverage=covg,
                                  product_datetime=start_dt,
                                  intensity=intensity,
                                  extra=extra,
                                  output_type_dir=output_type_dir)
    if output_old_tc_web is True:
        web_fname = old_tcweb_fnames(basedir=gpaths['TCWWW'],
                                     tc_year=int(area_def.sector_info['storm_year']),
                                     tc_basin=area_def.sector_info['storm_basin'],
                                     tc_stormnum=int(area_def.sector_info['storm_num']),
                                     tc_stormname=area_def.sector_info['final_storm_name'],
                                     output_type='jpg',
                                     product_name=prodname,
                                     source_name=wind_xarray.source_name,
                                     platform_name=wind_xarray.platform_name,
                                     coverage=covg,
                                     product_datetime=start_dt,
                                     intensity=intensity,
                                     extra=extra)
    return web_fname
