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

'''Utilities for working with dynamic sector specifications'''

import logging

LOG = logging.getLogger(__name__)

SECTOR_INFO_ATTRS = {'atcf': ['pressure', 'wind_speed', 'clat', 'clon', 'synoptic_time', 'track_type',
                              'storm_num', 'storm_name', 'storm_basin', 'storm_year', 'deck_line', 'source_file',
                              'final_storm_name'],
                     'pyrocb': ['min_lat', 'min_lon', 'max_lat', 'max_lon', 'box_resolution_km'],
                     'volcano': ['summit_elevation', 'plume_height', 'wind_speed', 'wind_dir', 'clat', 'clon'],
                     'atmosriver': ['min_lat', 'min_lon', 'max_lat', 'max_lon', 'box_resolution_km'],
                     'static': ['continent', 'country', 'area', 'subarea', 'state', 'city']}

from geoips2.sector_utils.atcf_tracks import TC_SECTOR_PIXEL_WIDTH_M, TC_SECTOR_PIXEL_HEIGHT_M
from geoips2.sector_utils.atcf_tracks import TC_SECTOR_NUM_LINES, TC_SECTOR_NUM_SAMPLES


def set_text_area_def(xarray_obj, area_def):
    ''' Set the area definition for the text files - raw sectored data, not interpolated

    Args:
        xarray_obj (Dataset) : xarray dataset
        area_def (AreaDefinition) : original area definition

    Returns:
        (AreaDefinition) : pyresample AreaDefinition pertaining to the region for generating text file
    '''
    text_area_def = area_def
    from geoips2.sector_utils.atcf_tracks import set_atcf_area_def
    num_lines = xarray_obj.wind_speed_kts.where(xarray_obj.wind_speed_kts > 0, drop=True).shape[0]
    num_samples = xarray_obj.wind_speed_kts.where(xarray_obj.wind_speed_kts > 0, drop=True).shape[1]
    # Uses default pixel width/height
    text_area_def = set_atcf_area_def(area_def.sector_info,
                                      num_lines=num_lines,
                                      num_samples=num_samples,
                                      pixel_width=None,
                                      pixel_height=None)
    text_area_def.pixel_size_x = 'native'
    text_area_def.pixel_size_y = 'native'

    return text_area_def


def set_mtif_area_def(xarray_obj, area_def):
    ''' Set the area definition for the metoctiff - this should be at native resolution, and on a grid

    Args:
        xarray_obj (Dataset) : xarray dataset
        area_def (AreaDefinition) : original area definition

    Returns:
        (AreaDefinition) : pyresample AreaDefinition pertaining to the region for plotting mtif
    '''
    mtif_area_def = area_def
    if 'sample_pixels_x' in xarray_obj.attrs\
       and 'sample_pixels_y' in xarray_obj.attrs\
       and 'sample_distance_km' in xarray_obj.attrs:
        from geoips2.sector_utils.atcf_tracks import set_atcf_area_def
        LOG.info('Changing area definition for mtifs')
        mtif_clat = get_lat_center(xarray_obj.latitude.to_masked_array())
        mtif_clon = get_lon_center(xarray_obj.longitude.to_masked_array())
        mtif_area_def = set_atcf_area_def(area_def.sector_info,
                                          clat=mtif_clat, clon=mtif_clon,
                                          num_lines=xarray_obj.sample_pixels_y, num_samples=xarray_obj.sample_pixels_x,
                                          pixel_width=xarray_obj.sample_distance_km*1000.0,
                                          pixel_height=xarray_obj.sample_distance_km*1000.0)
        LOG.info('MTIF area definition: %s', mtif_area_def)
    elif 'sample_distance_km' in xarray_obj.attrs:
        try:
            from geoips2.sector_utils.atcf_tracks import set_atcf_area_def
            pixel_width = 1000.0 * xarray_obj.sample_distance_km
            pixel_height = 1000.0 * xarray_obj.sample_distance_km
            mtif_area_def = set_atcf_area_def(area_def.sector_info,
                                              num_lines=int((area_def.pixel_size_y / pixel_height) * area_def.y_size),
                                              num_samples=int((area_def.pixel_size_x / pixel_width) * area_def.x_size),
                                              pixel_width=pixel_width,
                                              pixel_height=pixel_height)
        except TypeError:
            LOG.warning('sample_distance_km not defined on xarray object, not resampling for mtifs')

    return mtif_area_def


