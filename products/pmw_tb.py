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

''' This program is designed to prepare a list of TB products from variours passive microwave (PMW) senors'''

# Python Standard Libraries
import logging

# Third Party Installed Libraries
import numpy
    
from geoips2.xarray_utils.outputs import output_atcf_fname, output_geoips_fname
from geoips2.sector_utils.utils import is_sector_type
from geoips2.output_formats.metadata import produce_all_sector_metadata
from geoips2.data_manipulations.info import percent_unmasked

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

# scaling_term=(MAX_DATA_VAL-MIN_DATA_VAL)/(SCALE_DATA_MAX-SCALE_DATA_MIN)
# DATA_RANGE=MIN_SCALE_VALUE,MAX_SCALE_VALUE,MIN_DATA_VAL,scaling_term
# To determine MAX_DATA_VAL from scaling_term in DATA_RANGE:
#   scaling_term*(SCALE_DATA_MAX-SCALE_DATA_MIN) + MIN_DATA_VAL
# Terascan DATA_RANGE for AMSR2 89h: 0,239,180,0.41841,None
MIN_SCALE_VALUE = 0
MAX_SCALE_VALUE = 253
MISSING_SCALE_VALUE = 254
MTIF_UNITS = 'kelvin'
# MIN_TB_MTIF = 180          # MTIF range (based on Terascan)
# MAX_TB_MTIF = 280

MIN_TB_HI = 105          # high freq channels: 85-91 GHz
MAX_TB_HI = 305

MIN_TB_LO = 125          # low freq channels: 19-37 GHz
MAX_TB_LO = 300

# Specify which channel / variables are required for each data type
VARLIST = {'ssmi':  ['H19', 'V19', 'H37', 'V37', 'H85', 'V85'],
           'amsub': ['Chan1_AT', 'Chan2_AT', 'Chan3_AT', 'Chan4_AT', 'Chan5_AT'],
           # 'saphir': ['ch1_183.31_0.2', 'ch2_183.31_1.1', 'ch3_183.31_2.8', 'ch4_183.31_4.2',
           #            'ch5_183.31_6.8', 'ch6_183.31_11.0'],
           'saphir': ['ch2_183.31_1.1', 'ch3_183.31_2.8'],
           'mhs':   ['Chan1_AT', 'Chan2_AT', 'Chan3_AT', 'Chan4_AT', 'Chan5_AT'],
           'gmi':   ['V19','H19','V37','H37','V89', 'H89', 'V166','H166','V183-3','V183-7'],
           'windsat':   ['ftb37v', 'ftb37h'],
           'ssmis': ['H19','V19', 'H37', 'V37', 'H91', 'V91','V150', 'H183-1', 'H183-3', 'H183-7'],
           'amsr2': ['tb89hA', 'tb89vA', 'tb36h', 'tb36v'],
           'imerg': ['rain']}

# These go in the titles, filenames, and directory names. All variable names in VARLIST MUST be included in PRODNAMES
PRODNAMES = {'89H': ['tb89hA', 'tb89h', 'H85', 'H91', 'H89'],
             '89V': ['tb89vA', 'tb89v', 'V85', 'V91', 'V89','Chan1_AT'],
             '37H': ['tb36h', 'H37', 'ftb37h'],
             '37V': ['tb36v', 'V37', 'ftb37v'],
             '19H': ['tb19h', 'H19'],
             '19V': ['tb19v', 'V19'],
             '150V': ['V150'],
             '157V': ['Chan2_AT'],
             '166V': ['V166'],
             '166H': ['H166'],
             '183-1H': ['Chan3_AT', 'ch2_183.31_1.1', 'H183-1'],
             '183-3H': ['Chan4_AT', 'ch3_183.31_2.8', 'H183-3','V183-3'],
             '190V': ['Chan5_AT', 'H183-7','V183-7'],
             'Rain': ['rain']}

# sigma defaults to 10000, unless in this dictionary. NOTE these are all ssmi or ssmis
SIGMALIST = {'H19': 25000,
             'V19': 25000,
             'H37': 25000,
             'V37': 25000}

# Specify which PRODNAMES go into various RGB products
# products that output 4 color guns, red green blue and alpha layer
RGBA_PRODUCTS = {'color37': ['37H', '37V'],
                 'color89': ['89H', '89V'],
                 }

# Specify which PRODNAMES go into various single array output products
# products that output a single array with min and max value and colormap for plotting
SINGLE_ARRAY_PRODUCTS = {'37pct': ['37H', '37V'],
                         '89pct': ['89H', '89V'],
                         }

