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

''' This program is designed to process Microwave Imagery from NRL TC (MINT) data'''

# Python Standard Libraries
import logging

# Third Party Installed Libraries
import numpy

from geoips2.xarray_utils.outputs import output_atcf_fname
from geoips2.sector_utils.utils import is_sector_type
from geoips2.output_formats.metadata import produce_all_sector_metadata
from geoips2.xarray_utils.data import sector_xarray_dataset
from geoips2.readers.mint_ncdf import DATASET_INFO as DATASET_INFO
from geoips2.sector_utils.atcf_tracks import recenter_area_def, set_atcf_area_def

LOG = logging.getLogger(__name__)

# Setup basic conditions for images

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

MIN_SCALE_VALUE = 1
MAX_SCALE_VALUE = 255
MISSING_SCALE_VALUE = 0

MIN_TB_HI = 105          # high freq channels: 85-91 GHz
MAX_TB_HI = 305

MIN_TB_LO = 125          # low freq channels: 19-37 GHz
MAX_TB_LO = 300


# Define PMW plotting variables
def pmw_mint(xarray_datasets, area_def, arg_dict=None):
    ''' Process xarray_dataset (xarray_datasets expected to be length 1 list) over area_def, with optional arg_dict.
    input xarray-based variables are defined in the readers with the GEOIPS2 framework

    Args:
        xarray_datasets (list) : list of xarray Dataset objects - for pmw_mint products, expect a length one list.
        area_def (AreaDefinition) : pyresample AreaDefinition specifying initial region to process.
        arg_dict (dict) : Dictionary of optional arguments (command_line_args are passed through)
    Returns:
        (list) : List of full paths to all products produed through pmw_mint processing
    '''

    LOG.info(arg_dict)
    final_products = []

    full_xarray = xarray_datasets[0]

    # DATASET_INFO is imported from readers.mint_ncdf - contains list of possible variables for each dataset
    for varname in DATASET_INFO[full_xarray.dataset_name]:

        if varname not in full_xarray.variables.keys():
            LOG.info('SKIPPING variable %s, not in current xarray object', varname)
            continue

        # Interpolation radius of influence is set for each dataset separately in the mint_ncdf reader - adjust
        # in readers/mint_ncdf.py ROI_INFO dictionary
        # set_roi(full_xarray, varname)

        if area_def.sector_start_datetime:
            LOG.info('Trying to sector %s with dynamic time %s, %s points',
                     area_def.area_id, area_def.sector_start_datetime, full_xarray['latitude'].size)
        else:
            LOG.info('Trying to sector %s, %s points', area_def.area_id, full_xarray['latitude'].size)

        # Compile a list of variables that will be used to sector - the current data variable, and we will add in
        # the appropriate latitude and longitude variables (of the same shape as data), and if it exists the
        # appropriately shaped timestamp array
        vars_to_sect = [varname]            # create a new sect to list intended products

        # we have to have 'latitude','longitude" in the full_xarray, and 'timestamp' if we want temporal sectoring
        if 'latitude' in full_xarray.variables.keys():
            vars_to_sect += ['latitude']
        if 'longitude' in full_xarray.variables.keys():
            vars_to_sect += ['longitude']
        if 'timestamp' in full_xarray.variables.keys():
            vars_to_sect += ['timestamp']

        # I believe ARCHER can not have any masked data within the data grid, so create a separate smaller sector for
        # running archer.  The size of the "new" ARCHER sector could probably use some tweaking, though this worked
        # "out of the box" for my test case.
        # Probably in the end want to just run ARCHER first, get the new center, then create a new area_def with
        # the ARCHER center. and sector / register based on the ARCHER centered area_def. Ok, I'll just do that
        # really quickly.
        archer_area_def = set_atcf_area_def(area_def.sector_info,
                                            num_lines=500, num_samples=500,
                                            pixel_width=10000, pixel_height=10000)
        archer_xarray = sector_xarray_dataset(full_xarray,
                                              archer_area_def,
                                              vars_to_sect)

        try:
            from geoips2.sector_utils.atcf_tracks import run_archer
            in_dict, out_dict, score_dict = run_archer(archer_xarray, varname)
        except ValueError:
            from IPython import embed as shell; shell()
            continue

        recentered_area_def = recenter_area_def(area_def, out_dict)

        # The list of variables in vars_to_sect must ALL be the same shape
        sect_xarray = sector_xarray_dataset(full_xarray,
                                            recentered_area_def,
                                            vars_to_sect)


        # numpy arrays fail if numpy_array is None, and xarrays fail if x_array == None
        if sect_xarray is None:
            LOG.info('No coverage - skipping')
            return final_products

        sect_xarray.attrs['area_def'] = recentered_area_def        # add name of this sector to sector attribute
        if hasattr(sect_xarray, 'timestamp'):
            from geoips2.xarray_utils.timestamp import get_min_from_xarray_timestamp
            from geoips2.xarray_utils.timestamp import get_max_from_xarray_timestamp
            sect_xarray.attrs['start_datetime'] = get_min_from_xarray_timestamp(sect_xarray, 'timestamp')
            sect_xarray.attrs['end_datetime'] = get_max_from_xarray_timestamp(sect_xarray, 'timestamp')
            # Note:  need to test whether above two lines can reselect min and max time_info for this sector

        LOG.info('Sectored data start/end datetime: %s %s, %s points',
                 sect_xarray.start_datetime,
                 sect_xarray.end_datetime,
                 numpy.ma.count(sect_xarray[varname].to_masked_array()))

        array_nums = [None]                         # data points?
        if len(sect_xarray[varname].shape) == 3:
            array_nums = range(0, sect_xarray[varname].shape[2])

        for array_num in array_nums:
            # selection of an intepolation scheme

            from geoips2.xarray_utils.interpolation import interp_nearest
            try:
                [interp_data] = interp_nearest(recentered_area_def, sect_xarray, varlist=[varname], array_num=array_num)
            except ValueError:
                from IPython import embed as shell; shell()
            final_products += plot_interp_data(interp_data, sect_xarray, recentered_area_def, varname)

            from geoips2.xarray_utils.interpolation import interp_scipy_grid
            interp_data = interp_scipy_grid(recentered_area_def, sect_xarray, varname,
                                            array_num=array_num, method='linear')
            prodname = '{0}_{1}_GriddataLinear'.format(sect_xarray.source_name, varname)
            final_products += plot_interp_data(interp_data, sect_xarray, recentered_area_def, varname,
                                               product_name=prodname)

    return final_products


