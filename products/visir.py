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

''' Template for external algorithms, allowing for bypassing much of the GeoIPS 1.0 processing infrastructure '''

# Python Standard Libraries
import logging

# Third Party Installed Libraries
import numpy
import xarray

from geoips2.filenames.base_paths import PATHS as gpaths
from geoips2.sector_utils.utils import is_dynamic_sector

from IPython import embed as shell

LOG = logging.getLogger(__name__)

# Setup basic conditions for images

BOUNDARIES_INFO = {}
BOUNDARIES_INFO['request_coastlines'] = True
BOUNDARIES_INFO['request_countries'] = True
BOUNDARIES_INFO['request_states'] = True
BOUNDARIES_INFO['request_rivers'] = True

BOUNDARIES_INFO['coastlines_linewidth'] = 2
BOUNDARIES_INFO['countries_linewidth'] = 1
BOUNDARIES_INFO['states_linewidth'] = 0.25
BOUNDARIES_INFO['rivers_linewidth'] = 0.5

BOUNDARIES_INFO['coastlines_color'] = '#000000'
BOUNDARIES_INFO['countries_color']  = '#000000'
BOUNDARIES_INFO['states_color'] = '#000000'
BOUNDARIES_INFO['rivers_color'] = '#000000'

GRIDLINES_INFO = {}
GRIDLINES_INFO['left_label'] = True
GRIDLINES_INFO['right_label'] = True
GRIDLINES_INFO['top_label'] = True
GRIDLINES_INFO['bottom_label'] = True
GRIDLINES_INFO['grid_lat_linewidth'] = 1
GRIDLINES_INFO['grid_lon_linewidth'] = 1
GRIDLINES_INFO['grid_lat_color'] = "#000000"
GRIDLINES_INFO['grid_lon_color'] = "#000000"
GRIDLINES_INFO['grid_lat_spacing'] = 2
GRIDLINES_INFO['grid_lon_spacing'] = 2
GRIDLINES_INFO['grid_lat_dashes'] = [4, 2]
GRIDLINES_INFO['grid_lon_dashes'] = [4, 2]

# Setup product parameters

VARLIST = {'ahi': ['B14BT', 'B03Ref'],
           'abi': ['B14BT', 'B02Ref'],
           'seviri': ['B09BT', 'B01Ref'],
           'viirs': ['I05BT']}                           #I05: 11.45 um 
#           'viirs': ['I05BT','M16BT', 'M05Ref']}

PNGDIRS = {'ahi': 'png_dev',
           'abi': 'png_dev',
           'seviri': 'png_dev',
           'viirs': 'png_dev'}

PNGCLEANDIRS = {'ahi': 'png_clean_dev',
                'abi': 'png_clean_dev',
                'viirs': 'png_clean_dev',
                'seviri': 'png_clean_dev'}

ATCFDIRS = {'ahi': 'atcf_dev',
            'abi': 'atcf_dev',
            'viirs': 'atcf_dev',
            'seviri': 'atcf_dev'}

METADATADIRS = {'ahi': 'metadata_dev',
                'abi': 'metadata_dev',
                'viirs': 'metadata_dev',
                'seviri': 'metadata_dev'}

PRODNAME_LIST = {'ahiB14BT': 'Infrared-Gray',
                 'abiB14BT': 'Infrared-Gray',
                 'seviriB09BT': 'Infrared-Gray',
                 'seviriB01Ref': 'Visible-Gray',
                 'abiB02Ref': 'Visible-Gray',
                 'ahiB03Ref': 'Visible-Gray',
                 'viirsI05BT': 'Infrared',
                 'viirsM05Ref': 'Visible-Gray'}
                 #'viirsM16BT': 'Infrared-Gray',

# ALL PRODNAMES must be included in one of the PRODTYPES - these are used for setting colors
PRODTYPES = {'Infrared': ['Infrared']}
#             'Visible': ['tst']}

CMAPLIST = {'Infrared-Gray': 'Greys',
            'Visible-Gray': 'Greys_r',
            'Infrared': 'hsv'}                  # This Infrared hsv colormap will be replaced by a new scheme
DATA_UNITSLIST = {'Infrared-Gray': 'Kelvin',
                  'Visible-Gray': 'albedo',
                  'Infrared': 'Kelvin'}
VARTYPE_TITLE = {'Infrared-Gray': 'Brightness Temperatures',
                 'Visible-Gray': 'Albedo',
                 'Infrared': 'BT'}
PRODUCT_UNITS_LIST = {'Infrared-Gray': 'celsius',
                      'Visible-Gray': 'albedo',
                      'Infrared': 'celsius'}
KtoC_conversion = -273.15
AlbedoToAlbedo_conversion = 100

