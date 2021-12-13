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
from datetime import timedelta

import xarray

from geoips2.dev.product import get_required_variables, get_product_type

PMW_NUM_PIXELS_X = 1400
PMW_NUM_PIXELS_Y = 1400
PMW_PIXEL_SIZE_X = 1000
PMW_PIXEL_SIZE_Y = 1000

LOG = logging.getLogger(__name__)

procflow_type = 'standard'


def add_filename_extra_field(xarray_obj, field_name, field_value):
    if 'filename_extra_fields' not in xarray_obj.attrs:
        xarray_obj.attrs['filename_extra_fields'] = {}
    xarray_obj.attrs['filename_extra_fields'][field_name] = field_value
    return xarray_obj


def combine_filename_extra_fields(source_xarray, dest_xarray):
    if 'filename_extra_fields' in source_xarray.attrs:
        for field in source_xarray.filename_extra_fields:
            if 'filename_extra_fields' not in dest_xarray.attrs:
                dest_xarray.attrs['filename_extra_fields'] = {}
            dest_xarray.attrs['filename_extra_fields'][field] = source_xarray.filename_extra_fields[field]
    return dest_xarray


def process_sectored_data_output(xobjs, variables, product_name, output_format, filename_formats):
    output_products = []
    if get_product_type(product_name, xobjs['METADATA'].source_name) == 'sectored_xarray_dict_to_output_format':
        # xdict = {}
        # dsnum = 0
        # for sect_xarray in xobjs:
        #     xdict[f'DS{dsnum}'] = sect_xarray
        #     dsnum += 1
        # xdict['METADATA'] = xobjs[0][[]]
        output_products += process_xarray_dict_to_output_format(xobjs,
                                                                variables,
                                                                product_name,
                                                                output_format,
                                                                filename_formats)
    return output_products


def process_xarray_dict_to_output_format(xobjs,
                                         variables,
                                         product_name,
                                         output_format,
                                         filename_formats):

    from geoips2.dev.output import get_outputter, get_outputter_type
    from geoips2.dev.filename import get_filenamer, get_filenamer_type

    supported_product_types = ['sectored_xarray_dict_to_output_format', 'unsectored_xarray_dict_to_output_format']
    product_type = get_product_type(product_name, xobjs['METADATA'].source_name)
    if product_type not in supported_product_types:
        raise TypeError(f'UNSUPPORTED product_type {product_type} '
                        f'for product {product_name} source {xobjs["METADATA"].source_name} \n'
                        f'      product_type must be one of {supported_product_types}')

    outputter = get_outputter(output_format)
    fnames = []
    for filename_format in filename_formats:
        filenamer = get_filenamer(filename_format)
        if get_filenamer_type(filename_format) == 'xarray_metadata_to_filename':
            fnames += [filenamer(xobjs['METADATA'])]
        else:
            supported_filenamer_types = ['xarray_metadata_to_filename']
            raise TypeError(f'UNSUPPORTED filename_format "{filename_format}" '
                            f'for product_type "sectored_xarray_dict_to_output_format"\n'
                            f'      filenamer_type: "{get_filenamer_type(filename_format)}"\n'
                            f'      filenamer_type must be one of {supported_filenamer_types}')

    if get_outputter_type(output_format) == 'xarray_dict_data':
        curr_products = outputter(xobjs, variables, fnames)
    else:
        supported_outputter_types = ['xarray_dict_data']
        raise TypeError(f'UNSUPPORTED output_format "{output_format}" '
                        f'for product_type "sectored_xarray_dict_to_output_format"\n'
                        f'      outputter_type: "{get_outputter_type(output_format)}"\n'
                        f'      outputter_type must be one of {supported_outputter_types}')

    return curr_products



def print_area_def(area_def, print_str):
    LOG.info(f'\n\n************************************************************************************'\
             f'\n***{print_str}\n{area_def}')
    for key, value in area_def.sector_info.items():
        print(f'{key}: {value}')
    print(f'************************************************************************************')