def check_center_coverage(xarray_obj, area_def, varlist, covg_varname, width_degrees=8, height_degrees=8, verbose=False,
                          hours_before_sector_time=18, hours_after_sector_time=6):
    ''' Check if there is any data covering the center of the sector '''
    # Do not provide any longitude padding for coverage check sectoring - we want to see if there is any data within
    # the exact center box, not within +- 3 degrees of the center box.
    covg_area_def = set_tc_coverage_check_area_def(area_def, width_degrees=8, height_degrees=8)
    from geoips2.xarray_utils.data import sector_xarray_dataset
    covg_xarray = sector_xarray_dataset(xarray_obj,
                                        covg_area_def,
                                        varlist,
                                        lon_pad=0,
                                        verbose=verbose,
                                        hours_before_sector_time=hours_before_sector_time,
                                        hours_after_sector_time=hours_after_sector_time)

    from geoips2.data_manipulations.info import percent_unmasked
    if covg_xarray is None or percent_unmasked(covg_xarray[covg_varname].to_masked_array()) == 0:
        return False, covg_xarray
    return True, covg_xarray


def set_tc_coverage_check_area_def(area_def, width_degrees=8, height_degrees=8):
    ''' Set the area definition for checking coverage for TC overpasses - take a small box around the center of the
        storm to evaluate coverage, rather than the entire image.

    Args:
        area_def (AreaDefinition) : original area definition

    Returns:
        (AreaDefinition) : pyresample AreaDefinition pertaining to the region for plotting mtif
    '''
    covg_area_def = area_def
    DEG_TO_KM = 111.321
    # Take a 8km x 8km box centered over the storm location for coverage check, 1km pixels
    width_km = DEG_TO_KM * width_degrees
    height_km = DEG_TO_KM * height_degrees
    from geoips2.sector_utils.atcf_tracks import set_atcf_area_def
    LOG.info('Changing area definition for checking TC coverage')
    covg_area_def = set_atcf_area_def(area_def.sector_info,
                                      clat=area_def.sector_info['clat'], clon=area_def.sector_info['clon'],
                                      num_lines=int(height_km), num_samples=int(width_km),
                                      pixel_width=1000.0,
                                      pixel_height=1000.0)
    LOG.info('Coverage area definition: %s', covg_area_def)
    LOG.info('Coverage sector info: %s', covg_area_def.sector_info)

    return covg_area_def


def get_max_lat(lats):
    ''' Get maximum latitude from array of latitudes

    Args:
        lats (ndarray) : numpy MaskedArray of latitudes

    Return:
        (float) : Maximum latitude, between -90 and 90
    '''
    return float(lats.max())


def get_min_lat(lats):
    ''' Get minimum latitude from array of latitudes

    Args:
        lats (ndarray) : numpy MaskedArray of latitudes

    Return:
        (float) : Minimum latitude, between -90 and 90
    '''
    return float(lats.min())


def get_min_lon(lons):
    ''' Get minimum longitude from array of longitudes, handling date line

    Args:
        lons (ndarray) : numpy MaskedArray of longitudes

    Return:
        (float) : Minimum longitude, between -180 and 180
    '''
    if lons.max() > 179.5 and lons.min() < -179.5:
        import numpy
        lons = numpy.ma.where(lons < 0, lons + 360, lons)
    minlon = lons.min()
    if minlon > 180:
        minlon -= 360
    return float(minlon)


def get_max_lon(lons):
    ''' Get maximum longitude from array of longitudes, handling date line

    Args:
        lons (ndarray) : numpy MaskedArray of longitudes

    Return:
        (float) : Maximum longitude, between -180 and 180
    '''
    if lons.max() > 179.5 and lons.max() < -179.5:
        import numpy
        lons = numpy.ma.where(lons < 0, lons + 360, lons)
    maxlon = lons.max()
    if maxlon > 180:
        maxlon -= 360
    return float(maxlon)


def get_lat_center(lats):
    ''' Return the center longitude point from lats array '''
    center_lat = lats.min() + (lats.max() - lats.min()) / 2.0
    return center_lat


def get_lon_center(lons):
    ''' Return the center longitude point from lons array '''

    import numpy
    if lons.max() > 179.5 and lons.min() < -179.5:
        lons = numpy.ma.where(lons < 0, lons + 360, lons)

    center_lon = lons.min() + (lons.max() - lons.min()) / 2.0

    if center_lon > 180:
        center_lon -= 360

    return center_lon


