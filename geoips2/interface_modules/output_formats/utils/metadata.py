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

''' Output metadata related to the current product / sector '''
import logging

from geoips2.sector_utils.tc_tracks import produce_sector_metadata
from geoips2.sector_utils.utils import is_sector_type
from geoips2.dev.utils import replace_geoips_paths
from geoips2.sector_utils.yaml_utils import write_yamldict

LOG = logging.getLogger(__name__)


def produce_all_sector_metadata(final_products, area_def, xarray_obj, metadata_dir='metadata',
                                filename_formats_kwargs=None):
    ''' Produce metadata for all products listed in "final_products" - all products should cover area_def region

    Args:
        final_products (list) : list of strings, containing paths to all products that need metadata files generated.
        area_def (AreaDefinition) : pyresample AreaDefinition that was used to produce all products in final_products
        metadata_dir (str) : DEFAULT 'metadata' Specify subdirectory to use for all metadata - allow for alternate
                                                directory for "non-operational" test products outside the 'metadata'
                                                directory.

    Returns:
        (list) : list of strings, containing full paths to new YAML metadata files
    '''

    yaml_products = []

    kwargs = {}
    if filename_formats_kwargs and 'tc_fname_metadata' in filename_formats_kwargs \
       and 'basedir' in filename_formats_kwargs['tc_fname_metadata']:
        kwargs = {'basedir': filename_formats_kwargs['tc_fname_metadata']['basedir']}

    if is_sector_type(area_def, 'tc'):
        for final_product in final_products:
            if 'yaml' in final_product:
                continue
            curr_metadata_dir = metadata_dir
            if '_dev' not in metadata_dir and '_dev' in final_product:
                curr_metadata_dir = metadata_dir+'_dev'
            yaml_products += produce_sector_metadata(area_def,
                                                     xarray_obj,
                                                     final_product,
                                                     metadata_dir=curr_metadata_dir,
                                                     **kwargs)
    return yaml_products


def output_metadata_yaml(metadata_fname, area_def, xarray_obj, productname=None):
    ''' Write out yaml file "metadata_fname" of sector info found in "area_def"

    Args:
        metadata_fname (str) : Path to output metadata_fname
        area_def (AreaDefinition) : Pyresample AreaDefinition of sector information
        xarray_obj (xarray.Dataset) : xarray Dataset object that was used to produce product
        productname (str) : Full path to full product filename that this YAML file refers to
    Returns:
        (str) : Path to metadata filename if successfully produced.
    '''
    sector_info = area_def.sector_info.copy()

    if hasattr(area_def, 'sector_type') and 'sector_type' not in sector_info:
        sector_info['sector_type'] = area_def.sector_type

    sector_info['bounding_box'] = {}
    sector_info['bounding_box']['minlat'] = area_def.area_extent_ll[1]
    sector_info['bounding_box']['maxlat'] = area_def.area_extent_ll[3]
    sector_info['bounding_box']['minlon'] = area_def.area_extent_ll[0]
    sector_info['bounding_box']['maxlon'] = area_def.area_extent_ll[2]
    sector_info['bounding_box']['pixel_width_m'] = area_def.pixel_size_x
    sector_info['bounding_box']['pixel_height_m'] = area_def.pixel_size_y
    sector_info['bounding_box']['image_width'] = area_def.x_size
    sector_info['bounding_box']['image_height'] = area_def.y_size
    sector_info['bounding_box']['proj4_string'] = area_def.proj4_string

    if productname:
        sector_info['product_filename'] = replace_geoips_paths(productname)

    if 'original_source_filenames' in xarray_obj.attrs.keys():
        sector_info['original_source_filenames'] = xarray_obj.original_source_filenames

    returns = write_yamldict(sector_info, metadata_fname, force=True)
    if returns:
        LOG.info('METADATASUCCESS Writing %s', metadata_fname)
    return returns
