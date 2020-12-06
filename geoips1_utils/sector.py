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

'''Utilities for converting geoips1 Sector objects to pyresample AreaDefinition objects'''

import logging

from geoips2.sector_utils.utils import SECTOR_INFO_ATTRS

LOG = logging.getLogger(__name__)


def xml_to_yaml(in_xml_fname, out_yaml_fname):
    ''' Convert xml GeoIPS 1 style sectorfile into pyresample style YAML file

    Args:
        in_xml_fname (str) : Input full path to XML file
        out_yaml_fname (str) : Output full path to output YAML file

    Returns:
        (int) : 0 for success, 1 for failure (will not overwrite existing file)
    '''
    from xmltodict import parse

    with open(in_xml_fname) as fobj:
        xmldict = parse(fobj.read())

    if isinstance(xmldict['sector_file']['sector'], list):
        sectors = xmldict['sector_file']['sector']
    else:
        sectors = [xmldict['sector_file']['sector']]

    yamldict = {}
    for sector in sectors:
        yamldict = xml_sector_dict_to_yaml_dict(sector, yamldict)
    import yaml
    from os.path import exists
    if not exists(out_yaml_fname):
        with open(out_yaml_fname, 'w') as fobj:
            yaml.safe_dump(yamldict, fobj)
        retval = 0
    else:
        LOG.warning('%s already exists, NOT OVERWRITING', out_yaml_fname)
        retval = 1
    return retval


def xml_sector_dict_to_yaml_dict(sector, yamldict):
    ''' Set the pyresample style YAML dictionary for the current sector dictionary

    Args:
        sector (dict) : dictionary of GeoIPS 1 style sector information
        sectorname (str) : sectorname of the current YAML entry
        yamldict (dict) : dictionary of pyresample style YAML information

    Returns:
        (dict) : YAML pyresample dictionary
    '''
    from datetime import datetime, timedelta
    from geoips2.sector_utils.yaml_utils import add_dynamic_datetime_to_yamldict
    from geoips2.sector_utils.yaml_utils import add_description_to_yamldict
    sectorname = sector['@name']
    yamldict[sectorname] = {}
    if 'tc_info' in sector.keys():
        sector_start_datetime = datetime.strptime(sector['tc_info']['dtg'],
                                                  '%Y-%m-%d %H:%M:%S')
        sector_end_datetime = sector_start_datetime + timedelta(minutes=359)
        yamldict = add_dynamic_datetime_to_yamldict(yamldict, sectorname, sector_start_datetime, sector_end_datetime)
        yamldict = xml_info_dict_to_yaml_dict(yamldict, sectorname,
                                              sector['tc_info'])
    for sector_type in ['pyrocb', 'atmosriver', 'volcano']:
        if sector_type+'_info' in sector.keys():
            yamldict = xml_dynamic_dt_to_yaml_dict(yamldict, sectorname,
                                                   sector)
            yamldict = xml_info_dict_to_yaml_dict(yamldict, sectorname,
                                                  sector[sector_type+'_info'])
            yamldict = add_description_to_yamldict(yamldict, sectorname,
                                                   sector_type,
                                                   sector_start_datetime)
    # If we haven't found a matching sector type yet, it is static
    if 'sector_type' not in yamldict[sectorname].keys():
        yamldict = xml_info_dict_to_yaml_dict(yamldict, sectorname,
                                              sector['name_info'])
        yamldict = add_description_to_yamldict(yamldict, sectorname,
                                               'static')

    yamldict = xml_area_info_dict_to_yaml_dict(yamldict, sectorname,
                                               sector['area_info'])

    return yamldict