# ALL PRODNAMES must be included in one of the PRODTYPES - these are used for setting colors
PRODTYPES = {'37H': ['37H', '37V', '19H', '19V',
                     '37HNearest', '37VNearest', '19HNearest', '19VNearest'],
             '89H': ['89H', '89V',
                     '89HNearest', '89VNearest'],
             '150H': ['150H', '150V', '166H', '166V', '157V', '183-1H', '183-3H', '190V',
                      '150HNearest', '150VNearest', '166HNearest', '166VNearest', '157VNearest',
                      '183-1HNearest', '183-3HNearest', '190VNearest'],
             'Rain': ['Rain', 'RainNearest']}

# Put everything in png_dev for the time being, until we have evaluated the products
OLDWEB = {'amsr2': ['89H', '37V', '37H', '89pct', 'color37', 'color89'],
          'gmi': ['89H', '37V', '37H', '89pct', 'color37', 'color89'],
          'ssmi': ['89H', '37V', '37H', '89pct', 'color37', 'color89'],
          'ssmis': ['89H', '37V', '37H', '89pct', 'color37', 'color89'],
          'imerg': ['Rain'],
          'windsat': ['37H', '37V', 'color37'],
          'amsub': ['89V'],
          }
PNGDIRS = {'amsr2': 'png_dev',
           'gmi': 'png_dev',
           'saphir': 'png_dev',
           'ssmis': 'png_dev',
           'windsat': 'png_dev',
           'ssmi': 'png_dev',
           'amsub': 'png_dev',
           'imerg': 'png_dev'}

ATCFDIRS = {'amsr2': 'atcf_dev',
            'gmi': 'atcf_dev',
            'saphir': 'atcf_dev',
            'ssmis': 'atcf_dev',
            'windsat': 'atcf_dev',
            'ssmi': 'atcf_dev',
            'amsub': 'atcf_dev',
            'imerg': 'atcf_dev'}

METADATADIRS = {'amsr2': 'metadata_dev',
                'gmi': 'metadata_dev',
                'saphir': 'metadata_dev',
                'ssmis': 'metadata_dev',
                'windsat': 'metadata_dev',
                'ssmi': 'metadata_dev',
                'amsub': 'metadata_dev',
                'imerg': 'metadata_dev'}

PNGCLEANDIRS = {'amsr2': 'png_clean_dev',
                'gmi': 'png_clean_dev',
                'saphir': 'png_clean_dev',
                'ssmis': 'png_clean_dev',
                'windsat': 'png_clean_dev',
                'ssmi': 'png_clean_dev',
                'amsub': 'png_clean_dev',
                'imerg': 'png_clean_dev'}

# Setup for radius_of_influence - as readers get added to GeoIPS 2 prototype, radius of influence will be set
# appropriately within the readers and will NOT be required in this dictionary.
#ROILIST = {# 'ssmi':  [15000, 50000],
#           # 'amsub': [30000],
#           # 'mhs':   [30000],
#           #'gmi':   [10000, 20000],   # will see whether low freq with a large influence radius
#           # 'amsr2': [10000, 20000],  # this should be set in the GeoIPS2 reader
#           #'ssmis': [15000, 50000],  # 1st is for high frequency, 2nd is for low frequency, set in reader
#           }

#def set_roi(full_xarray, varname):
#    #''' Set interpolation radius of influence on the xarray object based on the dictionary configuration'''
#    # selection of radius of influence depending sensor frequency, if sensor is not included in ROILIST dictionary,
#    # assume radius of influence is set appropriately in reader - do NOT set a default here.
#    if full_xarray.source_name in ROILIST.keys():
#        if varname in VARLIST[full_xarray.source_name]:
#            # default as selection of the high requency
#            full_xarray.attrs['interpolation_radius_of_influence'] = ROILIST[full_xarray.source_name][0]
#            if varname in ['H19', 'V19', 'H37', 'V37', 'tb37H', 'tb19H', 'tb36h', 'tb36v']:
#                # low frequency
#                full_xarray.attrs['interpolation_radius_of_influence'] = ROILIST[full_xarray.source_name][1]


def interp_bg_data(vis_xarray, ir_xarray, area_def):
    interp_vis = None
    interp_ir = None
    if vis_xarray is not None:
        from geoips2.xarray_utils.interpolation import interp_nearest
        [interp_vis] = interp_nearest(area_def, vis_xarray, varlist=['Visible-Gray'])
    elif ir_xarray is not None:
        from geoips2.xarray_utils.interpolation import interp_nearest
        [interp_ir] = interp_nearest(area_def, ir_xarray, varlist=['Infrared-Gray'])
    return interp_vis, interp_ir


