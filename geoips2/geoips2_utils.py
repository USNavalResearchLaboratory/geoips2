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

''' General high level utilities for geoips2 processing '''

import logging
from importlib import metadata

LOG = logging.getLogger(__name__)

NAMESPACE_PREFIX = 'geoips2'

def find_config(subpackage_name, config_basename, txt_suffix='.yaml'):
    ''' Given 'subpackage_name', 'config_basename', and txt_suffix, find matching text file within GEOIPS2 packages

    Args:
        subpackage_name (str) : subdirectory under GEOIPS2 package to look for text file
                                ie text_fname = geoips2/<subpackage_name>/<config_basename><txt_suffix>
        config_basename (str) : text basename to look for,
                                ie text_fname = geoips2/<subpackage_name>/<config_basename><txt_suffix>
        txt_suffix (str) : DEFAULT '.yaml'
                                ie text_fname = geoips2/<subpackage_name>/<config_basename><txt_suffix>

    Returns:
        (str) : Full path to text filename
    '''
    text_fname = None
    from geoips2.filenames.base_paths import PATHS as gpaths
    import os
    for package_name in gpaths['GEOIPS2_PACKAGES']:
        fname = os.path.join(os.getenv('GEOIPS2_PACKAGES_DIR'),
                             package_name,
                             subpackage_name,
                             config_basename+txt_suffix)
        # LOG.info('Trying %s', fname)
        if os.path.exists(fname):
            LOG.info('FOUND %s', fname)
            text_fname = fname
        fname = os.path.join(os.getenv('GEOIPS2_PACKAGES_DIR'),
                             package_name,
                             package_name,
                             subpackage_name,
                             config_basename+txt_suffix)
        # LOG.info('Trying %s', fname)
        if os.path.exists(fname):
            LOG.info('FOUND %s', fname)
            text_fname = fname
    return text_fname


def find_entry_point(namespace, name, default=None):
    '''Find object matching 'name' in using GEOIPS2 entry point namespace 'namespace'.

    Automatically add 'geoips2' prefix to namespace for disambiguation.

    Args:
        namespace (str)    : Entry point namespace (e.g. 'readers')
        name (str)         : Entry point name (e.g. 'amsr2_ncdf')
        default (optional) : Default value if no match is found.  If this is not set (i.e. None),
                             then no match will result in an exception

    '''
    entry_points = metadata.entry_points()
    ep_namespace = '.'.join([NAMESPACE_PREFIX, namespace])
    for ep in entry_points[ep_namespace]:
        if ep.name == name:
            resolved_ep = ep.load()
            break
    else:
        resolved_ep = None
    if resolved_ep is not None:
        return resolved_ep
    else:
        if default is not None:
            return default
        else:
            raise Exception('Failed to find object matching {0} in namespace {1}'.format(name, ep_namespace))


def list_entry_points(namespace):
    '''List names of objects in GEOIPS2 entry point namespace 'namespace'.

    Automatically add 'geoips2' prefix to namespace for disambiguation.

    Args:
        namespace (str)    : Entry point namespace (e.g. 'readers')
    '''
    entry_points = metadata.entry_points()
    ep_namespace = '.'.join([NAMESPACE_PREFIX, namespace])
    return [ep.name for ep in entry_points[ep_namespace]]


def list_product_specs_dict_yamls():
    '''  List all YAML files containing product params in all geoips2 packages

    Returns:
        (list) : List of all product params dict YAMLs in all geoips2 packages

    '''
    from glob import glob
    from geoips2.filenames.base_paths import PATHS as gpaths
    from os.path import basename, splitext
    all_files = []
    for package_name in gpaths['GEOIPS2_PACKAGES']:
       	all_files += glob(gpaths['GEOIPS2_PACKAGES_DIR']+'/'+package_name+'/*/yaml_configs/product_params/*/*.yaml') 
       	all_files += glob(gpaths['GEOIPS2_PACKAGES_DIR']+'/'+package_name+'/yaml_configs/product_params/*/*.yaml') 
       	all_files += glob(gpaths['GEOIPS2_PACKAGES_DIR']+'/'+package_name+'/*/yaml_configs/product_params/*.yaml') 
       	all_files += glob(gpaths['GEOIPS2_PACKAGES_DIR']+'/'+package_name+'/yaml_configs/product_params/*.yaml') 
    return [fname for fname in all_files if '__init__' not in fname]


def list_product_source_dict_yamls():
    '''  List all YAML files containing product source specifications in all geoips2 packages

    Returns:
        (list) : List of all gridlines params dict YAMLs in all geoips2 packages

    '''
    from glob import glob
    from geoips2.filenames.base_paths import PATHS as gpaths
    from os.path import basename, splitext
    all_files = []
    for package_name in gpaths['GEOIPS2_PACKAGES']:
       	all_files += glob(gpaths['GEOIPS2_PACKAGES_DIR']+'/'+package_name+'/*/yaml_configs/product_inputs/*.yaml') 
       	all_files += glob(gpaths['GEOIPS2_PACKAGES_DIR']+'/'+package_name+'/yaml_configs/product_inputs/*.yaml') 
    return [fname for fname in all_files if '__init__' not in fname]


def list_gridlines_params_dict_yamls():
    '''  List all YAML files containing gridlines params in all geoips2 packages

    Returns:
        (list) : List of all gridlines params dict YAMLs in all geoips2 packages

    '''
    from glob import glob
    from geoips2.filenames.base_paths import PATHS as gpaths
    from os.path import basename, splitext
    all_files = []
    for package_name in gpaths['GEOIPS2_PACKAGES']:
       	all_files += glob(gpaths['GEOIPS2_PACKAGES_DIR']+'/'+package_name+'/*/yaml_configs/plotting_params/gridlines/*.yaml') 
       	all_files += glob(gpaths['GEOIPS2_PACKAGES_DIR']+'/'+package_name+'/yaml_configs/plotting_params/gridlines/*.yaml') 
    return [fname for fname in all_files if '__init__' not in fname]


def list_boundaries_params_dict_yamls():
    '''  List all YAML files containing coastline params in all geoips2 packages

    Returns:
        (list) : List of all coastline params dict YAMLs in all geoips2 packages

    '''
    from glob import glob
    from geoips2.filenames.base_paths import PATHS as gpaths
    from os.path import basename, splitext
    all_files = []
    for package_name in gpaths['GEOIPS2_PACKAGES']:
       	all_files += glob(gpaths['GEOIPS2_PACKAGES_DIR']+'/'+package_name+'/*/yaml_configs/plotting_params/boundaries/*.yaml') 
       	all_files += glob(gpaths['GEOIPS2_PACKAGES_DIR']+'/'+package_name+'/yaml_configs/plotting_params/boundaries/*.yaml') 
    return [fname for fname in all_files if '__init__' not in fname]


def copy_standard_metadata(orig_xarray, dest_xarray):
    from geoips2.dev.utils import copy_standard_metadata
    return copy_standard_metadata(orig_xarray, dest_xarray)


def deprecation(message):
    from geoips2.dev.utils import deprecation
    return deprecation(message)


def output_process_times(process_datetimes, num_jobs=None):
    from geoips2.dev.utils import output_process_times
    return output_process_times(process_datetimes, num_jobs=None)