def get_area_defs_for_xarray(xarray_obj,
                             sectorfiles=None, sectorlist=None,
                             pixel_size_x=TC_SECTOR_PIXEL_WIDTH_M,
                             pixel_size_y=TC_SECTOR_PIXEL_HEIGHT_M,
                             num_pixels_x=TC_SECTOR_NUM_SAMPLES,
                             num_pixels_y=TC_SECTOR_NUM_LINES,
                             hours_before_sector_time=18,
                             hours_after_sector_time=6,
                             track_type=None):
    ''' Get all area definitions for the current xarray object, and requested sectors.

    Args:
        xarray_obj (xarray.Dataset) : xarray Dataset to which we are assigning area_defs
        sectorfiles (list) : Default None, optional list of sectorfiles
        sectorlist (list) : Default None, optional list of sector names
        actual_datetime (datetime) : Default None, optional datetime to match for dynamic sectors
        var_for_coverage (str) : Default None, optional variable to sector to check exact time
        hours_before_sector_time (float) : Default 18, hours to look before sector time
        hours_after_sector_time (float) : Default 6, hours to look after sector time
    Returns:
        (list) : List of pyresample AreaDefinition objects
    '''
    area_defs = []
    if sectorfiles and sectorlist:
        area_defs = get_sectors_from_yamls(sectorfiles, sectorlist)
    elif 'area_def' in xarray_obj.attrs.keys() and xarray_obj.area_def is not None:
        area_defs = [xarray_obj.area_def]
    else:
        from datetime import timedelta
        from geoips2.sector_utils.atcf_database import get_all_storms_from_db
        curr_area_defs = get_all_storms_from_db(xarray_obj.start_datetime - timedelta(hours=hours_before_sector_time),
                                                xarray_obj.end_datetime + timedelta(hours=hours_after_sector_time),
                                                pixel_size_x=pixel_size_x, pixel_size_y=pixel_size_y,
                                                num_pixels_x=num_pixels_x, num_pixels_y=num_pixels_y)
        if sectorlist is not None:
            for area_def in curr_area_defs:
                if area_def.area_id in sectorlist:
                    area_defs += [area_def]
                else:
                    LOG.info('area_def %s not in sectorlist %s, not including', area_def.area_id, str(sectorlist))
        else:
            area_defs = curr_area_defs

    # Make sure there are no duplicates
    ret_area_defs = []
    for area_def in area_defs:
        if track_type is not None and 'track_type' in area_def.sector_info and area_def.sector_info['track_type'] != track_type:
            LOG.info('area_def %s track_type %s not requested, not including',
                     area_def.name, area_def.sector_info['track_type'])
        elif area_def.name not in [curr_area_def.name for curr_area_def in ret_area_defs]:
            if 'track_type' in area_def.sector_info:
                LOG.info('Including area_def %s in return list, track type %s',
                         area_def.name, area_def.sector_info['track_type'])
            else:
                LOG.info('Including area_def %s in return list', area_def.name)
            ret_area_defs += [area_def]
        else:
            LOG.info('area_def %s already in return list, not including', area_def.name)
            
    return ret_area_defs


def filter_area_defs_actual_time(area_defs, actual_datetime):
    ret_area_def_ids = {}
    for area_def in area_defs:
        if area_def.area_id not in ret_area_def_ids:
            ret_area_def_ids[area_def.area_id] = area_def
        elif is_dynamic_sector(area_def) and actual_datetime is not None:
            if abs(actual_datetime - area_def.sector_start_datetime)\
             < abs(actual_datetime - ret_area_def_ids[area_def.area_id].sector_start_datetime):
                LOG.info('AREA_DEF LIST REPLACING %s with area_def %s', ret_area_def_ids[area_def.area_id].name, area_def.name)
                ret_area_def_ids[area_def.area_id] = area_def
        else:
            LOG.warning('AREA_DEF LIST REPLACING Multiple identical sectors - using latest %s', area_def.name)
            ret_area_def_ids[area_def.area_id] = area_def

    return ret_area_def_ids.values()


def filter_area_defs_sector(area_defs, xarray_obj, var_for_coverage):
    from geoips2.xarray_utils.data import sector_xarrays
    ret_area_def_ids = {}
    ret_area_def_sects = {}
    for area_def in area_defs:
        if area_def.area_id not in ret_area_def_ids:
            sects = sector_xarrays([xarray_obj],
                                   area_def,
                                   varlist=[var_for_coverage],
                                   verbose=False)
            if not sects:
                LOG.info('AREA_DEF LIST NO COVERAGE not adding sector')
            else:
                LOG.info('AREA_DEF LIST ADDING area_def %s', area_def.name)
                ret_area_def_ids[area_def.area_id] = area_def
                ret_area_def_sects[area_def.area_id] = sects[0]
        elif is_dynamic_sector(area_def):
            old_sect = ret_area_def_sects[area_def.area_id]
            old_area_def = ret_area_def_ids[area_def.area_id]
            sects = sector_xarrays([xarray_obj],
                                   area_def,
                                   varlist=[var_for_coverage],
                                   verbose=False)
            if sects and abs(sects[0].start_datetime - area_def.sector_start_datetime) < abs(old_sect.start_datetime - old_area_def.sector_start_datetime):
            
                LOG.info('AREA_DEF LIST REPLACING %s with area_def %s',
                         ret_area_def_ids[area_def.area_id].name,
                         area_def.name)
                ret_area_def_ids[area_def.area_id] = area_def
                ret_area_def_sects[area_def.area_id] = sects[0]
                # from IPython import embed as shell; shell()
                
        else:
            LOG.warning('AREA_DEF LIST REPLACING Multiple identical sectors - using latest %s', area_def.name)
            ret_area_def_ids[area_def.area_id] = area_def

    return ret_area_def_ids.values()