def get_bg_xarrays(xarray_datasets):
    ir_xarray = None
    vis_xarray = None
    for xobj in xarray_datasets:
        if xobj.source_name in VARLIST:
            sect_xarray = xobj
        if 'Infrared-Gray' in xobj.variables.keys():
            ir_xarray = xobj
            ir_covg = percent_unmasked(ir_xarray['Infrared-Gray'].to_masked_array())
        if 'Visible-Gray' in xobj.variables.keys():
            vis_xarray = xobj
            vis_covg = percent_unmasked(vis_xarray['Visible-Gray'].to_masked_array())
    if vis_xarray and ir_xarray and ir_covg > vis_covg:
        vis_xarray = None
    return vis_xarray, ir_xarray


def pick_bg_data(vis_data, ir_data, vis_xarray, ir_xarray):
    bg_mpl_colors_info = None
    bg_data = None
    bg_xarray = None
    bg_product_name_title = None
    if vis_data is not None:
        from geoips2.products.visir import DATARANGE_LIST, CMAPLIST
        from geoips2.image_utils.mpl_utils import set_matplotlib_colors_standard
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
        from geoips2.image_utils.mpl_utils import set_matplotlib_colors_standard
        # Create the matplotlib color info dict - the fields in this dictionary (cmap, norm, boundaries,
        # etc) will be used in plot_image
        bg_data = ir_data
        bg_xarray = ir_xarray
        bg_product_name_title = 'Infrared'
        bg_mpl_colors_info = set_matplotlib_colors_standard(DATARANGE_LIST['Infrared-Gray'],
                                                            cmap_name=CMAPLIST['Infrared-Gray'],
                                                            cbar_label=None,
                                                            create_colorbar=False)
    return bg_mpl_colors_info, bg_data, bg_xarray, bg_product_name_title


def is_required_product(product_list, product_name):
    if product_list is None:
        return True
    if product_name in product_list or product_name+'Nearest' in product_list:
        return True
    for rgba_prods in RGBA_PRODUCTS.values():
       if product_name in rgba_prods or product_name+'Nearest' in rgba_prods:
           return True
    for sa_prods in SINGLE_ARRAY_PRODUCTS.values():
       if product_name in sa_prods or product_name+'Nearest' in sa_prods:
           return True
    if product_name in RGBA_PRODUCTS or product_name+'Nearest' in RGBA_PRODUCTS:
        return True
    if product_name in SINGLE_ARRAY_PRODUCTS or product_name+'Nearest' in SINGLE_ARRAY_PRODUCTS:
        return True
    return False


def get_product_name(varname, product_names_dictionary):
    ''' Return the appropriate product name for a given variable name'''
    product_name = None
    for prodname, varnames in product_names_dictionary.items():
        if varname in varnames:
            product_name = prodname

    if not product_name:
        raise(ValueError,
              'Must specify current product for varname {0} in the PRODNAMES dictionary'.format(varname))

    return product_name


def get_mtif_data(sect_xarray, area_def, interp_func, **kwargs):
    ''' Return data interpolated to mtif area definition.

    '''
    mtif_xarrays = []
    import xarray
    from geoips2.sector_utils.utils import set_mtif_area_def
    curr_mtif_area_def = set_mtif_area_def(sect_xarray, area_def)
    mtif_interp_datas = interp_func(curr_mtif_area_def, sect_xarray, **kwargs)

    # If the current area definition is already included in the list of mtif xarray datasets, just add to the
    # existing dataset, don't create a new one. We want one for each shape (mtif_area_def)
    matches_mtif_xarray = False
    for mtif_xarray in mtif_xarrays:
        if curr_mtif_area_def == mtif_xarray.area_definition:
            curr_mtif_xarray = mtif_xarray
            matches_mtif_xarray = True

    # If this is a new mtif xarray shape, create a new xarray dataset with required metadata
    if not matches_mtif_xarray:
        curr_mtif_xarray = xarray.Dataset()
        curr_mtif_xarray.attrs['area_definition'] = curr_mtif_area_def
        copy_standard_metadata(sect_xarray, curr_mtif_xarray)

    for varname, mtif_interp_data in zip(kwargs['varlist'], mtif_interp_datas):
        prodname = get_product_name(varname, PRODNAMES)
        curr_mtif_xarray[prodname] = xarray.DataArray(mtif_interp_data)

    return curr_mtif_area_def, curr_mtif_xarray


