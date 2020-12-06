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

''' Get appropriate data for current sector for the windspeed external algorithm.
    Using pandas / xarray as the basis for this external algorithm - storing all attributes previously assigned
    to datafile.metadata in the winds_xarray.attrs and winds_xarray['varname'].attrs dictionaries.
'''

# Python Standard Libraries
import logging

from geoips2.sector_utils.utils import is_sector_type, set_mtif_area_def, set_text_area_def
from geoips2.xarray_utils.data import sector_xarray_dataset
from geoips2.xarray_utils.interpolation import interp_nearest
from geoips2.data_manipulations.info import percent_unmasked
from geoips2.xarray_utils.outputs import output_windspeed_text, output_geoips_fname
from geoips2.xarray_utils.outputs import output_atcf_fname, output_metoctiff
from geoips2.image_utils.mpl_utils import set_matplotlib_colors_winds, set_matplotlib_colors_standard
from geoips2.output_formats.image import create_standard_imagery
from geoips2.output_formats.metadata import produce_all_sector_metadata

LOG = logging.getLogger(__name__)

BOUNDARIES_INFO = {}
BOUNDARIES_INFO['request_coastlines'] = True
BOUNDARIES_INFO['request_countries'] = True
BOUNDARIES_INFO['request_states'] = True
BOUNDARIES_INFO['request_rivers'] = True

BOUNDARIES_INFO['coastlines_linewidth'] = 2
BOUNDARIES_INFO['countries_linewidth'] = 1
BOUNDARIES_INFO['states_linewidth'] = 0.5
BOUNDARIES_INFO['rivers_linewidth'] = 0

BOUNDARIES_INFO['coastlines_color'] = '#00B4B4B4'
BOUNDARIES_INFO['countries_color'] = '#00B4B4B4'
BOUNDARIES_INFO['states_color'] = '#00B4B4B4'
BOUNDARIES_INFO['rivers_color'] = '#00B4B4B4'

GRIDLINES_INFO = {}
GRIDLINES_INFO['left_label'] = True
GRIDLINES_INFO['right_label'] = True
GRIDLINES_INFO['top_label'] = True
GRIDLINES_INFO['bottom_label'] = True
GRIDLINES_INFO['grid_lat_linewidth'] = 1
GRIDLINES_INFO['grid_lon_linewidth'] = 1
GRIDLINES_INFO['grid_lat_color'] = "#00B4B4B4"
GRIDLINES_INFO['grid_lon_color'] = "#00B4B4B4"
GRIDLINES_INFO['grid_lat_spacing'] = 2
GRIDLINES_INFO['grid_lon_spacing'] = 2
GRIDLINES_INFO['grid_lat_dashes'] = [4, 2]
GRIDLINES_INFO['grid_lon_dashes'] = [4, 2]

MTIF_MIN_WIND_SPEED = 1
MTIF_MAX_WIND_SPEED = 255
MTIF_SCALE_DATA_MIN = 1
MTIF_SCALE_DATA_MAX = 255
MTIF_MISSING_VALUE = 0

PNG_MIN_WIND_SPEED = 0
PNG_MAX_WIND_SPEED = 200

PRODUCT_DATATYPE_TITLE = {'smap-spd': 'SMAP',
                          'smos-spd': 'SMOS'}

OLDWEB = {'amsr2': 'windspeed',
          'windsat': 'windspeed'}