def get_sectors_from_yamls(sectorfnames, sectornames):
    ''' Get AreaDefinition objects with custom "sector_info" dictionary from YAML area definition

    Args:
        sectorfnames (list) : list of string full paths to YAML area definition files
        sectornames (list) : list of strings of desired sector names to retrieve from YAML files

    Returns:
        (list) : List of pyresample AreaDefinition objects, with arbitrary additional YAML
                    entries added as attributes to each area def (this is to allow specifying
                    "sector_info" metadata dictionary within the YAML file)
    '''
    from pyresample import load_area
    import yaml
    area_defs = []
    for sectorfname in sectorfnames:
        with open(sectorfname) as sectorfobj:
            ydict = yaml.safe_load(sectorfobj)
        for sectorname in sectornames:
            if sectorname in ydict.keys():
                try:
                        area_def = load_area(sectorfname, sectorname)
                except TypeError:
                        area_def = create_areadefinition_from_yaml(sectorfname,sectorname)
                for key in ydict[sectorname].keys():
                    if not hasattr(area_def, key) and key not in ['description', 'projection']:
                        area_def.__setattr__(key, ydict[sectorname][key])
                area_defs += [area_def]
    return area_defs


def create_areadefinition_from_yaml(yamlfile, sector):
    '''Take a YAML with misc metadata and create a pyresample areadefinition
    Misc. metadata will be parsed from the YAML file and manually added to the areadefinition
    Args:
        yamlfile : string full path to YAML area definition file
        sector : string name of sector
    Returns:
        (obj) : pyresample areadefinition object
    '''
    import pyresample
    import yaml
    with open(yamlfile, 'r') as f:
        sectorfile_yaml = yaml.load(f, Loader=yaml.FullLoader)
    sector_info = sectorfile_yaml[sector]
    area_id = sector
    description = sector_info.pop('description')
    projection = sector_info.pop('projection')
    resolution = sector_info.pop('resolution')
    shape = sector_info.pop('shape')
    area_extent = sector_info.pop('area_extent')
    # Create the pyresample area definition
    shape_list = [shape['height'],shape['width']]
    extent_list = []
    extent_list.extend(area_extent['lower_left_xy'])
    extent_list.extend(area_extent['upper_right_xy'])
    area_def = pyresample.create_area_def(area_id=area_id,
                                          description=description,
                                          projection=projection,
                                          resolution=resolution,
                                          shape=shape_list,
                                          area_extent=extent_list)
    # Manually add the metadata to area_def
    for key in sector_info.keys():
        area_def.__setattr__(key, sector_info[key])
    return area_def


def is_sector_type(area_def, sector_type_str):
    '''Determine if the type of area_def sector is as specified in passed sector_type_str.
       Parameters:
           area_def (AreaDefinition): pyresample AreaDefinition object specifying region of interest
           sector_type_str (str) String specifying the type of sector, must match 'sector_type'
                                 attribute on AreaDefinition object
                                 currently one of 'tc', 'pyrocb', 'volcano', 'atmosriver' 'static'
       Returns:
           bool, True if area_def.sector_type == 'sector_type', False otherwise
    '''
    if not area_def:
        LOG.info('area_def not defined, not of type %s', sector_type_str)
        return False
    if not hasattr(area_def, 'sector_type'):
        LOG.info('area_def.sector_type not defined, not of type %s', sector_type_str)
        return False

    if area_def.sector_type == sector_type_str:
        # Need to decide if this is necessary.
        # for attr in SECTOR_INFO_ATTRS[sector_type_str]:
        #     if attr not in area_def.sector_info.keys():
        #         LOG.warning('attr %s not in area_def.sector_info.keys(), not of type %s', attr, sector_type_str)
        #         return False
        return True
    return False


def is_dynamic_sector(area_def):
    '''Determine if the AreaDefinition object is a dynamic region of interest
       Parameters:
           area_def (AreaDefinition): pyresample AreaDefinition object specifying region of interest
       Returns:
           bool, True if area_def.sector_start_datetime exists and is not None, False otherwise
    '''
    if not area_def:
        return False
    if not hasattr(area_def, 'sector_start_datetime'):
        return False
    if not area_def.sector_start_datetime:
        return False
    if area_def.sector_start_datetime is not None:
        return True
    return False
