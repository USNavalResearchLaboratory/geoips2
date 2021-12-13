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

from geoips2.interface_modules.procflows.single_source import process_sectored_data_output
from geoips2.interface_modules.procflows.single_source import process_xarray_dict_to_output_format
from geoips2.geoips2_utils import find_entry_point

PMW_NUM_PIXELS_X = 1400
PMW_NUM_PIXELS_Y = 1400
PMW_PIXEL_SIZE_X = 1000
PMW_PIXEL_SIZE_Y = 1000

LOG = logging.getLogger(__name__)

procflow_type = 'standard'


def get_sectored_read(config_dict, area_defs, area_def_id, sector_type, reader, fnames, variables):
    ''' Return dictionary of xarray datasets for a given area def'''

    area_def = area_defs[area_def_id][sector_type]['area_def']

    from geoips2.interface_modules.procflows.single_source import pad_area_definition
    if 'primary_sector' in config_dict:
        primary_sector_type = area_defs[area_def_id][config_dict['primary_sector']]
        pad_area_def = primary_sector_type['area_def']
    else:
        pad_area_def = pad_area_definition(area_def)
    try:
        xobjs = reader(fnames,
                       metadata_only=False,
                       chans=variables,
                       area_def=pad_area_def)
    # geostationary satellites fail with IndexError when the area_def does not intersect the
    # data.  Just skip those.  We need a better method for handling this generally, but for
    # now skip IndexErrors.
    except IndexError as resp:
        LOG.error('%s SKIPPING no coverage for %s', resp, area_def)
        return {}
    return xobjs


def get_area_def_list_from_dict(area_defs):
    ''' Get a list of actual area_defs from the full dictionary returned from get_area_defs_from_available_sectors'''
    list_area_defs = []
    for area_def_id in area_defs:
        for sector_type in area_defs[area_def_id]:
            for ad in area_defs[area_def_id][sector_type]:
                list_area_defs += [area_defs[area_def_id][sector_type]['area_def']]
    return list_area_defs


def set_comparison_path(output_dict, product_name, output_type):
    ''' Replace variables specified by <varname> within the config-specified compare_path
        with appropriate variable names.

    Args:
        config (dict) : Dictionary of output specifications, containing key "compare_path"
        product_name (str) : Current requested product name, all instances of
                                <product> in compare_path replaced with product_name argument
        output_type (str) : Current requested output type, all instances of
                                <output> in compare_path replaced with output argument
    Returns:
        (str) : Return a single string with the fully specified comparison path for current product'''

    # If this config has a compare_path specified, replace variables appropriately
    if 'compare_path' in output_dict:
        if 'compare_outputs_module' in output_dict:
            compare_outputs_module = output_dict['compare_outputs_module']
        else:
            compare_outputs_module = 'compare_outputs'

        cpath = output_dict['compare_path'].replace('<product>',
                                                    product_name).replace('<procflow>',
                                                                          'config_based').replace('<output>',
                                                                                                  output_type)
    # If there is no comparison specified, identify as "no_comparison"
    else:

        cpath = 'no_comparison'
        compare_outputs_module = 'no_compare_outputs_module'

    return cpath, compare_outputs_module


def initialize_final_products(final_products, cpath, cmodule):
    ''' Initialize the final_products dictionary with cpath dictionary key if needed.

    Args:
        final_products (dict) : Dictionary of final products, with keys of final required "compare_paths"
                                    Products with no compare_path specified are stored with the key "no_comparison"
        cpath (str) : Key to add to final_products dictionary
    Returns:
        (dict) : Return final_products dictionary, updated with current "cpath" key:
                    final_products[cpath]['files'] = <list_of_files_in_given_cpath>'''

    if cpath not in final_products:
        final_products[cpath] = {}
        # This is where we store all the files
        final_products[cpath]['files'] = []
        final_products[cpath]['compare_outputs_module'] = cmodule

    return final_products