def plot_windspeeds(wind_xarray, area_def, interp_data,
                    mtif_area_def=None, mtif_interp_data=None, text_area_def=None,
                    vis_data=None, ir_data=None, vis_xarray=None, ir_xarray=None):
    ''' Plot wind speed files, based on the current data and area definitions

    Args:
        wind_xarray (Dataset) : xarray Dataset containing metadata information
        area_def (AreaDefinition) : pyresample AreaDefintion for full data array
        interp_data (ndarray) : numpy.ma.MaskedArray of data to plot, relating to area_def
        mtif_area_def (AreaDefinition) : pyresample AreaDefinition pertaining to native resolution mtif data
        mtif_interp_data (ndarray) : numpy.ma.MaskedArray of data to plot, relating to mtif_area_def
        text_area_def (AreaDefinition) : pyresample AreaDefinition pertaining to non-interpolated sectored data

    Returns:
        (list, list, list) : List of strings of full final products , List of strings of mtif final products
                             List of strings for text final products
    '''

    final_products = []
    mtif_final_products = []
    text_final_products = []
    product_name = 'windspeed'
    product_name_title = 'Winds'
    product_datatype_title = None
    if wind_xarray.source_name in PRODUCT_DATATYPE_TITLE:
        product_datatype_title = PRODUCT_DATATYPE_TITLE[wind_xarray.source_name]
    covg = percent_unmasked(interp_data)

    bg_mpl_colors_info = None
    bg_data = None
    bg_xarray = None
    bg_product_name_title = None
    if vis_data is not None:
        from geoips2.products.visir import DATARANGE_LIST, CMAPLIST
        bg_data = vis_data
        bg_xarray = vis_xarray
        bg_product_name_title = 'Visible'
        # Create the matplotlib color info dict - the fields in this dictionary (cmap, norm, boundaries,
        # etc) will be used in plot_image
        bg_mpl_colors_info = set_matplotlib_colors_standard(DATARANGE_LIST['Visible-Gray'],
                                                            cmap_name=CMAPLIST['Visible-Gray'],
                                                            cbar_label=None,
                                                            create_colorbar=False)
    elif ir_data is not None:
        from geoips2.products.visir import DATARANGE_LIST, CMAPLIST
        # Create the matplotlib color info dict - the fields in this dictionary (cmap, norm, boundaries,
        # etc) will be used in plot_image
        bg_data = ir_data
        bg_xarray = ir_xarray
        bg_product_name_title = 'Infrared'
        bg_mpl_colors_info = set_matplotlib_colors_standard(DATARANGE_LIST['Infrared-Gray'],
                                                            cmap_name=CMAPLIST['Infrared-Gray'],
                                                            cbar_label=None,
                                                            create_colorbar=False)

    if is_sector_type(area_def, 'atcf'):

        mtif_covg = percent_unmasked(mtif_interp_data)
        # get filename from objects
        atcf_fname = output_atcf_fname(area_def, wind_xarray, product_name, covg,
                                       output_type='png', output_type_dir='png',
                                       product_dir=product_name)
        old_tcweb_fname = output_atcf_fname(area_def, wind_xarray, product_name, covg,
                                            output_type='jpg',
                                            product_dir=product_name, output_old_tc_web=True)
        atcf_fname_clean = output_atcf_fname(area_def, wind_xarray, product_name+'Clean', covg,
                                             output_type='png', output_type_dir='png_clean',
                                             product_dir=product_name)
        annotated_fnames = [atcf_fname]
        if old_tcweb_fname is not None and wind_xarray.source_name in OLDWEB and product_name in OLDWEB[wind_xarray.source_name]:
            annotated_fnames += [old_tcweb_fname]
        # atcf_fname_clean = None

        # Create the matplotlib color info dict - the fields in this dictionary (cmap, norm, boundaries,
        # etc) will be used in plot_image to ensure the image matches the colorbar.
        mpl_colors_info = set_matplotlib_colors_winds(min_wind_speed=PNG_MIN_WIND_SPEED,
                                                      max_wind_speed=PNG_MAX_WIND_SPEED)

        final_products += create_standard_imagery(area_def,
                                                  plot_data=interp_data,
                                                  xarray_obj=wind_xarray,
                                                  product_name_title=product_name_title,
                                                  clean_fname=atcf_fname_clean,
                                                  annotated_fnames=annotated_fnames,
                                                  mpl_colors_info=mpl_colors_info,
                                                  boundaries_info=BOUNDARIES_INFO,
                                                  gridlines_info=GRIDLINES_INFO,
                                                  product_datatype_title=product_datatype_title,
                                                  bg_data=bg_data,
                                                  bg_mpl_colors_info=bg_mpl_colors_info,
                                                  bg_xarray=bg_xarray,
                                                  bg_product_name_title=bg_product_name_title)

        units = 'kts'
        if 'units' in wind_xarray['wind_speed_kts'].attrs.keys():
            units = wind_xarray['wind_speed_kts'].attrs['units']

        # Different color bars for MTIFs and PNGs - if the min/max wind speed in the color bar lines up with the
        # min/max scale values, then the colors will line up exactly with the 8 bit integer values.
        mpl_colors_info_mtif = set_matplotlib_colors_winds(min_wind_speed=MTIF_MIN_WIND_SPEED,
                                                           max_wind_speed=MTIF_MAX_WIND_SPEED)
        mtif_final_products += output_metoctiff(product_name, mtif_area_def, wind_xarray, mtif_interp_data,
                                                requested_data_min=MTIF_MIN_WIND_SPEED,
                                                requested_data_max=MTIF_MAX_WIND_SPEED,
                                                scale_data_min=MTIF_SCALE_DATA_MIN,
                                                scale_data_max=MTIF_SCALE_DATA_MAX,
                                                missing_value=MTIF_MISSING_VALUE,
                                                coverage=mtif_covg,
                                                mpl_cmap=mpl_colors_info_mtif['cmap'],
                                                units=units)
        text_final_products += output_windspeed_text(wind_xarray, area_def=area_def)

    else:

        # get filename from objects
        web_fname = output_geoips_fname(area_def, wind_xarray, product_name, covg)

        # Create the matplotlib color info dict - the fields in this dictionary (cmap, norm, boundaries,
        # etc) will be used in plot_image to ensure the image matches the colorbar.
        mpl_colors_info = set_matplotlib_colors_winds(min_wind_speed=PNG_MIN_WIND_SPEED,
                                                      max_wind_speed=PNG_MAX_WIND_SPEED)

        final_products += create_standard_imagery(area_def,
                                                  plot_data=interp_data,
                                                  xarray_obj=wind_xarray,
                                                  product_name_title=product_name_title,
                                                  clean_fname=None,
                                                  annotated_fnames=[web_fname],
                                                  mpl_colors_info=mpl_colors_info,
                                                  boundaries_info=BOUNDARIES_INFO,
                                                  bg_data=bg_data,
                                                  bg_mpl_colors_info=bg_mpl_colors_info,
                                                  bg_xarray=bg_xarray)

    return final_products, mtif_final_products, text_final_products