# Define PMW plotting variables
def pmw_tb(xarray_datasets, area_def, productlist=None):
    '''
    Args:
        xarray_objs (list): List of xarray.Dataset objects (one Dataset for each shape/resolution)
        area_def (AreaDefinition): pyresample Area_Definition object defining the sector
        productlist (list):
            * DEFAULT None (produce all products)
            * List of strings containing desired products
    
    Returns:
        list: List of strings containing all processing and output completed within the product call.
    '''

    final_products = []
    import xarray
    # low_res_mtif_xarray = xarray.Dataset()
    png_xarray = xarray.Dataset()
    png_xarray.attrs['registered_dataset'] = True
    png_xarray.attrs['area_definition'] = area_def
    mtif_xarrays = []

    sect_xarray = None

    vis_xarray, ir_xarray = get_bg_xarrays(xarray_datasets)

    for sect_xarray in xarray_datasets:
        if sect_xarray.source_name not in VARLIST:
            LOG.info('%s not in VARLIST, skipping', sect_xarray.source_name)
            continue

        vars_to_interp = list(set(VARLIST[sect_xarray.source_name]) & set(sect_xarray.variables.keys()))
        for varname in vars_to_interp:
            LOG.info('Min/max sect %s %s / %s',
                     varname,
                     sect_xarray[varname].to_masked_array().min(),
                     sect_xarray[varname].to_masked_array().max())

        interp_vis, interp_ir = interp_bg_data(vis_xarray, ir_xarray, area_def)

        # selection of an intepolation scheme

        # Nearest interpolation scheme
        from geoips2.xarray_utils.interpolation import interp_nearest
        interp_nearest_datas = interp_nearest(area_def, sect_xarray, varlist=vars_to_interp)

        # grid interpolation scheme (choice of 'nearest', 'linear' or 'cubic')
        # from geoips2.xarray_utils.interpolation import interp_scipy_grid
        # method_interp='cubic'
        # interp_data = interp_scipy_grid(area_def, sect_xarray, varname, method=method_interp)

        # Gaussian interpolation scheme
        from geoips2.xarray_utils.interpolation import interp_gauss
        sigma = 10000        #for high frequency channels: 89, 150  etc, aslso for gmi/amsr2 37
        for i in range(len(vars_to_interp)):
            if vars_to_interp[i] in SIGMALIST:
                sigma = 25000         #for ssmi and ssmis 19 and 37 GHz 

        interp_func = interp_gauss
        interp_func_args = {'sigmaval': sigma, 'varlist': vars_to_interp}
        interp_datas = interp_func(area_def, sect_xarray, **interp_func_args)

        curr_mtif_interp_data = None
        curr_mtif_area_def = None
        
        if is_sector_type(area_def, 'atcf'):
            curr_mtif_area_def, curr_mtif_xarray = get_mtif_data(sect_xarray, area_def, interp_func, **interp_func_args)

        copy_standard_metadata(sect_xarray, png_xarray)

        for varname, interp_data, interp_nearest_data in zip(vars_to_interp, interp_datas, interp_nearest_datas):
            prodname = get_product_name(varname, PRODNAMES)
            if not is_required_product(productlist, prodname):
                LOG.info('SKIPPING PRODUCT %s not requested in product list %s', prodname, productlist)
                continue
            LOG.info('Min/max interp %s %s / %s', varname, interp_data.min(), interp_data.max())
            LOG.info('Min/max interp nearest %s %s / %s', varname, interp_nearest_data.min(), interp_nearest_data.max())
            png_xarray[prodname] = xarray.DataArray(interp_data)
            png_xarray[prodname+'Nearest'] = xarray.DataArray(interp_nearest_data)
            if is_sector_type(area_def, 'atcf'):
                curr_mtif_interp_data = curr_mtif_xarray[prodname].to_masked_array()
                mtif_exists = False
                for mtif_xarray in mtif_xarrays:
                    if mtif_xarray.dims == curr_mtif_xarray.dims:
                        mtif_exists = True
                        mtif_xarray[prodname] = xarray.DataArray(curr_mtif_interp_data)
                if not mtif_exists:
                    new_mtif_xarray = xarray.Dataset()
                    new_mtif_xarray.attrs['area_definition'] = curr_mtif_area_def
                    copy_standard_metadata(curr_mtif_xarray, new_mtif_xarray)
                    new_mtif_xarray[prodname] = xarray.DataArray(curr_mtif_interp_data)
                    mtif_xarrays += [new_mtif_xarray]

            if productlist is None or prodname not in productlist:
                final_products += plot_interp_data(png_xarray[prodname].to_masked_array(),
                                                   sect_xarray,
                                                   area_def,
                                                   prodname,
                                                   vis_data=interp_vis,
                                                   ir_data=interp_ir,
                                                   vis_xarray=vis_xarray,
                                                   ir_xarray=ir_xarray,
                                                   mtif_area_def=curr_mtif_area_def,
                                                   mtif_interp_data=curr_mtif_interp_data)
            else:
                LOG.info('SKIPPING, PRODUCT %s not requested in product list %s', prodname, productlist)

            if productlist is None or prodname+'Nearest' not in productlist:
                final_products += plot_interp_data(png_xarray[prodname+'Nearest'].to_masked_array(),
                                                   sect_xarray,
                                                   area_def,
                                                   prodname+'Nearest',
                                                   vis_data=interp_vis,
                                                   ir_data=interp_ir,
                                                   vis_xarray=vis_xarray,
                                                   ir_xarray=ir_xarray,
                                                   mtif_area_def=None,
                                                   mtif_interp_data=None)
            else:
                LOG.info('SKIPPING, PRODUCT %sNearest not requested in product list %s', prodname, productlist)

    # Now png_xarray has all of the channels of any resolution resampled to the same domain.  These can be used in RGBs.
    # Make sure all the required channels are specified in the dictionaries at the top.
    final_products += produce_single_arrays(png_xarray, mtif_xarrays,
                                            ir_data=interp_ir, vis_data=interp_vis,
                                            ir_xarray=ir_xarray, vis_xarray=vis_xarray, productlist=productlist)
    final_products += produce_rgbs(png_xarray, mtif_xarrays,
                                   ir_data=interp_ir, vis_data=interp_vis,
                                   ir_xarray=ir_xarray, vis_xarray=vis_xarray, productlist=productlist)
    return final_products