def process_unsectored_data_outputs(final_products, available_outputs_dict, available_sectors_dict, xobjs, variables):
    ''' Loop through all possible outputs, identifying output types that require unsectored data output.
        Produce all required unsectored data output, update final_products dictionary accordingly, and
        return final_products dictionary with the new unsectored outputs.

    Args:
        final_products (dict) : Dictionary of final products, with keys of final required "compare_paths"
                                    Products with no compare_path specified are stored with the key "no_comparison"
        available_outputs_dict (dict) : Dictionary of all available output product specifications
        available_sectors_dict (dict) : Dictionary of available sector types - we are looking for available sectors
                                        that contain the "unsectored" keyword.
        xobjs (dict) : Dictionary of xarray datasets, for use in producing unsectored output formats
        variables (list) : List of strings of required variables in the given product.

    Returns:
        (dict) : Return final_products dictionary, updated with current "cpath" key:
                    final_products[cpath]['files'] = <list_of_files_in_given_cpath>'''

    # These are the different sectors, one for each method of reprojecting or sectoring or resampling the data
    for sector_type in available_sectors_dict:
        # We are looking for a sector_type that has the keyword "unsectored" meaning we want to process the dat
        # before doing anything else to it
        if 'unsectored' in available_sectors_dict[sector_type] and available_sectors_dict[sector_type]['unsectored']:
            # Once we've found an "unsectored" data type, we will look for all the output_types
            # in "available_outputs_dict" that use that sector_type
            for output_type in available_outputs_dict:
                output_dict = available_outputs_dict[output_type]
                if output_dict['requested_sector_type'] == sector_type:
                    # Now we will produce all of the individual products for the given output_type/sector_type
                    for product_name in output_dict['product_names']:
                        # This grabs the compare_path that was requested in the YAML config, and replaces
                        # all instances of <product> with product_name and
                        # all instances of <output> with output_type
                        cpath, cmodule = set_comparison_path(output_dict, product_name, output_type)
                        # This adds "cpath" to the final_products dictionary, if necessary
                        final_products = initialize_final_products(final_products, cpath, cmodule)
                        final_products[cpath]['compare_outputs_module'] = cmodule
                        # This actually produces all the required output files for the current product
                        out = process_xarray_dict_to_output_format(xobjs,
                                                                   variables,
                                                                   product_name,
                                                                   output_dict['output_format'],
                                                                   output_dict['filename_formats'])
                        # Add them to the final_products dictionary - comparisons happen at the end.
                        final_products[cpath]['files'] += out
    return final_products


def requires_bg(available_outputs_dict, sector_type):
    ''' Check if a given sector_type is requested for any product_types that also require background imagery.

    Args:
        available_outputs_dict (dict) : Dictionary of all requested output_types (specified in YAML config)
        sector_type (str) : sector_type to determine if any output_types that require background imagery also
                                request the passed sector_type
    Returns:
        (bool) : True if any output_types that require background imagery require the passed "sector_type"
                 False if no output_types require both background imagery and the passed "sector_type"
    '''
    # Check each output_type in the full config_dict
    for output_type in available_outputs_dict:
        # If the current output_type has an entry for "background_products" that means it requires background imagery
        # If the current output_type also requested the passed "sector_type", then return True.
        if 'background_products' in available_outputs_dict[output_type] \
           and available_outputs_dict[output_type]['requested_sector_type'] == sector_type:
            return True
    # If no output_types required both background_products and the passed "sector_type" then return False
    return False


def is_required_sector_type(available_outputs_dict, sector_type):
    ''' Check if a given sector_type is required for any currently requested output_types 

    Args:
        available_outputs_dict (dict) : Dictionary of all requested output_types (specified in YAML config)
        sector_type (str) : Determine if any output_types require the currently requested "sector_type"

    Returns:
        (bool) : True if any output_types require the passed "sector_type"
                 False if no output_types require the passed "sector_type"
    '''
    # Go through each output_type currently requested in the YAML config file
    for output_type in available_outputs_dict.keys():
        # If the passed sector_type is requested for any output_type in the YAML config, return True
        if sector_type == available_outputs_dict[output_type]['requested_sector_type']:
            return True
    # If the passed sector_type is not needed in the YAML config, return False
    return False