# GeoIPS 1.0 Infrared-Gray xml productfile settings
# MIN_IR = 173 + KtoC_conversion # -100
# MAX_IR = 323 + KtoC_conversion # 50
# Terascan range
# MIN_IR = -80
# MAX_IR = 30
MIN_IR = -100
MAX_IR = 50

MIN_VIS = 0
MAX_VIS = 120

min_val=-90     # for Infrerad
max_val=30

DATARANGE_LIST = {'Infrared-Gray': [MIN_IR, MAX_IR],
                  'Visible-Gray': [MIN_VIS, MAX_VIS],
                  'Infrared': [-90, 30]}                           # for matching Terrascan Infrared product color bar range 
GAMMA_LIST = {'Visible-Gray': [1.5]}
SCALEFACTOR_LIST = {'Visible-Gray': 100}
SUNZEN_CORRECTION_LIST = ['Visible-Gray']
MIN_SUNZEN_LIST = {'Visible-Gray': 90}

# REQUIRED FOR METOCTIFF INFRARED
MIN_SCALE_VALUE = 0
MAX_SCALE_VALUE = 249
MISSING_SCALE_VALUE = 255


def coverage(data_array):
    ''' Specify coverage based on current data type
        Parameters:
            data_array (numpy.ma.MaskedArray) : Final processed array from which to determine coverage
        Returns:
            (float) representing percent coverage
    '''

    return 100 * (float(numpy.ma.count(data_array)) / data_array.size)


def write_product_xarray(xarray_obj, orig_var_names, product_names):
    ''' Create a xarray object from the product variables

    Args:
        xarray_obj (Dataset): xarray Dataset of original sectored data file
        var_arrays (list): list of ndarrays, all variables to include in xarray object
        product_names (list): list of str, same length as var_arrays, names of variables
        orig_var_names (list): include metadata information from original variable in
                                             xarray_obj.
    Returns:
        (Dataset): xarray Dataset with desired products
    '''
    prod_xarray = xarray.Dataset()

    # for attr in ['start_datetime', 'end_datetime', 'platform_name', 'source_name', 'area_def', 'data_provider',
    #              'interpolation_radius_of_influence']:
    #     if attr in xarray_obj.attrs.keys():
    #         prod_xarray.attrs[attr] = xarray_obj.attrs[attr]

    from geoips2.xarray_utils.outputs import copy_standard_attrs
    copy_standard_attrs(xarray_obj, prod_xarray)

    for prodname, varname in zip(product_names, orig_var_names):
        prod_xarray[prodname] = xarray_obj[varname]
        prod_xarray[prodname].attrs['source_variable'] = varname
        # if prodname in DATARANGE_LIST:
        #     prod_xarray[prodname].attrs['valid_range'] = DATARANGE_LIST[prodname]
        # if prodname in GAMMA_LIST:
        #     prod_xarray[prodname].attrs['gamma'] = GAMMA_LIST[prodname]
        # if prodname in SCALEFACTOR_LIST:
        #     prod_xarray[prodname].attrs['scale_factor'] = SCALEFACTOR_LIST[prodname]
        # if prodname in SUNZEN_CORRECTION_LIST:
        #     prod_xarray[prodname].attrs['solar_zenith_correction'] = True
    from geoips2.xarray_utils.outputs import write_xarray_netcdf
    from geoips2.filenames.product_filenames import netcdf_write_filename
    ncdf_fname = netcdf_write_filename(basedir=gpaths['PRECALCULATED_DATA_PATH'],
                                       product_name='_'.join(product_names),
                                       source_name=prod_xarray.source_name,
                                       platform_name=prod_xarray.platform_name,
                                       sector_name=prod_xarray.area_def.area_id,
                                       product_datetime=prod_xarray.start_datetime)
    write_xarray_netcdf(prod_xarray, ncdf_fname)
    return [ncdf_fname]