def xml_dynamic_dt_to_yaml_dict(yamldict, sectorname, sector_dict):
    ''' Set the appropriate fields in the yaml dictionary for the dynamic start and end datetime

    Args:
        yamldict (dict) : Dictionary that can be dumped to a pyresample style YAML file
        sectorname (str) : sectorname of the current YAML entry
        sector_dict (dict) : Dictionary of sector information from GeoIPS 1 style xml sectorfile
    Returns:
        (dict) : Dictionary formatted for pyresample style YAML file
    '''
    from datetime import datetime
    sector_start_datetime = datetime.strptime(sector_dict['@dynamic_datetime'], '%Y%m%d.%H%M%S')
    if sector_dict['@dynamic_endtime']:
        sector_end_datetime = datetime.strptime(sector_dict['@dynamic_endtime'], '%Y%m%d.%H%M%S')
    else:
        sector_end_datetime = sector_start_datetime

    from geoips2.sector_utils.yaml_utils import add_dynamic_datetime_to_yamldict
    yamldict = add_dynamic_datetime_to_yamldict(yamldict, sectorname, sector_start_datetime, sector_end_datetime)

    return yamldict


def xml_area_info_dict_to_yaml_dict(yaml_dict, sectorname, area_info_dict):
    ''' Set appropriate fields in the pyresample style YAML dictionary from the xml area_info dict

    Args:
        yaml_dict (dict) : pyresample style YAML dictionary
        sectorname (str) : sectorname of the current YAML entry
        area_info_dict (dict) : GeoIPS 1 xml style area_info dictionary from xml sector

    Returns:
        (dict) : pyresample style YAML dictionary
    '''
    center_lat = float(area_info_dict['center_lat'])
    center_lon = float(area_info_dict['center_lon'])
    from geoips2.sector_utils.projections import get_projection
    center_x = 0
    center_y = 0
    pix_x = int(area_info_dict['num_samples'])
    pix_y = int(area_info_dict['num_lines'])
    pix_width_m = float(area_info_dict['pixel_width'])*1000.0
    pix_height_m = float(area_info_dict['pixel_height'])*1000.0
    yaml_dict['projection'] = {}
    proj = get_projection(area_info_dict['projection'])['p4name']
    from geoips2.sector_utils.yaml_utils import add_projection_to_yamldict
    yaml_dict = add_projection_to_yamldict(yaml_dict, sectorname,
                                           proj,
                                           center_lat, center_lon,
                                           center_x, center_y,
                                           pix_x, pix_y,
                                           pix_width_m, pix_height_m)

    return yaml_dict


def xml_info_dict_to_yaml_dict(yaml_dict, sectorname, info_dict):
    ''' Convert dynamic info dicts from xml sector dictionary into pyresample style YAML dict

    Args:
        yaml_dict (dict) : pyresample style YAML dictionary
        sectorname (str) : sectorname of the current YAML entry
        info_dict (dict) : GeoIPS 1 style dynamic info dict from XML sector entry
                                These are dictionaries named as found in SECTOR_INFO_ATTRS

    Returns:
        (dict) : Pyresample YAML style dictionary
    '''

    yaml_dict[sectorname]['sector_info'] = {}
    for attr in SECTOR_INFO_ATTRS[yaml_dict[sectorname]['sector_type']]:
        if attr in info_dict.keys():
            yaml_dict[sectorname]['sector_info'][attr] = info_dict[attr]
        elif attr == 'synoptic_time':
            yaml_dict[sectorname]['sector_info'][attr] = info_dict['dtg']
        else:
            yaml_dict[sectorname]['sector_info'][attr] = None
    return yaml_dict