def pad_area_definition(area_def, source_name=None):
    from geoips2.sector_utils.utils import is_sector_type
    if is_sector_type(area_def, 'tc'):
        LOG.info('Trying area_def %s, %s final %s',
                 area_def.name, area_def.sector_info['storm_name'], area_def.sector_info['final_storm_name'])
        # Get an extra 50% size for TCs so we can handle recentering and not have missing data.
        # --larger area for possibly moved center for vis/ir backgrounds
        num_lines = int(area_def.y_size * 1.5)
        num_samples = int(area_def.x_size * 1.5)
        # Need full swath width for AMSU-B and MHS. Need a better solution for this.
        if source_name is not None and source_name in ['amsu-b', 'mhs']:
            num_lines = int(area_def.y_size * 1)
            num_samples = int(area_def.x_size * 5)
        from geoips2.interface_modules.area_def_generators.clat_clon_resolution_shape import clat_clon_resolution_shape
        pad_area_def = clat_clon_resolution_shape(area_id=area_def.area_id,
                                                  long_description=area_def.description,
                                                  clat=area_def.sector_info['clat'],
                                                  clon=area_def.sector_info['clon'],
                                                  projection='eqc',
                                                  num_lines=num_lines,
                                                  num_samples=num_samples,
                                                  pixel_width=area_def.pixel_size_x,
                                                  pixel_height=area_def.pixel_size_y)
        from geoips2.sector_utils.utils import copy_sector_info
        pad_area_def = copy_sector_info(area_def, pad_area_def)
    else:
        pad_area_def = area_def
    return pad_area_def


def get_filename(alg_xarray, area_def, filename_format, product_name, **kwargs):

    from geoips2.dev.product import get_covg_from_product, get_covg_args_from_product
    covg_func = get_covg_from_product(product_name, alg_xarray.source_name)
    covg_args = get_covg_args_from_product(product_name, alg_xarray.source_name)
    covg = covg_func(alg_xarray, product_name, area_def, **covg_args)

    from geoips2.dev.filename import get_filenamer, get_filenamer_type
    filename_func = get_filenamer(filename_format)
    if get_filenamer_type(filename_format) == 'data':
        return filename_func(area_def, alg_xarray, [product_name, 'latitude', 'longitude'], covg, **kwargs)
    else:
        return filename_func(area_def, alg_xarray, product_name, covg, **kwargs)


def plot_data(alg_xarray, area_def, output_format, product_name, output_fnames, **kwargs):
    from geoips2.dev.output import get_outputter, get_outputter_type

    if get_outputter_type(output_format) == 'xarray_data':
        output_func = get_outputter(output_format)
        final_products = output_func(xarray_obj=alg_xarray,
                                     product_names=[product_name, 'latitude', 'longitude'],
                                     output_fnames=output_fnames)
    else:
        from geoips2.dev.cmap import get_cmap
        from geoips2.dev.product import get_cmap_name, get_cmap_args
        from geoips2.dev.filename import get_filenamer
        from geoips2.dev.product import get_product_display_name
        cmap_func_name = get_cmap_name(product_name, alg_xarray.source_name)
        mpl_colors_info = None
        if cmap_func_name is not None:
            cmap_func = get_cmap(cmap_func_name)
            cmap_args = get_cmap_args(product_name, alg_xarray.source_name)
            mpl_colors_info = cmap_func(**cmap_args)

        output_func = get_outputter(output_format)
        if get_outputter_type(output_format) == 'image':
            # This returns None if not specified
            final_products = output_func(area_def,
                                         xarray_obj=alg_xarray,
                                         product_name=product_name,
                                         output_fnames=output_fnames,
                                         product_name_title=get_product_display_name(product_name,
                                                                                     alg_xarray.source_name),
                                         mpl_colors_info=mpl_colors_info)
        elif get_outputter_type(output_format) == 'image_overlay':
            # This can include background information, gridlines/boundaries plotting information, etc
            final_products = output_func(area_def,
                                         xarray_obj=alg_xarray,
                                         product_name=product_name,
                                         output_fnames=output_fnames,
                                         product_name_title=get_product_display_name(product_name,
                                                                                     alg_xarray.source_name),
                                         mpl_colors_info=mpl_colors_info,
                                         **kwargs)
    return final_products


