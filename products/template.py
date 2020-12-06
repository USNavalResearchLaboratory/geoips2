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

LOG = logging.getLogger(__name__)

# Specify which channel / variable to plot for demonstration purposes for each data type
VARLIST = {'smap-spd': ['wind_speed_kts'],
           'smos-spd': ['wind_speed_kts'],
           'amsr2': ['wind_speed_kts', 'tb89hA'],
           'amsr2rss': ['wind_speed_kts'],
           'amsub': ['Chan2_AT'],
           'sar-spd': ['wind_speed_kts'],
           'ascat': ['wind_speed_kts'],
           'ascatuhr': ['wind_speed_kts'],
           'ascatuhrsig0': ['sig_fore'],
           'windsat': ['wind_speed', 'ftb37h'],
           'abi': ['B14BT'],
           'ahi': ['B14BT'],
           'seviri': ['B09BT'],
           'gmi': ['tb89h'],
           'ssmis': ['ch18', 'tb89h'],
           'ssmi': ['tb89h'],
           'amsre': ['tb89h'],
           'tmi': ['tb89h'],
           'viirs': ['I05TB']}                     # test viirs IMG05 TBs for viisr infrared at 11mu 

DATA_RANGE_LIST = {'ascatuhrsig0': [-40.0, 0],
                   'viirs': [183, 303]}

# CMAP_LIST = {'ascatuhrsig0': 'Greys_r'}
CMAP_LIST = {}

CBAR_LABEL_LIST = {'ascatuhrsig0': 'Sigma-0 (dB)'}

ROILIST = {'windsat': 5000}