def windspeed(full_xarrays, area_def):
    ''' Product specification to appropriately sector and plot wind speed data
      NOTE in geoips/geoimg/plot/prototypealg.py
          scifile is converted to xarray BEFORE being passed
          sector is converted to area_def BEFORE being passed
      from geoips2.geoips1_utils.scifile import xarray_from_scifile
      from geoips2.geoips1_utils.sector import area_def_from_sector
    '''

    final_products = []
    # These use a different area definition - make sure the correct one is recorded.
    mtif_final_products = []
    text_final_products = []

    wind_xarray = None
    ir_xarray = None
    vis_xarray = None
    interp_bg = None

    for xobj in full_xarrays:
        if 'wind_speed_kts' in xobj.variables.keys():
            wind_xarray = xobj
        if 'Infrared-Gray' in xobj.variables.keys():
            ir_xarray = xobj
            ir_covg = percent_unmasked(ir_xarray['Infrared-Gray'].to_masked_array())
        if 'Visible-Gray' in xobj.variables.keys():
            vis_xarray = xobj
            vis_covg = percent_unmasked(vis_xarray['Visible-Gray'].to_masked_array())
    if vis_xarray and ir_xarray and ir_covg > vis_covg:
        vis_xarray = None

    [interp_data] = interp_nearest(area_def, wind_xarray, varlist=['wind_speed_kts'])
    interp_vis = None
    interp_ir = None
    if vis_xarray is not None:
        [interp_vis] = interp_nearest(area_def, vis_xarray, varlist=['Visible-Gray'])
    elif ir_xarray is not None:
        [interp_ir] = interp_nearest(area_def, ir_xarray, varlist=['Infrared-Gray'])

    mtif_area_def = None
    mtif_interp_data = None
    text_area_def = None
    if is_sector_type(area_def, 'atcf'):
        mtif_area_def = set_mtif_area_def(wind_xarray, area_def)
        [mtif_interp_data] = interp_nearest(mtif_area_def, wind_xarray, varlist=['wind_speed_kts'])
        
        text_area_def = set_text_area_def(wind_xarray, area_def)

        if mtif_interp_data is None:
            mtif_interp_data = interp_data

    covg = percent_unmasked(interp_data)
    # Assume this is set in the reader.
    # if covg > wind_xarray.minimum_coverage:
    # Now that we are checking coverage within 4 deg x 4deg center box, we can now take ANY amount of overall coverage.
    if covg > 1:
        final_products, mtif_final_products, text_final_products = plot_windspeeds(wind_xarray,
                                                                                   area_def,
                                                                                   interp_data,
                                                                                   mtif_area_def,
                                                                                   mtif_interp_data,
                                                                                   text_area_def,
                                                                                   vis_data=interp_vis,
                                                                                   ir_data=interp_ir,
                                                                                   vis_xarray=vis_xarray,
                                                                                   ir_xarray=ir_xarray)

    else:
        LOG.info('SKIPPING Insufficient coverage %s%%, minimum required %s%%',
                 covg, wind_xarray.minimum_coverage)

    # This generates YAML files of sector-related metadata for all products in the final_products list
    # NOTE this produces metadata based on "area_def" - if we begin re-centering the storm, ensure this is updated to
    # reflect varying area definitions
    final_products += produce_all_sector_metadata(final_products, area_def, wind_xarray)
    mtif_final_products += produce_all_sector_metadata(mtif_final_products, mtif_area_def, wind_xarray)
    text_final_products += produce_all_sector_metadata(text_final_products, text_area_def, wind_xarray)

    return final_products+mtif_final_products+text_final_products