def get_area_defs_from_command_line_args(command_line_args, xobjs, variables, filter_time=True):
    from geoips2.sector_utils.utils import get_static_area_defs_for_xarray, get_tc_area_defs_for_xarray
    from geoips2.sector_utils.utils import get_trackfile_area_defs
    from geoips2.sector_utils.utils import filter_area_defs_actual_time
    sectorfiles=None
    sector_list=None
    tcdb_sector_list=None
    tcdb=None
    trackfile_sector_list=None
    trackfiles=None
    trackfile_parser=None
    tc_template_yaml=None
    area_defs = []
    if 'reader_defined_area_def' in command_line_args and command_line_args['reader_defined_area_def'] is not None:
        area_defs += [xobjs['METADATA'].area_definition]
    if 'sectorfiles' in command_line_args:
        sectorfiles = command_line_args['sectorfiles']
    if 'sector_list' in command_line_args:
        sector_list = command_line_args['sector_list']
    if 'tcdb_sector_list' in command_line_args:
        tcdb_sector_list = command_line_args['tcdb_sector_list']
    if 'tcdb' in command_line_args:
        tcdb = command_line_args['tcdb']
    if 'trackfile_sector_list' in command_line_args:
        trackfile_sector_list = command_line_args['trackfile_sector_list']
    if 'trackfiles' in command_line_args:
        trackfiles = command_line_args['trackfiles']
    if 'trackfile_parser' in command_line_args:
        trackfile_parser = command_line_args['trackfile_parser']
    if 'tc_template_yaml' in command_line_args:
        tc_template_yaml = command_line_args['tc_template_yaml']

    if sectorfiles:
        if xobjs is None:
            area_defs += get_static_area_defs_for_xarray(None, sectorfiles, sector_list)
        else:
            area_defs += get_static_area_defs_for_xarray(xobjs['METADATA'], sectorfiles, sector_list)
    if tcdb:
        if xobjs is None:
            raise(TypeError, 'Must have xobjs defined for tcdb sectors')
        area_defs += get_tc_area_defs_for_xarray(xobjs['METADATA'], tcdb_sector_list,
                                                   tc_template_yaml,
                                                   aid_type='BEST',)
    if trackfiles:
        area_defs += get_trackfile_area_defs(trackfiles,
                                             trackfile_parser,
                                             trackfile_sector_list,
                                             tc_template_yaml,
                                             aid_type='BEST',
                                             start_datetime=xobjs['METADATA'].start_datetime - timedelta(hours=8),
                                             end_datetime=xobjs['METADATA'].end_datetime + timedelta(hours=3))

    # If we have a "short" data file, return only a single dynamic sector closest to the start time.
    # If longer than one swath for polar orbiters, we may have more than one "hit", so don't filter.
    if filter_time and xobjs is not None\
       and xobjs['METADATA'].end_datetime - xobjs['METADATA'].start_datetime < timedelta(hours=3):
        area_defs = filter_area_defs_actual_time(area_defs, xobjs['METADATA'].start_datetime)
    LOG.info('Allowed area_defs: %s', [ad.name for ad in area_defs])
    return list(area_defs)