def copy_standard_metadata(orig_xarray, dest_xarray):
    for attr in ['start_datetime', 'end_datetime', 'platform_name', 'source_name', 'minimum_coverage', 'data_provider',
                 'granule_minutes']:
        if attr in orig_xarray.attrs.keys():
            dest_xarray.attrs[attr] = orig_xarray.attrs[attr]


def create_color37_rgba_product(xarray_obj):
    from geoips2.data_manipulations.corrections import apply_data_range, apply_gamma
    red = (2.181*xarray_obj['37V'].to_masked_array())-(1.181*xarray_obj['37H'].to_masked_array())
    red = apply_data_range(red, 260.0, 280.0, min_outbounds='crop', max_outbounds='crop', norm=True, inverse=True)
    red = apply_gamma(red, 1.0)

    grn = (xarray_obj['37V'].to_masked_array() - 180.0) / (300.0 - 180.0)
    grn = apply_data_range(grn, 0.0, 1.0, min_outbounds='crop', max_outbounds='crop', norm=True, inverse=False)
    grn = apply_gamma(grn, 1.0)

    blu = (xarray_obj['37H'].to_masked_array() - 160.0) / (300.0 - 160.0)
    blu = apply_data_range(blu, 0.0, 1.0, min_outbounds='crop', max_outbounds='crop', norm=True, inverse=False)
    blu = apply_gamma(blu, 1.0)

    from geoips2.image_utils.mpl_utils import alpha_from_masked_arrays, rgba_from_arrays
    alp = alpha_from_masked_arrays([red, grn, blu])
    rgba = rgba_from_arrays(red, grn, blu, alp)
    return rgba


def create_37pct_single_array_product(xarray_obj):
    from geoips2.data_manipulations.corrections import apply_data_range
    min_val = 230.0
    max_val = 280.0
    img = (2.15*xarray_obj['37V'].to_masked_array())-(1.15*xarray_obj['37H'].to_masked_array())
    img = apply_data_range(img, min_val, max_val, min_outbounds='crop', max_outbounds='mask', norm=False, inverse=False)
    from geoips2.image_utils.mpl_utils import set_matplotlib_colors_37pct
    mpl_colors_info = set_matplotlib_colors_37pct(min_tb=min_val, max_tb=max_val)
    return img, min_val, max_val, mpl_colors_info


def create_color89_rgba_product(xarray_obj):
    from geoips2.data_manipulations.corrections import apply_data_range, apply_gamma
    red = (1.818*xarray_obj['89V'].to_masked_array())-(0.818*xarray_obj['89H'].to_masked_array())
    red = apply_data_range(red, 220.0, 310.0, min_outbounds='crop', max_outbounds='crop', norm=True, inverse=True)
    red = apply_gamma(red, 1.0)

    grn = (xarray_obj['89H'].to_masked_array() - 240.0) / (300.0 - 240.0)
    grn = apply_data_range(grn, 0.0, 1.0, min_outbounds='crop', max_outbounds='crop', norm=True, inverse=False)
    grn = apply_gamma(grn, 1.0)

    blu = (xarray_obj['89V'].to_masked_array() - 270.0) / (290.0 - 270.0)
    blu = apply_data_range(blu, 0.0, 1.0, min_outbounds='crop', max_outbounds='crop', norm=True, inverse=False)
    blu = apply_gamma(blu, 1.0)

    from geoips2.image_utils.mpl_utils import alpha_from_masked_arrays, rgba_from_arrays
    alp = alpha_from_masked_arrays([red, grn, blu])
    rgba = rgba_from_arrays(red, grn, blu, alp)
    return rgba


