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

''' Driver for standard single channel products '''

import logging

from geoips2.interface_modules.procflows.single_source import PMW_NUM_PIXELS_X, PMW_NUM_PIXELS_Y, PMW_PIXEL_SIZE_X, PMW_PIXEL_SIZE_Y

LOG = logging.getLogger(__name__)

procflow_type = 'standard'


def plot_data(alg_xarray, area_def, output_format, product_name, output_fnames,
              bg_xarray=None, bg_product_name=None, **kwargs):

    from geoips2.dev.output import get_outputter, get_outputter_type

    output_func = get_outputter(output_format)
    output_func_type = get_outputter_type(output_format)
    if output_func_type == 'xarray_data':
        final_products = output_func(xarray_obj=alg_xarray,
                                     product_names=[product_name, 'latitude', 'longitude'],
                                     output_fnames=output_fnames)
    else:
        from geoips2.dev.cmap import get_cmap
        from geoips2.dev.product import get_cmap_name, get_cmap_args

        cmap_func_name = get_cmap_name(product_name, alg_xarray.source_name)
        mpl_colors_info = None
        if cmap_func_name is not None:
            cmap_func = get_cmap(cmap_func_name)
            cmap_args = get_cmap_args(product_name, alg_xarray.source_name)
            mpl_colors_info = cmap_func(**cmap_args)

        if output_func_type == 'image_overlay':
            bg_data = None
            bg_mpl_colors_info = None
            if bg_xarray is not None:
                bg_cmap_func_name = get_cmap_name(bg_product_name, bg_xarray.source_name)
                bg_mpl_colors_info = None
                if bg_cmap_func_name is not None:
                    bg_cmap_func = get_cmap(bg_cmap_func_name)
                    bg_cmap_args = get_cmap_args(bg_product_name, bg_xarray.source_name)
                    bg_mpl_colors_info = bg_cmap_func(**bg_cmap_args)
                bg_data = bg_xarray[bg_product_name].to_masked_array()

            final_products = output_func(area_def,
                                         xarray_obj=alg_xarray,
                                         product_name_title=product_name,
                                         product_name=product_name,
                                         output_fnames=output_fnames,
                                         mpl_colors_info=mpl_colors_info,
                                         bg_xarray=bg_xarray,
                                         bg_data=bg_data,
                                         bg_product_name_title=bg_product_name,
                                         bg_mpl_colors_info=bg_mpl_colors_info,
                                         **kwargs)
        else:
            final_products = output_func(area_def,
                                         xarray_obj=alg_xarray,
                                         product_name_title=product_name,
                                         product_name=product_name,
                                         output_fnames=output_fnames,
                                         mpl_colors_info=mpl_colors_info,
                                         **kwargs)
    return final_products


def get_bg_xarray(sect_xarrays, area_def, product_name):

    from geoips2.dev.interp import get_interp
    from geoips2.dev.product import get_interp_name, get_interp_args
    interp_func_name = get_interp_name(product_name, sect_xarrays['METADATA'].source_name)
    interp_func = None
    if interp_func_name is not None:
        interp_func = get_interp(interp_func_name)
        interp_args = get_interp_args(product_name, sect_xarrays['METADATA'].source_name)

    alg_xarray = None

    # If this is a preprocessed data file with the final product in it, just pull the final product
    # Must take out METADATA dataset!
    if len(set(sect_xarrays.keys()).difference({'METADATA'})) == 1\
       and product_name in list(sect_xarrays.values())[0].variables:
        sect_xarray = list(sect_xarrays.values())[0]
        LOG.info('Min/max %s %s / %s',
                 product_name,
                 sect_xarray[product_name].to_masked_array().min(),
                 sect_xarray[product_name].to_masked_array().max())

        alg_xarray = interp_func(area_def, sect_xarray, alg_xarray, varlist=[product_name], **interp_args)

        LOG.info('Min/max interp %s %s / %s',
                 product_name,
                 alg_xarray[product_name].min(),
                 alg_xarray[product_name].max())

    # If this is a raw datafile, pull the required variables for applying the given algorithm, and generate the
    # product array.
    else:
        from geoips2.interface_modules.procflows.single_source import pad_area_definition
        pad_area_def = pad_area_definition(area_def)
        # Ensure pre-processed and raw look the same - this requires applying algorithm to padded sectored data,
        # since that is what is written out to the pre-processed netcdf file,
        # then interpolating to the desired area definition.
        from geoips2.interface_modules.procflows.single_source import get_alg_xarray
        sect_xarray = get_alg_xarray(sect_xarrays, pad_area_def, product_name)
        alg_xarray = interp_func(area_def, sect_xarray, alg_xarray, varlist=[product_name])

    alg_xarray.attrs['registered_dataset'] = True
    alg_xarray.attrs['area_definition'] = area_def
    if product_name in alg_xarray.variables:
        from geoips2.interface_modules.procflows.single_source import add_filename_extra_field
        alg_xarray = add_filename_extra_field(alg_xarray,
                                              'background_data',
                                              f'bg{product_name}')

    return alg_xarray