def get_alg_xarray(sect_xarrays, area_def, product_name):

    from geoips2.dev.interp import get_interp
    from geoips2.dev.product import get_interp_name, get_interp_args
    from geoips2.dev.product import get_alg_name, get_alg_args
    from geoips2.dev.alg import get_alg, get_alg_type
    variables = get_required_variables(product_name, sect_xarrays['METADATA'].source_name)   #original input variables from sensor.py (i.e., abi.py)
    alg_func = get_alg(get_alg_name(product_name, sect_xarrays['METADATA'].source_name))
    alg_func_type = get_alg_type(get_alg_name(product_name, sect_xarrays['METADATA'].source_name))
    alg_args = get_alg_args(product_name, sect_xarrays['METADATA'].source_name)
    interp_func_name = get_interp_name(product_name, sect_xarrays['METADATA'].source_name)
    interp_func = None
    if interp_func_name is not None:
        interp_func = get_interp(interp_func_name)
        interp_args = get_interp_args(product_name, sect_xarrays['METADATA'].source_name)

    interp_xarray = None

    for varname in variables:
        for key, sect_xarray in sect_xarrays.items():
            if varname not in sect_xarray.variables:
                continue
            LOG.info('Min/max %s %s / %s',
                     varname,
                     sect_xarray[varname].to_masked_array().min(),
                     sect_xarray[varname].to_masked_array().max())

            # If interp_func is explicitly specified to be None, just return the full
            # variable array, and include the latitude and longitude array as well (since
            # they will map one to one with the variable arrays)
            if interp_func is None:
                if interp_xarray is None:
                    interp_xarray = sect_xarray
                if sect_xarray[varname].shape == interp_xarray[varname].shape:
                    interp_xarray[varname] = sect_xarray[varname]
                else:
                    LOG.info('variable %s incorrect shape %s, expected %s, skipping',
                             varname, sect_xarray[varname].shape, interp_xarray)
                    
            # Otherwise, apply the requested interpolation routine.
            else:
                interp_args['varlist'] = [varname]
                interp_xarray = interp_func(area_def, sect_xarray, interp_xarray, **interp_args)

            LOG.info('Min/max interp %s %s / %s', varname, interp_xarray[varname].min(), interp_xarray[varname].max())

    # Right now, the "standard" algorithm type returns a single array (of any shape).
    # To accommodate wind barbs, I just return a 3d array with 3 layers (speed, direction, rain_flag),
    # and the windbarb plotting routine knows the organization of the resulting "windbarbs" or "wind_ambiguities"
    # variables in order to plot them appropriately.
    # Perhaps windbarbs and wind-ambiguities should be a separate algorithm type, and we should determine
    # how to handle different algorithm types differently (that's the end goal - though perhaps different
    # algorithm types would by necessity have different procflows in general, rather than having a one size
    # fits all procflow...).

    if alg_func_type == 'xarray_to_numpy':
        interp_xarray[product_name] = xarray.DataArray(alg_func(interp_xarray, **alg_args))
    else:
        interp_xarray[product_name] = xarray.DataArray(alg_func([interp_xarray[varname].to_masked_array()
                                                             for varname in variables], **alg_args))  

    # Add appropriate attributes to alg_xarray
    if 'adjustment_id' in area_def.sector_info:
        interp_xarray = add_filename_extra_field(interp_xarray,
                                                 'adjustment_id',
                                                 area_def.sector_info['adjustment_id'])

    return interp_xarray


def verify_area_def(area_defs, check_area_def, data_start_datetime, data_end_datetime, time_range_hours=3):
    from geoips2.sector_utils.utils import filter_area_defs_actual_time
    if data_end_datetime - data_start_datetime < timedelta(hours=time_range_hours):
        new_area_defs = filter_area_defs_actual_time(area_defs, data_start_datetime)
    LOG.info('Allowed area_defs: %s', [ad.name for ad in new_area_defs])
    if check_area_def.name not in [ad.name for ad in new_area_defs]:
        return False
    return True