def create_89pct_single_array_product(xarray_obj):
    from geoips2.data_manipulations.corrections import apply_data_range
    min_val = 105.0
    max_val = 280.0
    img = (1.7*xarray_obj['89V'].to_masked_array())-(0.7*xarray_obj['89H'].to_masked_array())
    img = apply_data_range(img, min_val, max_val, min_outbounds='crop', max_outbounds='mask', norm=False, inverse=False)
    from geoips2.image_utils.mpl_utils import set_matplotlib_colors_89pct
    mpl_colors_info = set_matplotlib_colors_89pct(min_tb=min_val, max_tb=max_val)
    return img, min_val, max_val, mpl_colors_info


def produce_single_arrays(png_xarray, mtif_xarrays=None,
                          ir_data=None, vis_data=None,
                          vis_xarray=None, ir_xarray=None, productlist=None):
    final_products = []
    if mtif_xarrays is None:
        mtif_xarrays = []

    mtif_area_definition = None
    mtif_single_array_data = None

    for product_name in SINGLE_ARRAY_PRODUCTS:
        if productlist is not None and product_name not in productlist:
            LOG.info('SKIPPING, PRODUCT %s not requested in product list %s', product_name, productlist)
            continue
        if set(SINGLE_ARRAY_PRODUCTS[product_name]).issubset(png_xarray.variables.keys()):
            LOG.info('Running combined single array product %s', product_name)
            from importlib import import_module
            single_array_algorithm = getattr(import_module('{0}.{1}.{2}'.format('geoips2',
                                                                                'products', 'pmw_tb')),
                                             'create_{0}_single_array_product'.format(product_name))
            single_array_data, min_val, max_val, mpl_colors_info = single_array_algorithm(png_xarray)
            mtif_single_array_data = None
            for mtif_xarray in mtif_xarrays:
                if set(SINGLE_ARRAY_PRODUCTS[product_name]).issubset(mtif_xarray.variables.keys()):
                    mtif_single_array_data, min_val, max_val, mpl_colors_info = single_array_algorithm(mtif_xarray)
                    mtif_area_definition = mtif_xarray.area_definition

            final_products += plot_interp_data(single_array_data,
                                               png_xarray,
                                               png_xarray.area_definition,
                                               product_name,
                                               vis_data=vis_data,
                                               ir_data=ir_data,
                                               vis_xarray=vis_xarray,
                                               ir_xarray=ir_xarray,
                                               mtif_area_def=mtif_area_definition,
                                               mtif_interp_data=mtif_single_array_data,
                                               min_val=min_val,
                                               max_val=max_val,
                                               mpl_colors_info=mpl_colors_info)

    return final_products