def get_config_dict(config_yaml_file):
    ''' Populate the full config dictionary (sector and output specifications) from a given YAML config file

    Args:
        config_yaml_file (str) : Full path to YAML config file, containing sector and output specifications.
                                    YAML config files support environment variables in entries flagged with !ENV

    Returns:
        (dict) : Return dictionary of both sector and output specifications, as found in config_yaml_file
                    The output dictionary references the "sector_types" found in the available_sectors dictionary,
                    each output_type requests a specific "sector_type" to be used for processing.
    '''
    # import yaml
    # with open(config_yaml_file, 'r') as f:
    #     config_dict = yaml.safe_load(f)
    # return config_dict
    # This allows environment variables specified by !ENV ${ENVVARNAME}
    from pyaml_env import parse_config
    return parse_config(config_yaml_file)


def get_variables_from_available_outputs_dict(available_outputs_dict, source_name, sector_types=None):
    ''' Get required variables for all outputs for a given "source_name" specified within the YAML config

    Args:
        available_outputs_dict (dict) : Dictionary of all requested output_types (specified in YAML config)
        source_name (str) : Find all required variables for the passed "source_name"
        sector_types (list) : DEFAULT None, if sector_types list of strings is passed, only include
                                output_types that require one of the passed "sector_types"

    Returns:
        (list) : List of all required variables for all output products for the given source_name
    '''
    from geoips2.dev.product import get_required_variables

    variables = []
    # Loop through all possible output types
    for output_type in available_outputs_dict:
        # If we requested specific sector_types, only include output_types that require that sector_type
        if sector_types is None or available_outputs_dict[output_type]['requested_sector_type'] in sector_types:
            # Loop through all products for the given output_type
            for product_name in available_outputs_dict[output_type]['product_names']:
                # Add all required variables for the current product and source to the list
                variables += get_required_variables(product_name, source_name)
    # Return list of all required variables
    return list(set(variables))


def get_area_defs_from_available_sectors(available_sectors_dict, command_line_args, xobjs, variables):
    ''' Get all required area_defs for the given set of YAML config parameters (config_dict), command_line_args,
        xobjs, and required variables. Command line args override config specifications

    Args:
        available_sectors_dict (dict) : Dictionary of all requested sector_types (specified in YAML config)
        command_line_args (dict) : Dictionary of command line arguments - any command line argument that is also
                                    a key in available_sectors_dict[<sector_type>] will replace the value in
                                    the available_sectors_dict[<sector_type>]
        xobjs (dict) : Dictionary of xarray datasets, used in determining start/end time of data files for identifying
                        dynamic sectors
        variables (list) : List of required variables, for determining center coverage for TCs

    Returns:
        (dict) : Dictionary of required area_defs, with area_def.name as the dictionary keys.
                    Based on YAML config-specified available_sectors, and command line args

                    Each area_def.name key has one or more "sector_types" associated with it.

                    Each sector_type dictionary contains the actual "requested_sector_dict" from the YAML config,
                    and the actual AreaDefinition object that was returned.

                        area_defs[area_def.name][sector_type]['requested_sector_dict']
                        area_defs[area_def.name][sector_type]['area_def']
    '''

    area_defs = {}
    from geoips2.interface_modules.procflows.single_source import get_area_defs_from_command_line_args
    # Loop through all available sector types
    for sector_type in available_sectors_dict:
        sector_dict = available_sectors_dict[sector_type].copy()

        # If the current sector_type is "unsectored" skip it, because it has no associated sector information
        if 'unsectored' in sector_dict and sector_dict['unsectored']:
            continue

        # command_line_args take priority over config args - if someone passes something in
        # explicitly, it will be used rather than config "default"
        for argname in command_line_args.keys():
            if command_line_args[argname]:
                sector_dict[argname] = command_line_args[argname]

        # Double check if tcdb should be set to false
        if sector_dict.get('trackfiles'):
            sector_dict['tcdb'] = False

        # This is the standard "get_area_defs_from_command_line_args", YAML config specified sector information
        # matches the command line specified sector information
        curr_area_defs = get_area_defs_from_command_line_args(sector_dict,
                                                              xobjs,
                                                              variables,
                                                              filter_time=True)

        # Loop through the list of area_defs returned by get_area_defs_from_command_line_args,
        # we are going to organize them
        for area_def in curr_area_defs:
            # Use description or name so it includes synoptic time
            # We want each sectorname as a key in the dictionary, with one or more sector_types attached to it.
            # Ie, we may have different sizes/resolutions for the same region, so we want a dictionary of sector_types
            # within the dictionary of area_defs
            if area_def.name not in area_defs:
                # Store the actual sector_dict and area_def in the dictionary
                area_defs[area_def.name] = {sector_type: {'requested_sector_dict': sector_dict,
                                                          'area_def': area_def}}
            else:
                area_defs[area_def.name][sector_type] = {'requested_sector_dict': sector_dict,
                                                         'area_def': area_def}
    return area_defs