def single_source(fnames, command_line_args=None):
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

    # These args should always be checked
    check_args = ['sector_list', 'sectorfiles',  # Static sectors,
                  'tcdb', 'tcdb_sector_list',  # TC Database sectors,
                  'trackfiles', 'trackfile_parser', 'trackfile_sector_list',  # Flat text trackfile,
                  'reader_name', 'product_name',
                  'gridlines_params', 'boundaries_params',
                  'output_format', 'filename_format',
                  'adjust_area_def', 'reader_defined_area_def']

    check_command_line_args(check_args, command_line_args)

    product_name = command_line_args['product_name']  # 89HNearest
    filename_format = command_line_args['filename_format']  # tc_fname
    output_format = command_line_args['output_format']  # output_formats.imagery_annotated
    reader_name = command_line_args['reader_name']  # ssmis_binary
    compare_paths = command_line_args['compare_paths']
    compare_outputs_module = command_line_args['compare_outputs_module']
    adjust_area_def = command_line_args['adjust_area_def']

    from geoips2.dev.gridlines import get_gridlines, set_lonlat_spacing
    from geoips2.dev.boundaries import get_boundaries
    gridlines_info = get_gridlines(command_line_args['gridlines_params'])
    boundaries_info = get_boundaries(command_line_args['boundaries_params'])

    from geoips2.stable.reader import get_reader
    from geoips2.dev.output import get_outputter, get_outputter_type
    from geoips2.dev.filename import get_filenamer, get_filenamer_type
    reader = get_reader(reader_name)

    num_jobs = 0
    xobjs = reader(fnames, metadata_only=True)
    from geoips2.xarray_utils.data import sector_xarrays

    variables = get_required_variables(product_name, xobjs['METADATA'].source_name)  #get input variables
    area_defs = get_area_defs_from_command_line_args(command_line_args, xobjs, variables, filter_time=True)

    if get_product_type(product_name, xobjs['METADATA'].source_name) == 'unsectored_xarray_dict_to_output_format':
        xdict = reader(fnames, metadata_only=False)
        final_products += process_xarray_dict_to_output_format(xdict, variables, product_name,
                                                               output_format, [filename_format])
                
    from geoips2.interface_modules.output_formats.utils.metadata import produce_all_sector_metadata
    from geoips2.filenames.duplicate_files import remove_duplicates
    new_attrs = {'filename_extra_fields': {}}
    # setup for TC products
    for area_def in area_defs:

        LOG.info('\n\n\n\nNEXT area definition: %s', area_def)
        pad_area_def = pad_area_definition(area_def, xobjs['METADATA'].source_name)
        try:
            xobjs = reader(fnames, metadata_only=False, chans=variables, area_def=pad_area_def)
        # geostationary satellites fail with IndexError when the area_def does not intersect the
        # data.  Just skip those.  We need a better method for handling this generally, but for
        # now skip IndexErrors.
        except IndexError as resp:
            LOG.error('SKIPPING no coverage for %s', area_def.name)
            continue

        process_datetimes[area_def.area_id] = {}
        process_datetimes[area_def.area_id]['start'] = datetime.utcnow()
        # add SatAzimuth and SunAzimuth into list of the variables for ABI only (come from ABI reader)
        if xobjs['METADATA'].source_name == 'abi':
            if 'SatAzimuth' in list(xobjs.values())[0].keys() and 'SunAzimuth' in list(xobjs.values())[0].keys():
                variables +=['SatAzimuth', 'SunAzimuth']
            else:
                raise ValueError('SatAzimuth and/or SunAzimuth not in ABI data')
        pad_sect_xarrays = sector_xarrays(xobjs, pad_area_def, varlist=variables,
                                          hours_before_sector_time=6, hours_after_sector_time=6, drop=True)

        if len(pad_sect_xarrays.keys()) == 0:
            LOG.info('SKIPPING no sectored xarrays returned for %s', area_def.name)
            continue

        if not verify_area_def(area_defs, pad_area_def,
                               pad_sect_xarrays['METADATA'].start_datetime, pad_sect_xarrays['METADATA'].end_datetime):
            LOG.info('SKIPPING duplicate area_def, out of time range, for %s', area_def.name)
            continue

        curr_output_products = process_sectored_data_output(pad_sect_xarrays, variables, product_name,
                                                            output_format, [filename_format])

        # If we had a request for sectored data processing, skip the rest of the loop
        if curr_output_products:
            final_products += curr_output_products
            continue

        if adjust_area_def:
            from geoips2.geoips2_utils import find_entry_point
            area_def_adjuster = find_entry_point('area_def_adjusters', adjust_area_def)
            # Use normal size sectored xarray when running area_def_adjuster, not padded
            # Center time (mintime + (maxtime - mintime)/2) is very slightly different for different size
            # sectored arrays, so for consistency if we change padding amounts, use the fully sectored
            # array for adjusting the area_def.
            if pad_sect_xarrays['METADATA'].source_name not in ['amsu-b', 'mhs']:
                sect_xarrays = sector_xarrays(pad_sect_xarrays, area_def, varlist=variables,
                                              hours_before_sector_time=6, hours_after_sector_time=6, drop=True)
                area_def = area_def_adjuster(list(sect_xarrays.values()),
                                             area_def,
                                             variables)
            else:
                # AMSU-b specifically needs full swath width...
                area_def = area_def_adjuster(list(pad_sect_xarrays.values()),
                                             area_def,
                                             variables)
            # These will be added to the alg_xarray
            # new_attrs['area_definition'] = area_def
            if 'adjustment_id' in area_def.sector_info:
                new_attrs['filename_extra_fields']['adjustment_id'] = area_def.sector_info['adjustment_id']

        all_vars = []
        for key, xobj in pad_sect_xarrays.items():
            all_vars += list(xobj.variables.keys())
        # If the required variables are not contained within the xarray objects, do not
        # attempt to process (variables in product algorithm are not available)
        if set(variables).issubset(all_vars):

            if get_outputter_type(output_format) == 'xarray_data':
                alg_xarray = get_alg_xarray(pad_sect_xarrays, pad_area_def, product_name)
            else:
                sect_xarrays = sector_xarrays(pad_sect_xarrays, area_def, varlist=variables,
                                              hours_before_sector_time=6, hours_after_sector_time=6, drop=True)
                alg_xarray = get_alg_xarray(sect_xarrays, area_def, product_name)

            from geoips2.dev.product import get_covg_from_product
            covg_func = get_covg_from_product(product_name, alg_xarray.source_name)
            covg = covg_func(alg_xarray, product_name, area_def)

            for attrname in new_attrs:
                LOG.info('ADDING attribute %s %s to alg_xarray', attrname, new_attrs[attrname])
                alg_xarray.attrs[attrname] = new_attrs[attrname]

            output_fnames = []

            # Apply a new coverage scheme (coverage within 300km radical range from TC center)
            # to be done  ????

            minimum_coverage = 10
            if hasattr(alg_xarray, 'minimum_coverage'):
                minimum_coverage = alg_xarray.minimum_coverage
            if covg < minimum_coverage:
                LOG.info('Insufficient coverage %s for data products for %s, SKIPPING', covg, area_def.name)
                continue
 
            output_fnames += [get_filename(alg_xarray, area_def, filename_format, product_name)]
            if gridlines_info is not None:
                gridlines_info = set_lonlat_spacing(gridlines_info, area_def)
                curr_products = plot_data(alg_xarray,
                                      area_def,
                                      output_format,
                                      product_name,
                                      output_fnames,
                                      gridlines_info=gridlines_info,
                                      boundaries_info=boundaries_info)
            else:
                curr_products = plot_data(alg_xarray,
                                      area_def,
                                      output_format,
                                      product_name,
                                      output_fnames)

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
            LOG.info('SKIPPING No coverage or required variables "%s" for %s %s',
                     variables, xobjs['METADATA'].source_name, area_def.name)
            #raise ImportError('Failed to find required fields in product algorithm: {0}.{1}'.format(
            #                                                        sect_xarrays[0].source_name,product_name))

    process_datetimes['overall_end'] = datetime.utcnow()
    from geoips2.dev.utils import output_process_times
    output_process_times(process_datetimes, num_jobs)

    from os.path import basename
    LOG.info('The following products were produced from procflow %s', basename(__file__))
    for output_product in final_products:
        LOG.info('    SINGLESOURCESUCCESS %s', output_product)

    retval = 0
    if compare_paths:
        from geoips2.geoips2_utils import find_entry_point
        compare_outputs = find_entry_point('output_comparisons', compare_outputs_module)
        retval = compare_outputs(compare_paths[0].replace('<product>', product_name).replace('<procflow>', 'single_source'),
                                 final_products)

    return retval