def produce_rgbs(png_xarray, mtif_xarrays,
                 ir_data=None, vis_data=None,
                 vis_xarray=None, ir_xarray=None, productlist=None):
    final_products = []
    mtif_final_products = []

    bg_mpl_colors_info, bg_data, bg_xarray, bg_product_name_title = pick_bg_data(vis_data, ir_data,
                                                                                 vis_xarray, ir_xarray) 

    for product_name in RGBA_PRODUCTS:
        if productlist is not None and product_name not in productlist:
            LOG.info('SKIPPING, PRODUCT %s not requested in product list %s', product_name, productlist)
            continue
        if set(RGBA_PRODUCTS[product_name]).issubset(png_xarray.variables.keys()):
            LOG.info('Running combined product %s', product_name)
            from importlib import import_module
            rgb_algorithm = getattr(import_module('{0}.{1}.{2}'.format('geoips2', 'products', 'pmw_tb')),
                                    'create_{0}_rgba_product'.format(product_name))
            rgb_data = rgb_algorithm(png_xarray)
            from geoips2.image_utils.mpl_utils import percent_unmasked_rgba
            covg = percent_unmasked_rgba(rgb_data)

            if is_sector_type(png_xarray.area_definition, 'atcf'):
                atcf_fname = output_atcf_fname(png_xarray.area_definition, png_xarray, product_name, covg,
                                               output_type='png', output_type_dir=PNGDIRS[png_xarray.source_name],
                                               product_dir=product_name)
                old_tcweb_fname = output_atcf_fname(png_xarray.area_definition, png_xarray, product_name, covg,
                                                    output_type='jpg',
                                                    product_dir=product_name, output_old_tc_web=True)
                annotated_fnames = [atcf_fname]
                if old_tcweb_fname is not None and png_xarray.source_name in OLDWEB and product_name in OLDWEB[png_xarray.source_name]:
                    annotated_fnames += [old_tcweb_fname]
                clean_fname = output_atcf_fname(png_xarray.area_definition, png_xarray, product_name+'Clean', covg,
                                                output_type='png',
                                                output_type_dir=PNGCLEANDIRS[png_xarray.source_name],
                                                product_dir=product_name)
            else:
                # Get the output filename from sector, and xarray objects
                annotated_fnames = [output_geoips_fname(png_xarray.area_definition, png_xarray, product_name, covg)]
                clean_fname = output_geoips_fname(png_xarray.area_definition, png_xarray,
                                                  product_name+'Clean', covg)

            from geoips2.output_formats.image import create_standard_imagery

            from geoips2.image_utils.mpl_utils import set_matplotlib_colors_rgb
            # This basically sets everything to False or None, since colors are specified within the rgb array
            mpl_colors_info = set_matplotlib_colors_rgb()
            final_products += create_standard_imagery(png_xarray.area_definition,
                                                      plot_data=rgb_data,
                                                      xarray_obj=png_xarray,
                                                      product_name_title=product_name,
                                                      clean_fname=clean_fname,
                                                      annotated_fnames=annotated_fnames,
                                                      mpl_colors_info=mpl_colors_info,
                                                      boundaries_info=BOUNDARIES_INFO,
                                                      gridlines_info=GRIDLINES_INFO,
                                                      bg_data=bg_data,
                                                      bg_mpl_colors_info=bg_mpl_colors_info,
                                                      bg_xarray=bg_xarray,
                                                      bg_product_name_title=bg_product_name_title,
                                                      remove_duplicate_minrange=10)
            from geoips2.xarray_utils.outputs import output_metoctiff
            for mtif_xarray in mtif_xarrays:
                if set(RGBA_PRODUCTS[product_name]).issubset(mtif_xarray.variables.keys()):
                    mtif_rgb_data = rgb_algorithm(mtif_xarray)
                    curr_final_products = output_metoctiff(product_name, mtif_xarray.area_definition,
                                                           mtif_xarray,
                                                           mtif_rgb_data,
                                                           existing_image=mtif_rgb_data,
                                                           coverage=covg,
                                                           atcf_dir=ATCFDIRS[mtif_xarray.source_name])
                    mtif_final_products += produce_all_sector_metadata(curr_final_products,
                                                                       mtif_xarray.area_definition,
                                                                       mtif_xarray,
                                                                       METADATADIRS[mtif_xarray.source_name])
                    mtif_final_products += curr_final_products

    # NOTE this produces metadata based on "area_def" - if we begin re-centering the storm, ensure this is updated to
    # reflect varying area definitions
    final_products += produce_all_sector_metadata(final_products, png_xarray.area_definition, png_xarray,
                                                  metadata_dir=METADATADIRS[png_xarray.source_name])
    return mtif_final_products+final_products