def config_based(fnames, command_line_args=None):
    ''' Workflow for efficiently running all required outputs (sectors and products) for a given set of data types,
        specified via a YAML config file

    Args:
        fnames (list) : List of strings specifying full paths to input file names to process
        command_line_args (dict) : dictionary of command line arguments
                                     'output_config': Explicitly request full path to YAML config file
    Returns:
        (int) : 0 for successful completion, non-zero for error (incorrect comparison, or failed run)
    '''
    from datetime import datetime
    process_datetimes = {}
    process_datetimes['overall_start'] = datetime.utcnow()
    final_products = {}
    removed_products = []
    saved_products = []
    num_jobs = 0

    from geoips2.commandline.args import check_command_line_args

    # These args should always be checked
    check_args = ['output_config', 'fuse_files', 'fuse_reader']

    check_command_line_args(check_args, command_line_args)
    config_dict = get_config_dict(command_line_args['output_config'])

    from geoips2.stable.reader import get_reader
    from glob import glob
    from geoips2.dev.product import get_required_variables

    if not fnames and 'filenames' in config_dict:
        fnames = glob(config_dict['filenames'])

    bg_files = None

    if 'fuse_files' in command_line_args and command_line_args['fuse_files'] is not None:
        bg_files = command_line_args['fuse_files'][0]
    elif 'fuse_files' in config_dict:
        bg_files = glob(config_dict['fuse_files'])

    if 'fuse_reader' in command_line_args and command_line_args['fuse_reader'] is not None:
        bg_reader = get_reader(command_line_args['fuse_reader'][0])
    elif 'fuse_reader' in config_dict:
        bg_reader = get_reader(config_dict['fuse_reader'])

    if 'fuse_product' in command_line_args and command_line_args['fuse_product'] is not None:
        bg_product_name = command_line_args['fuse_product'][0]
    elif 'fuse_product' in config_dict:
        bg_product_name = config_dict['fuse_product']

    if bg_files is not None:
        bg_xobjs = bg_reader(bg_files, metadata_only=True)
        bg_variables = get_required_variables(bg_product_name, bg_xobjs['METADATA'].source_name)

    reader = get_reader(config_dict['reader_name'])
    xobjs = reader(fnames, metadata_only=True)
    source_name = xobjs['METADATA'].source_name

    variables = get_variables_from_available_outputs_dict(config_dict['outputs'], source_name)
    # command_line_args take priority over config args - if someone passes something in
    # explicitly, it will be used rather than config "default"
    area_defs = get_area_defs_from_available_sectors(config_dict['available_sectors'],
                                                     command_line_args,
                                                     xobjs,
                                                     variables)

    # If this config does not perform a sectored read, just read all the data now
    # Otherwise data will be read within the area_def loop
    sectored_read = False
    if 'sectored_read' in config_dict and config_dict['sectored_read']:
        sectored_read = True

    if not sectored_read:
        xobjs = reader(fnames, metadata_only=False, chans=variables)

    # Check if we have any required unsectored outputs, if so produce here, then continue
    final_products = process_unsectored_data_outputs(final_products,
                                                     config_dict['outputs'],
                                                     config_dict['available_sectors'],
                                                     xobjs,
                                                     variables)

    from geoips2.xarray_utils.data import sector_xarrays
    from geoips2.interface_modules.output_formats.utils.metadata import produce_all_sector_metadata
    from geoips2.filenames.duplicate_files import remove_duplicates
    from geoips2.interface_modules.procflows.single_source import pad_area_definition, get_filename
    from geoips2.interface_modules.procflows.overlay import plot_data
    from geoips2.interface_modules.procflows.single_source import get_alg_xarray
    from geoips2.interface_modules.procflows.single_source import verify_area_def

    list_area_defs = get_area_def_list_from_dict(area_defs)

    # Loop through each template - register the data once for each template/area_def
    for area_def_id in area_defs:

        LOG.info('\n\n\n\nNEXT area def id: %s', area_def_id)

        bg_alg_xarrays = {}
        # Loop through each sector_type - each sector_type is a different projection / shape / resolution,
        # so we only want to reproject once for each sector_type
        for sector_type in area_defs[area_def_id]:

            # If we read separately for each sector (geostationary), then must set xobjs within area_def loop
            if sectored_read:
                xobjs = get_sectored_read(config_dict, area_defs, area_def_id, sector_type, reader, fnames, variables)
                if not xobjs:
                    continue
            area_def = area_defs[area_def_id][sector_type]['area_def']
            # Padded region to ensure we have enough data for recentering, etc.
            pad_area_def = pad_area_definition(area_def, xobjs['METADATA'].source_name)
            # See if this sector_type is used at all for product output, if not, skip it.
            if not is_required_sector_type(config_dict['outputs'], sector_type):
                LOG.info('\n\n\nSKIPPING sector type: %s, not required for outputs %s',
                         sector_type,
                         config_dict['outputs'].keys())
                continue
            requested_sector_dict = area_defs[area_def_id][sector_type]['requested_sector_dict']

            LOG.info('\n\n\n\nNEXT area definition: %s', area_def)

            LOG.info('\n\nNEXT sector type: %s, requested: %s\n\n',
                     sector_type, requested_sector_dict)

            curr_variables = get_variables_from_available_outputs_dict(config_dict['outputs'],
                                                                       source_name,
                                                                       sector_types=[sector_type])

            # Reduce hours before and after sector time, so we don't get both overpasses from
            # a single. Sector to pad_area_def so we have enough data for recentering.
            process_datetimes[area_def.area_id] = {}
            process_datetimes[area_def.area_id]['start'] = datetime.utcnow()
            # Make sure we grab some around the required data.
            pad_sect_xarrays = sector_xarrays(xobjs, pad_area_def, varlist=curr_variables,
                                              hours_before_sector_time=6, hours_after_sector_time=6, drop=True)

            # If we didn't get any data, continue to the next sector_type
            if len(pad_sect_xarrays) == 0:
                LOG.info('SKIPPING no sectored xarrays returned for %s', area_def.name)
                continue

            # Now we check to see if the current area_def is the closest one to the dynamic time, if appropriate.
            # We could end up with multiple area_defs for a single dynamic sector, and we can't truly test to see
            # how close each one is to the actual data until we sector it... So, check now to see if any of the
            # area_defs in list_area_defs is closer than pad_area_def
            if not verify_area_def(list_area_defs, pad_area_def,
                                   pad_sect_xarrays['METADATA'].start_datetime,
                                   pad_sect_xarrays['METADATA'].end_datetime):
                LOG.info('SKIPPING duplicate area_def, out of time range, for %s', area_def.name)
                continue

            # Check the config dict to see if this sector_type requests background products
            if bg_files and requires_bg(config_dict['outputs'], sector_type):
                # If we haven't created the bg_alg_xarray for the current sector_type yet, process it and add to the
                # dictionary
                if sector_type not in bg_alg_xarrays:
                    bg_xobjs = bg_reader(bg_files, metadata_only=False,
                                         chans=bg_variables, area_def=pad_area_def)
                    bg_pad_sect_xarrays = sector_xarrays(bg_xobjs,
                                                         pad_area_def,
                                                         varlist=bg_variables,
                                                         hours_before_sector_time=6,
                                                         hours_after_sector_time=6,
                                                         drop=True)
                    from geoips2.interface_modules.procflows.overlay import get_bg_xarray
                    bg_alg_xarrays[sector_type] = get_bg_xarray(bg_pad_sect_xarrays, area_def, bg_product_name)

            # Must adjust the area definition AFTER sectoring xarray (to get valid start/end time
            adjust_area_def = None
            if 'adjust_area_def' in config_dict['available_sectors'][sector_type]:
                adjust_area_def = config_dict['available_sectors'][sector_type]['adjust_area_def'] 
            if adjust_area_def:
                area_def_adjuster = find_entry_point('area_def_adjusters', adjust_area_def)
                # Use normal size sectored xarray when running area_def_adjuster, not padded
                # Center time (mintime + (maxtime - mintime)/2) is very slightly different for different size
                # sectored arrays, so for consistency if we change padding amounts, use the fully sectored
                # array for adjusting the area_def.
                sect_xarrays = sector_xarrays(pad_sect_xarrays, area_def, varlist=variables,
                                              hours_before_sector_time=6, hours_after_sector_time=6, drop=True)
                area_def = area_def_adjuster(list(sect_xarrays.values()),
                                             area_def,
                                             variables,
                                             config_dict['available_sectors'][sector_type]['adjust_variables'])

            # Keep track of the applied algorithms in order to prevent redundant algorithm application
            pad_alg_xarrays = {}
            alg_xarrays = {}
            from geoips2.dev.output import get_outputter, get_outputter_type
            for output_type, output_dict in config_dict['outputs'].items():

                # If the current output type does not require the current sector_type, skip
                if output_dict['requested_sector_type'] != sector_type:
                    continue

                LOG.info('\n\n\n\nNEXT output_type: %s, area_def.name: %s, sector_type: %s',
                         output_type, area_def.name, sector_type)

                for product_name in output_dict['product_names']:
                    cpath, cmodule = set_comparison_path(output_dict, product_name, output_type)
                    final_products = initialize_final_products(final_products, cpath, cmodule)
                    final_products[cpath]['compare_outputs_module'] = cmodule

                    output_format = output_dict['output_format']
                    filename_formats = output_dict['filename_formats']

                    # Produce sectored data output
                    curr_output_products = process_sectored_data_output(pad_sect_xarrays, curr_variables, product_name,
                                                                        output_format, filename_formats)
                    # If the current product required sectored data processing, skip the rest of the loop
                    if curr_output_products:
                        final_products[cpath]['files'] += curr_output_products
                        continue

                    if get_outputter_type(output_format) == 'xarray_data':
                        # If we're saving out intermediate data file, write out pad_area_def.
                        if product_name not in alg_xarrays:
                            pad_alg_xarrays[product_name] = get_alg_xarray(pad_sect_xarrays, pad_area_def, product_name)
                        alg_xarray = pad_alg_xarrays[product_name]
                    else:
                        # If we're writing out an image, cut it down to the desired size.
                        if product_name not in alg_xarrays:
                            sect_xarrays = sector_xarrays(pad_sect_xarrays, area_def, varlist=curr_variables,
                                                          hours_before_sector_time=6, hours_after_sector_time=6,
                                                          drop=True)
                            alg_xarrays[product_name] = get_alg_xarray(sect_xarrays, area_def, product_name)
                        alg_xarray = alg_xarrays[product_name]

                    from geoips2.dev.product import get_covg_from_product
                    covg_func = get_covg_from_product(product_name, alg_xarray.source_name)
                    covg = covg_func(alg_xarray, product_name, area_def)

                    minimum_coverage = 10
                    if hasattr(alg_xarray, 'minimum_coverage'):
                        minimum_coverage = alg_xarray.minimum_coverage
                    if covg < minimum_coverage:
                        LOG.info('Insufficient coverage %s for data products, SKIPPING', covg)
                        continue
 
                    kwargs = {}

                    if 'gridlines_params' in output_dict and output_dict['gridlines_params'] is not None:
                        from geoips2.dev.gridlines import get_gridlines, set_lonlat_spacing
                        gridlines_info = get_gridlines(output_dict['gridlines_params'])
                        gridlines_info = set_lonlat_spacing(gridlines_info, area_def)
                        kwargs['gridlines_info'] = gridlines_info

                    if 'boundaries_params' in output_dict and output_dict['boundaries_params'] is not None:
                        from geoips2.dev.boundaries import get_boundaries
                        boundaries_info = get_boundaries(output_dict['boundaries_params'])
                        kwargs['boundaries_info'] = boundaries_info

                    if bg_files and 'background_products' in output_dict and sector_type in bg_alg_xarrays:
                        kwargs['bg_xarray'] = bg_alg_xarrays[sector_type]
                        kwargs['bg_product_name'] = bg_product_name

                        from geoips2.interface_modules.procflows.single_source import combine_filename_extra_fields
                        alg_xarray = combine_filename_extra_fields(bg_alg_xarrays[sector_type], alg_xarray)

                    output_fnames = []
                    for filename_format in filename_formats:
                        output_fnames += [get_filename(alg_xarray, area_def, filename_format, product_name)]

                    curr_products = plot_data(alg_xarray,
                                              area_def,
                                              output_format,
                                              product_name,
                                              output_fnames,
                                              **kwargs)

                    curr_metadata = produce_all_sector_metadata(curr_products, area_def, alg_xarray)
                    final_products[cpath]['files'] += curr_metadata
                    final_products[cpath]['files'] += curr_products

                    for filename_format in filename_formats:
                        if 'remove_duplicates' in output_dict and output_dict['remove_duplicates'] is not None:
                            curr_removed_products, curr_saved_products = remove_duplicates(curr_products+curr_metadata,
                                                                                           filename_format,
                                                                                           remove_files=True)
                            removed_products += curr_removed_products
                            saved_products += curr_saved_products

                    process_datetimes[area_def.area_id]['end'] = datetime.utcnow()
                    num_jobs += 1

    process_datetimes['overall_end'] = datetime.utcnow()
    from geoips2.dev.utils import output_process_times
    output_process_times(process_datetimes, num_jobs)

    retval = 0
    failed_compares = {}
    for cpath in final_products:
        if cpath != 'no_comparison':
            curr_compare_outputs = find_entry_point('output_comparisons',
                                                    final_products[cpath]['compare_outputs_module'])
            curr_retval = curr_compare_outputs(cpath, final_products[cpath]['files'])
            retval += curr_retval
            if curr_retval != 0:
                failed_compares[cpath] = curr_retval
        else:
            LOG.info('No comparison specified, not attempting to compare outputs')

    from os.path import basename
    LOG.info('The following products were produced from procflow %s', basename(__file__))
    for cpath in final_products:
        if cpath in failed_compares:
            LOG.info('%s FAILED COMPARISONS IN DIR: %s\n', failed_compares[cpath], cpath)
        elif cpath != 'no_comparison':
          LOG.info('SUCCESSFUL COMPARISON DIR: %s\n', cpath)
        for filename in final_products[cpath]['files']:
            LOG.info('    CONFIGSUCCESS %s', filename)
        LOG.info('\n')

    return retval