def plot_interp_data(interp_data, xarray_obj, area_def, varname, product_name=None):
    ''' Plot the current interpolated data array, using metadata found in xarray_obj and area_def

    Args:
        interp_data (numpy.ndarray) : ndarray or MaskedArray of data to plot
        xarray_obj (Dataset) : xarray Dataset containing appropriate metadata for naming files, etc
        area_def (AreaDefinition) : Pyresample AreaDefinition specifying the region to plot
        varname (str) : Name of variable that we are plotting out of xarray_obj

    Returns:
        (list) : List of strings containing full paths to all output products created
    '''

    final_products = []

    if not product_name:
        product_name = '{0}_{1}'.format(xarray_obj.source_name, varname)

    from geoips2.data_manipulations.info import percent_unmasked

    covg = percent_unmasked(interp_data)
    if covg > 0:                # test a data coverage criterion
        if is_sector_type(area_def, 'atcf'):

            # Get the output filename from sector, and xarray objects

            atcf_fname = output_atcf_fname(area_def, xarray_obj, product_name, covg)
            #                            product_dir=product_name,
            #                            source_dir=product_name)
            atcf_fname_clean = output_atcf_fname(area_def, xarray_obj, product_name+'Clear', covg)
            #                                  product_dir=product_name,
            #                                  source_dir=product_name)

            # Create the matplotlib color info dict - the fields in this dictionary (cmap, norm, boundaries,
            # etc) will be used in plot_image to ensure the image matches the colorbar.
            # selelec a relative color scheme depending on Hi or Lo frequency channels
            if varname in ['H19', 'V19', 'H37', 'V37', 'tb37H', 'tb19H']:
                # color scheme for low frequency
                from geoips2.image_utils.mpl_utils import set_matplotlib_colors_37H
                mpl_colors_info = set_matplotlib_colors_37H(min_tb=MIN_TB_LO, max_tb=MAX_TB_LO)
            else:
                if varname in ['Chan2_AT', 'Chan3_AT', 'Chan4_AT', 'Chan5_AT']:
                    # default for high frequency (150-190 GHz) color scheme
                    from geoips2.image_utils.mpl_utils import set_matplotlib_colors_150H
                    mpl_colors_info = set_matplotlib_colors_150H(min_tb=110, max_tb=310)
                else:
                    # default for high frequency (85-91 GHz) color scheme
                    from geoips2.image_utils.mpl_utils import set_matplotlib_colors_89H
                    mpl_colors_info = set_matplotlib_colors_89H(min_tb=MIN_TB_HI, max_tb=MAX_TB_HI)

            from geoips2.output_formats.image import create_standard_imagery

            final_products += create_standard_imagery(area_def,
                                                      plot_data=interp_data,
                                                      xarray_obj=xarray_obj,
                                                      product_name_title=product_name,
                                                      clean_fname=atcf_fname_clean,
                                                      annotated_fname=atcf_fname,
                                                      mpl_colors_info=mpl_colors_info,
                                                      boundaries_info=BOUNDARIES_INFO,
                                                      gridlines_info=GRIDLINES_INFO)

    else:
        LOG.info('Insufficient coverage, skipping')

    # This generates YAML files of sector-related metadata for all products in the final_products list
    final_products += produce_all_sector_metadata(final_products, area_def, xarray_obj)
    return final_products