def visir(xarray_datasets, area_def):
    '''
    This is a template for creating an external algorithm for operating on arbitrary data types from the datafile,
    outputting required data products, and plotting as needed. Most of standard GeoIPS processing is bypassed for these
    algorithm types.

      NOTE in geoips/geoimg/plot/prototypealg.py
          scifile is converted to xarray BEFORE being passed (standard variables latitude*, longitude*, timestamp*)
          sector is converted to area_def BEFORE being passed  (standard attributes sector_*)
      from geoips2.geoips1_utils.scifile import xarray_from_scifile
      from geoips2.geoips1_utils.sector import area_def_from_sector

    Args:
        xarray_dataset (xarray.Dataset) : xarray Dataset object including all required variables.
        area_def (AreaDefinition) : pyresample AreaDefinition object specifying the current location information.

    Returns:
        (None). since all processing, outputs, and plotting is complete prior to returning to the GeoIPS 1.0 process
        flow.  No automated plotting is performed from process.py fo prototype algorithms, all plotting must be
        performed from geoips2.r
    '''

    final_products = []

    # Assuming since this is the single channel algorithm, that we are only pulling one variable
    for xarray_dataset in xarray_datasets:
        for currvarname in VARLIST[xarray_dataset.source_name]:
            if currvarname not in xarray_dataset.variables.keys():
                LOG.info('%s not in xarray_dataset, skipping', currvarname)
                continue

            varname = currvarname
            LOG.info('Running on variable %s in xarray_dataset with shape %s', varname, xarray_dataset['latitude'].dims)
                
            product_name = PRODNAME_LIST[xarray_dataset.source_name+varname]

            if is_dynamic_sector(area_def):
                LOG.info('Trying to sector %s with dynamic time %s, %s points',
                         area_def.area_id, area_def.sector_start_datetime, xarray_dataset['latitude'].size)
            else:
                LOG.info('Trying to sector %s, %s points', area_def.area_id, xarray_dataset['latitude'].size)

            xarray_dataset[varname].attrs['units'] = DATA_UNITSLIST[product_name]

            if DATA_UNITSLIST[product_name] == 'Kelvin' and PRODUCT_UNITS_LIST[product_name] == 'celsius':
                if 'units' in xarray_dataset[varname].attrs and xarray_dataset[varname].units == 'celsius':
                    LOG.info('%s already in celsius, not converting', varname)
                else:
                    xarray_dataset[varname] = xarray_dataset[varname] + KtoC_conversion
                    xarray_dataset[varname].attrs['units'] = 'celsius'

            from geoips2.xarray_utils.data import sector_xarray_dataset
            # Pass all 4 variables to sector_xarray_dataset, so they are all masked appropriately for pulling min/max vals
            varlist = [varname, 'latitude', 'longitude']
            if product_name in MIN_SUNZEN_LIST.keys():
                varlist += ['SunZenith']
            # Grab an extra +- 3 degrees so if we read in the pre-sectored dataset, we will have extra data for
            # re-centering
            sect_xarray = sector_xarray_dataset(xarray_dataset,
                                                area_def,
                                                varlist,
                                                lon_pad=3,
                                                lat_pad=3)

            # Well this is annoying. numpy arrays fail if numpy_array is None, and xarrays fail if x_array == None
            if sect_xarray is None:
                continue

            sect_xarray.attrs['area_def'] = area_def
            sect_xarray.attrs['start_datetime'] = xarray_dataset.start_datetime
            sect_xarray.attrs['end_datetime'] = xarray_dataset.end_datetime

            LOG.info('Sectored data start/mid/end datetime: %s %s, %s points',
                     sect_xarray.start_datetime,
                     sect_xarray.end_datetime,
                     numpy.ma.count(sect_xarray[varname].to_masked_array()))

            from geoips2.xarray_utils.interpolation import interp_nearest
            from geoips2.data_manipulations.info import percent_unmasked

            if product_name in MIN_SUNZEN_LIST.keys():
                from geoips2.data_manipulations.corrections import mask_night
                LOG.info('Percent unmasked day/night %s', percent_unmasked(sect_xarray[varname]))
                sect_xarray[varname] = xarray.DataArray(mask_night(sect_xarray[varname].to_masked_array(),
                                                                   sect_xarray['SunZenith'].to_masked_array(),
                                                                   MIN_SUNZEN_LIST[product_name]))
                LOG.info('Percent unmasked day only %s', percent_unmasked(sect_xarray[varname]))

            if product_name in SUNZEN_CORRECTION_LIST:
                from geoips2.data_manipulations.corrections import apply_solar_zenith_correction
                sect_xarray[varname] = xarray.DataArray(apply_solar_zenith_correction(
                                                        sect_xarray[varname].to_masked_array(),
                                                        sect_xarray['SunZenith'].to_masked_array()))

            if product_name in GAMMA_LIST.keys():
                from geoips2.data_manipulations.corrections import apply_gamma
                for gamma in GAMMA_LIST[product_name]:
                    sect_xarray[varname] = xarray.DataArray(apply_gamma(sect_xarray[varname].to_masked_array(),
                                                                        gamma))

            if product_name in SCALEFACTOR_LIST.keys():
                from geoips2.data_manipulations.corrections import apply_scale_factor
                sect_xarray[varname] = xarray.DataArray(apply_scale_factor(sect_xarray[varname].to_masked_array(),
                                                                           SCALEFACTOR_LIST[product_name]))

            LOG.info('min/max before: %s to %s', sect_xarray[varname].min(), sect_xarray[varname].max())
            [interp_data] = interp_nearest(area_def, sect_xarray, varlist=[varname])

            LOG.info('min/max after: %s to %s', interp_data.min(), interp_data.max())
            LOG.info('Percent unmasked before %s', percent_unmasked(interp_data))

            covg = percent_unmasked(interp_data)
            LOG.info('Percent unmasked after %s', percent_unmasked(interp_data))
            if covg > 0:
                final_products += write_product_xarray(sect_xarray,
                                                       [varname, 'latitude', 'longitude'],
                                                       [product_name, 'latitude', 'longitude'])

                from geoips2.xarray_utils.outputs import output_atcf_fname, output_metoctiff
                # from geoips2.output_formats.image import plot_image

                from geoips2.image_utils.mpl_utils import set_matplotlib_colors_standard

                cbar_label = '{0} ({1})'.format(VARTYPE_TITLE[product_name], xarray_dataset[varname].units)

                LOG.info('data min val %s to max va %s', interp_data.min(), interp_data.max())

                # Create the matplotlib color info dict - the fields in this dictionary (cmap, norm, boundaries,
                # etc) will be used in plot_image to ensure the image matches the colorbar.
                mpl_colors_info = set_matplotlib_colors_standard(DATARANGE_LIST[product_name],
                                                                 cmap_name=CMAPLIST[product_name],
                                                                 cbar_label=cbar_label)


                from geoips2.sector_utils.utils import is_sector_type

                if is_sector_type(area_def, 'atcf'):
                    # from geoips2.sector_utils.atcf_tracks import run_archer
                    # run_archer(sect_xarray, varname)

                    # get filename from objects
                    atcf_fname = output_atcf_fname(area_def, sect_xarray, product_name, covg,
                                                   output_type='png', output_type_dir=PNGDIRS[sect_xarray.source_name],
                                                   product_dir=product_name)
                    atcf_fname_clean = output_atcf_fname(area_def, sect_xarray, product_name, covg,
                                                         output_type='png',
                                                         output_type_dir=PNGCLEANDIRS[sect_xarray.source_name],
                                                         product_dir=product_name)

                    # generate images

                    if product_name in PRODTYPES['Infrared']:
                        # setup a special color map for Infrared images at 11 um
                        from geoips2.image_utils.mpl_utils import set_matplotlib_colors_IR
                        curr_min_tb=-90
                        curr_max_tb= 30
                        mpl_colors_info = set_matplotlib_colors_IR(min_tb=curr_min_tb, max_tb=curr_max_tb)

                    # call plotting function
                    from geoips2.output_formats.image import create_standard_imagery
                    final_products += create_standard_imagery(area_def,
                                                              plot_data=interp_data,
                                                              xarray_obj=sect_xarray,
                                                              product_name_title=product_name,
                                                              clean_fname=atcf_fname_clean,
                                                              annotated_fnames=[atcf_fname],
                                                              mpl_colors_info=mpl_colors_info,
                                                              boundaries_info=BOUNDARIES_INFO,
                                                              gridlines_info=GRIDLINES_INFO,
                                                              remove_duplicate_minrange=10)

                    # output Metoctiff files
                    final_products += output_metoctiff(product_name, area_def, sect_xarray, interp_data,
                                                       requested_data_min=DATARANGE_LIST[product_name][0],
                                                       requested_data_max=DATARANGE_LIST[product_name][1],
                                                       scale_data_min=MIN_SCALE_VALUE,
                                                       scale_data_max=MAX_SCALE_VALUE,
                                                       missing_value=MISSING_SCALE_VALUE,
                                                       units=xarray_dataset[varname].units,
                                                       mpl_cmap=mpl_colors_info['cmap'],
                                                       coverage=covg,
                                                       atcf_dir=ATCFDIRS[sect_xarray.source_name])

                else:
                    
                    from geoips2.xarray_utils.outputs import output_geoips_fname
                    # get filename from objects
                    web_fname = output_geoips_fname(area_def, sect_xarray, product_name, covg)

                    from geoips2.output_formats.image import create_standard_imagery
                    final_products += create_standard_imagery(area_def,
                                                              plot_data=interp_data,
                                                              xarray_obj=sect_xarray,
                                                              product_name_title=product_name,
                                                              clean_fname=None,
                                                              annotated_fnames=[web_fname],
                                                              mpl_colors_info=mpl_colors_info)

        else:
            LOG.info('Insufficient coverage, skipping')

    from geoips2.output_formats.metadata import produce_all_sector_metadata
    final_products += produce_all_sector_metadata(final_products, area_def, xarray_dataset,
                                                  metadata_dir=METADATADIRS[xarray_dataset.source_name])

    return final_products