def area_def_from_sector(sector):
    ''' Retrun pyresample AreaDefinition from a geoips1 style Sector object
        Parameters:
            sector (Sector): GeoIPS 1.0 Sector object, which has an existing pyresample
                             AreaDefinition object as the area_definition attribute
        Returns:
            AreaDefinition: pyresample AreaDefinition object, with additional attributes:
                            sector_type (str): String id specifying the sector type - sector_info
                                               dictionary will vary based on the sector type.
                                               Currently one of 'static', 'atcf', 'volcano',
                                                                'pyrocb', 'atmosriver'
                            sector_info (dict): Additional info associated with the current
                                                sector type (ie, storm name, volcano height, etc)
                            sector_start_datetime (datetime): If this is a "dynamic" sector (ie,
                                                time dependent), this will be set to the start
                                                time that the sector is valid
                            sector_end_datetime (datetime): If this is a "dynamic" sector,
                                                this specifies the end of the valid time of the
                                                sector - if unknown, match start_datetime.
                            Standard AreaDefinition attributes follow these standards:
                                area_id (str): Short name (equivalent to sector.name)
                                name (str): Python 2 Long name (including sector start_datetime)
                                description (str): Python 3 Long name (same as area_def.name)
                                proj_id (str): proj4 projection name + Short name
    '''

    area_def = sector.area_definition

    if sector.isdynamic:

        # If sector.dynamic_datetime is not specified on Sector object, set to None on area_def
        try:
            area_def.__setattr__('sector_start_datetime', sector.dynamic_datetime)
        except ValueError:
            area_def.__setattr__('sector_start_datetime', None)

        # If sector.dynamic_endtime is not specified on Sector object,
        # set area_def.sector_end_datetime to area_def.sector_start_datetime
        try:
            area_def.__setattr__('sector_end_datetime', sector.dynamic_endtime)
        except ValueError:
            area_def.__setattr__('sector_end_datetime', area_def.sector_start_datetime)

        # Set sector_info and sector_type attributes on area_def
        if sector.tc_info:
            area_def = set_tc_attrs(area_def, sector.tc_info)
        elif sector.pyrocb_info:
            area_def = set_pyrocb_attrs(area_def, sector.pyrocb_info)
        elif sector.atmosriver_info:
            area_def = set_atmosriver_attrs(area_def, sector.atmosriver_info)
        elif sector.volcano_info:
            area_def = set_volcano_attrs(area_def, sector.volcano_info)
    else:
        # If Sector object is not specified as "isdynamic", then it is a static sector.
        area_def.__setattr__('sector_info', sector.name_dict.copy())
        area_def.__setattr__('sector_type', 'static')
        area_def.__setattr__('sector_start_datetime', None)
        area_def.__setattr__('sector_end_datetime', None)

    # Set standard, continent, country, area, subarea, state, city
    for key in sector.name_dict.keys():
        if key not in area_def.sector_info.keys():
            area_def.sector_info[key] = sector.name_dict[key]
    # Python3 compatibility - pyresample AreaDefinition using description rather than name
    # Use area_def.area_id as "short name" (sector.name), and area_def.name / area_def.description
    # as the "long name" (or display-type name)
    area_def.__setattr__('area_id', sector.name)
    area_def.__setattr__('description', '{0} synoptic_time {1}'.format(area_def.name,
                                                                       str(area_def.sector_start_datetime)))
    area_def.__setattr__('name', area_def.description)
    area_def.__setattr__('proj_id', '{0}_{1}'.format(area_def.proj_dict['proj'], area_def.name))

    return area_def


def set_tc_attrs(area_def, info_node):
    ''' Set sector_info dictionary on pyresample AreaDefinition object, based on information
        in GeoIPS 1.0 style XML based SectorInfoNode - specific attributes on the InfoNodde
        based on the sector type

        Parameters:
            area_def (AreaDefinition): pyresample AreaDefinition object, to which sector_info
                                       dictionary attribute must be added
            info_node (TCInfoNode): GeoIPS 1.0 XML based TCInfoNode - pull sector_info dictionary
                                    fields from InfoNode attributes.
        Returns: AreaDefinition
            pyresample AreaDefinition object, with updated attributes:
                sector_info dictionary containing pressure, wind_speed, clat, clon, synoptic_time,
                                                  storm_num, storm_name, storm_basin, storm_year
                sector_type string = 'atcf'
    '''
    info_dict = {}
    sector_type = 'atcf'
    # These attrs are found in sector_utils/utils.py, ensure they match
    # for attr in ['pressure', 'wind_speed', 'clat', 'clon', 'synoptic_time',
    #              'storm_num', 'storm_name', 'storm_basin', 'storm_year']:
    for attr in SECTOR_INFO_ATTRS[sector_type]:
        try:
            info_dict[attr] = getattr(info_node, attr)
        except AttributeError:
            info_dict[attr] = 'unknown'
    area_def.__setattr__('sector_info', info_dict)
    area_def.__setattr__('sector_type', sector_type)
    return area_def