def plot_interp_data(interp_data, xarray_obj, area_def, product_name,
                     mtif_area_def=None, mtif_interp_data=None,
                     min_val=None, max_val=None, mpl_colors_info=None,
                     vis_data=None, ir_data=None, vis_xarray=None, ir_xarray=None):
    ''' Plot the current interpolated data array, using metadata found in xarray_obj and area_def
        interp_data (numpy.ndarray) : ndarray or MaskedArray of data to plot
        xarray_obj (Dataset) : xarray Dataset containing appropriate metadata for naming files, etc
        area_def (AreaDefinition) : Pyresample AreaDefinition specifying the region to plot
        mtif_area_def (AreaDefinition) : DEFAULT None, Area definition for mtif creation
        mtif_interp_data (numpy.ndarray) : DEFAULT None, ndarray or MaskedArray of mtif data to plot, interpolated to
                                                         mtif_area_def

    Returns:
        (list) : List of strings containing full paths to all output products created
    '''

    final_products = []
    mtif_final_products = []

    bg_mpl_colors_info, bg_data, bg_xarray, bg_product_name_title = pick_bg_data(vis_data, ir_data,
                                                                                 vis_xarray, ir_xarray) 

    covg = percent_unmasked(interp_data)
    if covg > 0:                # test a data coverage criterion
        if is_sector_type(area_def, 'atcf'):

            # Get the output filename from sector, and xarray objects
            atcf_fname = output_atcf_fname(area_def, xarray_obj, product_name, covg,
                                           output_type='png', output_type_dir=PNGDIRS[xarray_obj.source_name],
                                           product_dir=product_name)
            old_tcweb_fname = output_atcf_fname(area_def, xarray_obj, product_name, covg,
                                                output_type='jpg',
                                                product_dir=product_name, output_old_tc_web=True)
            annotated_fnames = [atcf_fname]
            if old_tcweb_fname is not None and xarray_obj.source_name in OLDWEB and product_name in OLDWEB[xarray_obj.source_name]:
                annotated_fnames += [old_tcweb_fname]
            clean_fname = output_atcf_fname(area_def, xarray_obj, product_name+'Clean', covg,
                                                 output_type='png',
                                                 output_type_dir=PNGCLEANDIRS[xarray_obj.source_name],
                                                 product_dir=product_name)
        else:
            # Get the output filename from sector, and xarray objects
            annotated_fnames = [output_geoips_fname(area_def, xarray_obj, product_name, covg)]
            clean_fname = output_geoips_fname(area_def, xarray_obj, product_name+'Clean', covg)

        # Create the matplotlib color info dict - the fields in this dictionary (cmap, norm, boundaries,
        # etc) will be used in plot_image to ensure the image matches the colorbar.
        # selelec a relative color scheme depending on Hi or Lo frequency channels

        if mpl_colors_info is not None and min_val is not None and max_val is not None:
            curr_min_tb = min_val
            curr_max_tb = max_val
            mpl_colors_info = mpl_colors_info
        elif product_name in PRODTYPES['37H']:
            # color scheme for low frequency
            from geoips2.image_utils.mpl_utils import set_matplotlib_colors_37H
            curr_min_tb = MIN_TB_LO
            curr_max_tb = MAX_TB_LO
            mpl_colors_info = set_matplotlib_colors_37H(min_tb=curr_min_tb, max_tb=curr_max_tb)
        elif product_name in PRODTYPES['150H']:
            # default for high frequency (150-190 GHz) color scheme
            from geoips2.image_utils.mpl_utils import set_matplotlib_colors_150H
            curr_min_tb = 110
            curr_max_tb = 310
            mpl_colors_info = set_matplotlib_colors_150H(min_tb=curr_min_tb, max_tb=curr_max_tb)
        elif product_name in PRODTYPES['89H']:
            # default for high frequency (85-91 GHz) color scheme
            from geoips2.image_utils.mpl_utils import set_matplotlib_colors_89H
            curr_min_tb = MIN_TB_HI
            curr_max_tb = MAX_TB_HI
            mpl_colors_info = set_matplotlib_colors_89H(min_tb=curr_min_tb, max_tb=curr_max_tb)
        elif product_name in PRODTYPES['Rain']:
            # default for precipitation color scheme
            from geoips2.image_utils.mpl_utils import set_matplotlib_colors_rain
            curr_min_tb = 0.05              # use ***_min _tb because the name is also used in mtif output 
            curr_max_tb = 50                 # otherwise, more changes are needed
            mpl_colors_info = set_matplotlib_colors_rain(min_tb=curr_min_tb, max_tb=curr_max_tb)
            # mask 0 rainfall
            from geoips2.data_manipulations.corrections import apply_data_range
            interp_data = apply_data_range(interp_data, min_val=curr_min_tb, max_val=None,
                                           min_outbounds='mask', max_outbounds=None,
                                           norm=False, inverse=False)
        else:
            raise(ValueError, 'Must specify which product type the current product falls under in the PRODTYPES' +
                  'dictionary')

        from geoips2.output_formats.image import create_standard_imagery

        final_products += create_standard_imagery(area_def,
                                                  plot_data=interp_data,
                                                  xarray_obj=xarray_obj,
                                                  product_name_title=product_name,
                                                  clean_fname=clean_fname,
                                                  annotated_fnames=annotated_fnames,
                                                  mpl_colors_info=mpl_colors_info,
                                                  boundaries_info=BOUNDARIES_INFO,
                                                  gridlines_info=GRIDLINES_INFO,
                                                  bg_data=bg_data,
                                                  bg_mpl_colors_info=bg_mpl_colors_info,
                                                  bg_xarray=bg_xarray,
                                                  bg_product_name_title=bg_product_name_title,
                                                  remove_duplicate_minrange=10)
        if mtif_area_def:
            from geoips2.xarray_utils.outputs import output_metoctiff
            mtif_final_products += output_metoctiff(product_name, mtif_area_def, xarray_obj, mtif_interp_data,
                                                    requested_data_min=curr_min_tb,
                                                    requested_data_max=curr_max_tb,
                                                    scale_data_min=MIN_SCALE_VALUE,
                                                    scale_data_max=MAX_SCALE_VALUE,
                                                    missing_value=MISSING_SCALE_VALUE,
                                                    coverage=covg,
                                                    mpl_cmap=mpl_colors_info['cmap'],
                                                    units=MTIF_UNITS,
                                                    atcf_dir=ATCFDIRS[xarray_obj.source_name])

    else:
        LOG.info('Insufficient coverage, skipping')

    # NOTE this produces metadata based on "area_def" - if we begin re-centering the storm, ensure this is updated to
    # reflect varying area definitions
    final_products += produce_all_sector_metadata(final_products, area_def, xarray_obj,
                                                  metadata_dir=METADATADIRS[xarray_obj.source_name])
    mtif_final_products += produce_all_sector_metadata(mtif_final_products, mtif_area_def, xarray_obj,
                                                       metadata_dir=METADATADIRS[xarray_obj.source_name])
    return final_products+mtif_final_products