def template(xarray_datasets, area_def):
    ''' Template for creating a simple product from a single channel from each supported data type.

    All products found in geoips2/products must have consistent call signatures, and require
    no return values.  All data processing, plotting, and data and imagery outputs must be completed
    within the product algorithm.

    Call signature for all products found in geoips2/products/<product_name>.py:
    def <product_name>(xarray_datasets, area_def):

      NOTE FOR GEOIPS1 Interface: Link directly from geoips/productfiles/<source_name>/<product_name>.xml
                                  to geoips2.products.<product_name>.<product_name>
                                  Must be consistently named.

          in geoips/geoimg/plot/prototypealg.py
              scifile is converted to xarray BEFORE being passed (standard variables latitude, longitude, timestamp)
              sector is converted to area_def BEFORE being passed  (standard attributes sector_*)
          from geoips2.geoips1_utils.scifile import xarray_from_scifile
          from geoips2.geoips1_utils.sector import area_def_from_sector

      NOTE FOR GEOIPS2 Prototype Interface: This will be imported and called from modules found in:
          geoips2/drivers/

    Args:
        xarray_datasets (list of xarray.Dataset) : list of xarray Dataset objects including all required variables.
                          Required variables: 'latitude', 'longitude'
                          Optional variable; 'timestamp'
                          Required attributes: 'start_datetime', 'end_datetime',
                                               'source_name', 'platform_name', 'data_provider'
        area_def (AreaDefinition) : pyresample AreaDefinition object specifying the current location information.
                          This includes standard pyresample AreaDefinition attributes, as well as additional
                          dynamic or static sector info (ie, storm name, basin, etc for TCs)
                          Extra GeoIPS 2 required attributes:
                                'sector_info', 'sector_type'
                          optional attributes (if included, assumed dynamic):
                                'sector_start_datetime', 'sector_end_datetime'


    Returns:
        (None). All processing, outputs, and plotting is complete at the end of the product scripts - no return value
    '''
    final_outputs = []
    LOG.info('Running area_def %s', area_def)

    # Just write out registered datafile ...
    # start_dtstr = xarray_datasets[0].start_datetime.strftime('%Y%m%d.%H%M')
    # ncfname = start_dtstr+area_def.area_id+'.nc'
    # from geoips2.xarray_utils.outputs import write_xarray_netcdf
    from IPython import embed as shell
    # write_xarray_netcdf(xarray_datasets[0], ncfname)

    full_xarray = None
    # Assuming for template, we are just plotting a single variable per file, so loop through until we find it.
    # Note some "source_names" can have multiple file types, but there will only be one of
    # the listed variables per file.
    for xarray_dataset in xarray_datasets:
        source_name = xarray_dataset.source_name
        for currvarname in VARLIST[source_name]:
            if currvarname not in xarray_dataset.variables.keys():
                # LOG.info('SKIPPING variable %s, not in current xarray object', currvarname)
                continue
            LOG.info('FOUND variable %s, in xarray dataset with dims %s',
                     currvarname, xarray_dataset['latitude'].dims)
            varname = currvarname
            full_xarray = xarray_dataset

    if full_xarray is None:
        LOG.info('FAILED variable %s not found in any xarray Datasets')
        return final_outputs
    # Base product name here is "Template" for plotting titles, etc
    product_name = 'Template'

    # If we want to override the default radius of influence, pull it from the list above.
    if source_name in ROILIST.keys():
        full_xarray.attrs['interpolation_radius_of_influence'] = ROILIST[source_name]

    # logging information for what we are sectoring (temporally and spatially for dynamic, just temporally for static
    if hasattr(area_def, 'sector_start_datetime') and area_def.sector_start_datetime:
        LOG.info('Trying to sector %s with dynamic time %s, %s points',
                 area_def.area_id, area_def.sector_start_datetime, full_xarray['latitude'].size)
    else:
        LOG.info('Trying to sector %s, %s points', area_def.area_id, full_xarray['latitude'].size)

    # Compile a list of variables that will be used to sector - the current data variable, and we will add in
    # the appropriate latitude and longitude variables (of the same shape as data), and if it exists the
    # appropriately shaped timestamp array
    vars_to_sect = [varname, 'latitude', 'longitude']
    if 'timestamp' in full_xarray.variables.keys():
        vars_to_sect += ['timestamp']

    # The list of variables in vars_to_sect must ALL be the same shape
    from geoips2.xarray_utils.data import sector_xarray_dataset
    sect_xarray = sector_xarray_dataset(full_xarray,
                                        area_def,
                                        vars_to_sect)

    # numpy arrays fail if numpy_array is None, and xarrays fail if x_array == None
    if sect_xarray is None:
        LOG.info('No coverage - skipping')
        return final_outputs

    sect_xarray.attrs['area_def'] = area_def

    # If you have normal old 2d arrays, you don't have to worry about any of the array_nums pieces.
    array_nums = [None]
    if len(sect_xarray[varname].shape) == 3:
        array_nums = range(0, sect_xarray[varname].shape[2])

    from geoips2.xarray_utils.interpolation import interp_nearest
    from geoips2.xarray_utils.outputs import output_geoips_fname
    from geoips2.data_manipulations.info import percent_unmasked
    from geoips2.image_utils.mpl_utils import set_matplotlib_colors_standard

    final_products = []
    for array_num in array_nums:
        # Just pass array_num=None if it is a single 2d array
        [interp_data] = interp_nearest(area_def, sect_xarray, varlist=[varname], array_num=array_num)
        data_range = [interp_data.min(), interp_data.max()]
        cmap_name = None
        cbar_label = None
        if sect_xarray.source_name in CBAR_LABEL_LIST:
            cbar_label = CBAR_LABEL_LIST[sect_xarray.source_name]
        if sect_xarray.source_name in CMAP_LIST:
            cmap_name = CMAP_LIST[sect_xarray.source_name]
        if sect_xarray.source_name in DATA_RANGE_LIST:
            data_range = DATA_RANGE_LIST[sect_xarray.source_name]
        covg = percent_unmasked(interp_data)

        if covg > 0:
            from geoips2.sector_utils.utils import is_sector_type
            if is_sector_type(area_def, 'atcf'):
                # get filename from objects
                prodname = '{0}_{1}'.format(product_name, varname)
                from geoips2.xarray_utils.outputs import output_atcf_fname
                atcf_fname = output_atcf_fname(area_def, sect_xarray, prodname, covg)
                atcf_fname_clean = output_atcf_fname(area_def, sect_xarray, prodname+'Clean', covg)

                mpl_colors_info = set_matplotlib_colors_standard(data_range=data_range,
                                                                 cmap_name=cmap_name,
                                                                 cbar_label=cbar_label)

                from geoips2.output_formats.image import create_standard_imagery
                final_products += create_standard_imagery(area_def,
                                                          plot_data=interp_data,
                                                          xarray_obj=sect_xarray,
                                                          product_name_title=prodname,
                                                          clean_fname=atcf_fname_clean,
                                                          annotated_fnames=[atcf_fname],
                                                          mpl_colors_info=mpl_colors_info)

            else:
                # Get the output filename from sector, and xarray objects
                prodname = '{0}_{1}'.format(product_name, varname)
                web_fname = output_geoips_fname(area_def, sect_xarray, prodname, covg,
                                                product_dir=product_name,
                                                source_dir=product_name)
                web_fname_clean = output_geoips_fname(area_def, sect_xarray, prodname+'Clean', covg,
                                                      product_dir=product_name,
                                                      source_dir=product_name)

                mpl_colors_info = set_matplotlib_colors_standard(data_range=data_range,
                                                                 cmap_name=cmap_name,
                                                                 cbar_label=cbar_label)

                from geoips2.output_formats.image import create_standard_imagery
                final_products += create_standard_imagery(area_def,
                                                          plot_data=interp_data,
                                                          xarray_obj=sect_xarray,
                                                          product_name_title=prodname,
                                                          clean_fname=web_fname_clean,
                                                          annotated_fnames=[web_fname],
                                                          mpl_colors_info=mpl_colors_info)

        else:
            LOG.info('Insufficient coverage, skipping')

    LOG.info('The following products were successfully produced from %s', __file__)
    for final_product in final_products:
        LOG.info('PRODUCTSUCCESS %s', final_product)

    from geoips2.output_formats.metadata import produce_all_sector_metadata
    final_products += produce_all_sector_metadata(final_products, area_def, full_xarray)

    return final_products