def overlay(fnames, command_line_args=None):
    ''' Workflow for running PMW brightness temperature products, for all sensors.

    Args:
        fnames (list) : List of strings specifying full paths to input file names to process
        command_line_args (dict) : dictionary of command line arguments
                                     'reader_name': Explicitly request reader
                                                      geoips2*.readers.reader_name.reader_name
                                     Optional: 'sectorfiles': list of YAML sectorfiles
                                               'sector_list': list of desired sectors found in "sectorfiles"
                                                                tc<YYYY><BASIN><NUM><NAME> for TCs,
                                                                ie tc2020sh16gabekile
                                     If sectorfiles and sector_list not included, looks in database
    Returns:
        (list) : Return list of strings specifying full paths to output products that were produced
    '''
    from datetime import datetime
    process_datetimes = {}
    process_datetimes['overall_start'] = datetime.utcnow()
    final_products = []
    removed_products = []
    saved_products = []

    from geoips2.commandline.args import check_command_line_args

    check_command_line_args(['sector_list', 'sectorfiles',  # Static sectors
                             'tcdb', 'tcdb_sector_list',  # TC Database sectors
                             'trackfiles', 'trackfile_parser', 'trackfile_sector_list',  # Flat text trackfile
                             'reader_name', 'product_name',
                             'bg_reader_name', 'bg_fnames', 'bg_product_name',
                             'output_format', 'filename_format',
                             'gridlines_params', 'boundaries_params',
                             'adjust_area_def'],
                             command_line_args)

    product_name = command_line_args['product_name']  # 89HNearest
    filename_format = command_line_args['filename_format']  # tc_fname
    output_format = command_line_args['output_format']  # output_formats.annotated_imagery
    reader_name = command_line_args['reader_name']  # ssmis_binary
    bg_reader_name = command_line_args['bg_reader_name']  # geoips_netcdf if pre-processed, raw data format otherwise
    bg_fnames = command_line_args['bg_fnames']  # Filenames to use for background
    bg_product_name = command_line_args['bg_product_name']  # Filenames to use for background
    compare_paths = command_line_args['compare_paths']
    compare_outputs_module = command_line_args['compare_outputs_module']
    adjust_area_def = command_line_args['adjust_area_def']
    from geoips2.dev.gridlines import get_gridlines, set_lonlat_spacing
    from geoips2.dev.boundaries import get_boundaries
    gridlines_info = get_gridlines(command_line_args['gridlines_params'])
    boundaries_info = get_boundaries(command_line_args['boundaries_params'])

    from geoips2.stable.reader import get_reader
    reader = get_reader(reader_name)
    bg_reader = get_reader(bg_reader_name)

    num_jobs = 0
    xobjs = reader(fnames, metadata_only=True)
    bg_xobjs = bg_reader(bg_fnames, metadata_only=True)
    from geoips2.xarray_utils.data import sector_xarrays

    from geoips2.dev.product import get_required_variables
    variables = get_required_variables(product_name, xobjs['METADATA'].source_name)
    bg_variables = get_required_variables(bg_product_name, bg_xobjs['METADATA'].source_name)

    from geoips2.interface_modules.procflows.single_source import get_area_defs_from_command_line_args
    area_defs = get_area_defs_from_command_line_args(command_line_args, xobjs, variables)
    if len(area_defs) > 1:
        raise ValueError('Overlay procflow can only be run on a single sector - ensure multiple sectors not attempted')

    area_def = area_defs[0]

    from geoips2.interface_modules.output_formats.utils.metadata import produce_all_sector_metadata
    from geoips2.filenames.duplicate_files import remove_duplicates

    from geoips2.interface_modules.procflows.single_source import pad_area_definition
    pad_area_def = pad_area_definition(area_def)

    # Read in primary (foreground) data files
    xobjs = reader(fnames, metadata_only=False, chans=variables, area_def=pad_area_def)
    # Read in background data files.
    bg_xobjs = bg_reader(bg_fnames, metadata_only=False, chans=bg_variables, area_def=pad_area_def)

    process_datetimes[area_def.area_id] = {}
    process_datetimes[area_def.area_id]['start'] = datetime.utcnow()
    # Sector to pad_area_def to give us some wiggle room for recentering
    sect_xarrays = sector_xarrays(xobjs, pad_area_def, varlist=variables, drop=True)

    # Always sector to pad_area_def for bg xarrays initially - start datetime is based off primary data.
    # bg_xarrays will be interpolated to area_def at the last step.
    bg_sect_xarrays = sector_xarrays(bg_xobjs, pad_area_def, varlist=bg_variables+[bg_product_name])

    if adjust_area_def:
        from geoips2.geoips2_utils import find_entry_point
        area_def_adjuster = find_entry_point('area_def_adjusters', adjust_area_def)
        area_def = area_def_adjuster(sect_xarrays,
                                     area_def,
                                     variables)
        # MLS CHANGES TEST OUTPUT FULL SECTORING Allow recentering with foreground or background data
        # area_def = area_def_adjuster(sect_xarrays+bg_sect_xarrays,
        #                              area_def,
        #                              variables+bg_variables+[bg_product_name])

    all_vars = []
    for key, xobj in sect_xarrays.items():
        all_vars += list(xobj.variables.keys())

    # If the required variables are not contained within the xarray objects, do not
    # attempt to process (variables in product algorithm are not available)
    if set(variables).issubset(all_vars):
        from geoips2.dev.output import get_outputter, get_outputter_type
        from geoips2.interface_modules.procflows.single_source import get_alg_xarray, get_filename
        
        sect_xarrays = sector_xarrays(sect_xarrays, area_def, varlist=variables, drop=True)
        alg_xarray = get_alg_xarray(sect_xarrays, area_def, product_name)
        bg_xarray = get_bg_xarray(bg_sect_xarrays, area_def, bg_product_name)

        from geoips2.interface_modules.procflows.single_source import combine_filename_extra_fields
        alg_xarray = combine_filename_extra_fields(bg_xarray, alg_xarray)

        output_fnames = []
        output_fnames += [get_filename(alg_xarray, area_def, filename_format, product_name)]
        if gridlines_info is not None:
            gridlines_info = set_lonlat_spacing(gridlines_info, area_def)
            curr_products = plot_data(alg_xarray,
                                      area_def,
                                      output_format,
                                      product_name,
                                      output_fnames,
                                      bg_xarray,
                                      bg_product_name,
                                      gridlines_info=gridlines_info,
                                      boundaries_info=boundaries_info)
        else:
            curr_products = plot_data(alg_xarray,
                                      area_def,
                                      output_format,
                                      product_name,
                                      output_fnames,
                                      bg_xarray,
                                      bg_product_name)

        curr_metadata = produce_all_sector_metadata(curr_products, area_def, alg_xarray)

        final_products += curr_metadata
        final_products += curr_products

        curr_removed_products, curr_saved_products = remove_duplicates(curr_products+curr_metadata,
                                                                       filename_format,
                                                                       remove_files=True)
        removed_products += curr_removed_products
        saved_products += curr_saved_products

        process_datetimes[area_def.area_id]['end'] = datetime.utcnow()
        num_jobs += 1
    else:
        LOG.info('SKIPPING No coverage or required variables for %s %s', xobjs['METADATA'].source_name, area_def.name)
        #raise ImportError('Failed to find required fields in product algorithm: {0}.{1}'.format(
        #                                                        sect_xarrays[0].source_name,product_name))

    process_datetimes['overall_end'] = datetime.utcnow()
    from geoips2.dev.utils import output_process_times
    output_process_times(process_datetimes, num_jobs)

    retval = 0
    if compare_paths:
        from geoips2.geoips2_utils import find_entry_point
        compare_outputs = find_entry_point('output_comparisons', compare_outputs_module)
        retval = compare_outputs(compare_paths[0].replace('<product>', product_name), final_products)

    from os.path import basename
    LOG.info('The following products were produced from procflow %s', basename(__file__))
    for output_product in final_products:
        LOG.info('    SINGLESOURCESUCCESS %s', output_product)
    LOG.info('Return Value: %s', bin(retval))

    return retval