def set_pyrocb_attrs(area_def, info_node):
    ''' Set sector_info dictionary on pyresample AreaDefinition object, based on information
        in GeoIPS 1.0 style XML based InfoNode - specific attributes on the InfoNode
        based on the sector type

        Parameters:
            area_def (AreaDefinition): pyresample AreaDefinition object, to which sector_info
                                       dictionary attribute must be added
            info_node (PyroCbInfoNode): GeoIPS 1.0 XML based PyroCbInfoNode - pull sector_info
                                        dictionary fields from InfoNode attributes.
        Returns: AreaDefinition
            pyresample AreaDefinition object, with updated attributes:
                sector_info dictionary containing min_lat, max_lat, min_lon, max_lon,
                                                  box_resolution_km
                sector_type string = 'pyrocb'
    '''
    info_dict = {}
    sector_type = 'pyrocb'
    # These attrs are found in sector_utils/utils.py, ensure they match
    # for attr in ['min_lat', 'min_lon', 'max_lat', 'max_lon',
    #              'box_resolution_km']:
    for attr in SECTOR_INFO_ATTRS[sector_type]:
        try:
            info_dict[attr] = getattr(info_node, attr)
        except AttributeError:
            info_dict[attr] = 'unknown'
    area_def.__setattr__('sector_info', info_dict)
    area_def.__setattr__('sector_type', sector_type)
    return area_def


def set_volcano_attrs(area_def, info_node):
    ''' Set sector_info dictionary on pyresample AreaDefinition object, based on information
        in GeoIPS 1.0 style XML based InfoNode - specific attributes on the InfoNode
        based on the sector type

        Parameters:
            area_def (AreaDefinition): pyresample AreaDefinition object, to which sector_info
                                       dictionary attribute must be added
            info_node (VolcanoInfoNode): GeoIPS 1.0 XML based VolcanoInfoNode - pull sector_info
                                        dictionary fields from InfoNode attributes.
        Returns: AreaDefinition
            pyresample AreaDefinition object, with updated attributes:
                sector_info dictionary containing summit_elevation, plume_height, wind_speed,
                                                  wind_dir, clat, clon
                sector_type string = 'volcano'
    '''
    info_dict = {}
    sector_type = 'volcano'
    # These attrs are found in sector_utils/utils.py, ensure they match
    # for attr in ['summit_elevation', 'plume_height', 'wind_speed', 'wind_dir',
    #              'clat', 'clon']:
    for attr in SECTOR_INFO_ATTRS[sector_type]:
        try:
            info_dict[attr] = getattr(info_node, attr)
        except AttributeError:
            info_dict[attr] = 'unknown'
    area_def.__setattr__('sector_info', info_dict)
    area_def.__setattr__('sector_type', sector_type)
    return area_def


def set_atmosriver_attrs(area_def, info_node):
    ''' Set sector_info dictionary on pyresample AreaDefinition object, based on information
        in GeoIPS 1.0 style XML based InfoNode - specific attributes on the InfoNode
        based on the sector type

        Parameters:
            area_def (AreaDefinition): pyresample AreaDefinition object, to which sector_info
                                       dictionary attribute must be added
            info_node (AtmosRiverInfoNode): GeoIPS 1.0 XML based InfoNode - pull sector_info
                                        dictionary fields from InfoNode attributes.
        Returns: AreaDefinition
            pyresample AreaDefinition object, with updated attributes:
                sector_info dictionary containing min_lat, max_lat, min_lon, max_lon,
                                                  box_resolution_km
                sector_type string = 'atmosriver'
    '''
    info_dict = {}
    sector_type = 'atmosriver'
    # These attrs are found in sector_utils/utils.py, ensure they match
    # for attr in ['min_lat', 'min_lon', 'max_lat', 'max_lon',
    #              'box_resolution_km']:
    for attr in SECTOR_INFO_ATTRS[sector_type]:
        try:
            info_dict[attr] = getattr(info_node, attr)
        except AttributeError:
            info_dict[attr] = 'unknown'
    area_def.__setattr__('sector_info', info_dict)
    area_def.__setattr__('sector_type', sector_type)
    return area_def
