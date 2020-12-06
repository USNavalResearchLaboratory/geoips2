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

'''Modules to access ATCF tracks, based on locations found in the deck files.  These are duplicated from
    geoips.sectorfile.dynamic to avoid using modules from geoips. set_atcf_sector still imports from sectorfile,
    as we are still internally relying on the Sector objects. '''
import os
from datetime import datetime
import logging

from geoips2.filenames.base_paths import PATHS as gpaths

LOG = logging.getLogger(__name__)

# For consistency, these should match template_atcf_sectors
TC_SECTOR_NUM_LINES = 1400
TC_SECTOR_NUM_SAMPLES = 1400
TC_SECTOR_PROJECTION = 'eqc'
TC_SECTOR_PIXEL_WIDTH_M = 1000
TC_SECTOR_PIXEL_HEIGHT_M = 1000


def run_archer(xarray_obj, varname):
    ''' Run archer on the variable varname found in the xarray_obj'''
    KtoC_conversion = -273.15
    if varname in ['tb89h', 'tb89v', 'tb89hA', 'tb89hB', 'tb89vA', 'tb89vB', 'tb85h', 'tb85v', 'tb91h', 'tb91v']:
        archer_channel_type = '89GHz'
    elif varname in ['tb37h', 'tb37v', 'tb36h', 'tb36v']:
        archer_channel_type = '37GHz'
    elif 'BT' in varname:
        archer_channel_type = 'IR'
    elif 'Ref' in varname:
        archer_channel_type = 'Vis'
    else:
        LOG.warning('Unsupported sensor %s / channel %s type for ARCHER, returning without recentering',
                    xarray_obj.source_name, varname)
        return {}, {}, {}
    image = {}
    attrib = {}
    first_guess = {}
    attrib['archer_channel_type'] = archer_channel_type
    # This is currently unused in ARCHER, so just use GeoIPS platform names for attrib['sat']
    attrib['sat'] = xarray_obj.platform_name
    out_fname = 'archer_test_{0}_{1}_{2}.png'.format(xarray_obj.platform_name, xarray_obj.source_name,
                                                     archer_channel_type)
    image['lat_grid'] = xarray_obj['latitude'].to_masked_array()
    image['lon_grid'] = xarray_obj['longitude'].to_masked_array()
    image['data_grid'] = xarray_obj[varname].to_masked_array()
    import numpy
    num_masked = numpy.ma.count_masked(image['data_grid'])
    if num_masked > 0:
        LOG.warning('There are %s masked values in array of size %s, not attempting to run ARCHER', num_masked,
                    image['data_grid'].size)
        from IPython import embed as shell; shell()
        return {}, {}, {}
    # image['time_arr'] = Does not exist

    if 'BT' in varname:
        if xarray_obj[varname].units == 'celsius':
            image['data_grid'] = xarray_obj[varname].to_masked_array() - KtoC_conversion

    if xarray_obj.platform_name == 'himawari8':
        attrib['sensor'] = 'Imager'
        attrib['scan_type'] = 'Geo'
        attrib['nadir_lon'] = 140.7
    if xarray_obj.source_name == 'ssmis':
        attrib['sensor'] = 'SSMIS'
        attrib['scan_type'] = 'Conical'
    if xarray_obj.source_name == 'ssmi':
        attrib['sensor'] = 'SSMI'
        attrib['scan_type'] = 'Conical'
    if xarray_obj.source_name == 'tmi':
        attrib['sensor'] = 'TMI'
        attrib['scan_type'] = 'Conical'
    if xarray_obj.source_name == 'amsre':
        attrib['sensor'] = 'AMSRE'
        attrib['scan_type'] = 'Conical'
    if xarray_obj.source_name == 'amsr2':
        attrib['sensor'] = 'AMSR2'
        attrib['scan_type'] = 'Conical'
    if xarray_obj.source_name == 'gmi':
        attrib['sensor'] = 'GMI'
        attrib['scan_type'] = 'Conical'
    if xarray_obj.source_name == 'amsub':
        attrib['sensor'] = 'AMSUB'
        attrib['scan_type'] = 'Crosstrack'
    if xarray_obj.source_name == 'mhs':
        attrib['sensor'] = 'MHS'
        attrib['scan_type'] = 'Crosstrack'
    if xarray_obj.source_name == 'atms':
        attrib['sensor'] = 'ATMS'
        attrib['scan_type'] = 'Crosstrack'

    import calendar
    # This is currently unused by ARCHER - but it should probably be best track, not fx if using deck files ?
    first_guess['source'] = 'fx'
    first_guess['time'] = calendar.timegm(xarray_obj.start_datetime.timetuple())
    first_guess['vmax'] = xarray_obj.area_def.sector_info['wind_speed']
    first_guess['lat'] = xarray_obj.area_def.sector_info['clat']
    first_guess['lon'] = xarray_obj.area_def.sector_info['clon']

    from archer.archer4 import archer4
    in_dict, out_dict, score_dict = \
        archer4(image, attrib, first_guess, para_fix=True, display_filename=out_fname)
    return in_dict, out_dict, score_dict


def get_stormyear_from_deckfilename(deck_filename):
    ''' Get the storm year from the deck filename

    Args:
        deck_filename (str) : Path to deck file to search for storm year
                                Must be of format: xxxxxYYYY.dat - pulls YYYY from filename based on location

    Returns:
        (int) : Storm year
    '''
    return int(os.path.basename(deck_filename)[5:9])


def get_finalstormname_from_deckfile(deck_filename):
    ''' Get the final storm name from the deck file

    Args:
        deck_filename (str) : Path to deck file to search for final storm name

    Returns:
        (str) : Final storm name
    '''
    storm_year = get_stormyear_from_deckfilename(deck_filename)
    final_storm_name = 'INVEST'
    with open(deck_filename) as dfobj:
        for line in dfobj.readlines():
            fields = parse_atcf_deck_line(line, storm_year)
            if fields['storm_name'] and fields['storm_name'] != 'INVEST':
                final_storm_name = fields['storm_name']
    return final_storm_name


def produce_sector_metadata(area_def, xarray_obj, product_filename, metadata_dir='metadata'):
    ''' Produce metadata yaml file of sector information associated with the final_product
    Args:
        area_def (AreaDefinition) : Pyresample AreaDefintion object
        final_product (str) : Product that is associated with the passed area_def
        metadata_dir (str) : DEFAULT 'metadata' Subdirectory name for metadata (using non-default allows for
                                                non-operational outputs)

    Returns:
        (str) : Metadata yaml filename, if one was produced.
    '''
    from geoips2.output_formats.metadata import output_metadata_yaml
    from geoips2.filenames.atcf_filenames import atcf_metadata_dir
    from os.path import join as pathjoin
    from os.path import basename
    metadata_yaml_basename = basename(product_filename)+'.yaml'
    metadata_yaml_filename = pathjoin(atcf_metadata_dir(basedir=gpaths['TCWWW'],
                                                        tc_year=int(area_def.sector_info['storm_year']),
                                                        tc_basin=area_def.sector_info['storm_basin'],
                                                        tc_stormnum=int(area_def.sector_info['storm_num']),
                                                        metadata_type='sector_information',
                                                        metadata_datetime=xarray_obj.start_datetime,
                                                        metadata_dir=metadata_dir),
                                      metadata_yaml_basename)
    # os.path.join does not take a list, so "*" it
    product_partial_path = product_filename.replace(gpaths['TCWWW'], 'https://www.nrlmry.navy.mil/tcdat')
    # product_partial_path = pathjoin(*final_product.split('/')[-5:-1]+[basename(final_product)])
    return output_metadata_yaml(metadata_yaml_filename, area_def, xarray_obj, product_partial_path)


def deckfile_to_yamlfiles(deckfile_name, output_path, storm_year, final_storm_name):
    ''' Convert all entries in a deckfile to appropriate YAML formatted files.

    Args:
        deckfile_name (str) : Full path to deck file
        output_path (str) : Location for output YAML files
        storm_year (int) : Year of current storm
        final_storm_name (str) : Final name of storm (INVEST if never named)

    Returns:
        (list) : List of files that were actually created - skips existing files.
    '''
    from os.path import join, exists
    from geoips2.sector_utils.yaml_utils import write_yamldict
    yaml_filenames = []
    with open(deckfile_name) as dobj:
        for line in dobj.readlines():
            yamldict = deckline_to_yamldict(line, final_storm_name, storm_year)
            parts = line.split(',')
            out_fname = join('.', output_path, parts[2]+'_'+parts[0]+parts[1]+'.yaml')
            if not exists(out_fname):
                LOG.info('WRITING %s', out_fname)
                write_yamldict(yamldict, out_fname)
                yaml_filenames += [out_fname]
            else:
                LOG.info('SKIPPING %s already exists, delete if you need to recreate', out_fname)

    return yaml_filenames


def deckline_to_yamldict(deckline, final_storm_name, storm_year):
    ''' Convert a line found in a dick file to a dictionary that can be saved as a valid Pyresample YAML file

    Args:
        deckline (str) : Line from an ATCF deck file
        final_storm_name (str) : For named storm, use final name throughout reprocessing
        storm_year (int) : Storm year is not included in the line, so pass in

    Returns:
        (dict) : Dictionary that can be saved as a valid pyresample AreaDefinition YAML file
    '''
    from datetime import timedelta
    fields = parse_atcf_deck_line(deckline, storm_year)
    sectorname = get_atcf_sectorname(fields, final_storm_name, storm_year)
    from geoips2.sector_utils.yaml_utils import add_dynamic_datetime_to_yamldict
    from geoips2.sector_utils.yaml_utils import add_sectorinfo_to_yamldict
    from geoips2.sector_utils.yaml_utils import add_projection_to_yamldict
    from geoips2.sector_utils.yaml_utils import add_description_to_yamldict
    yamldict = {}
    yamldict[sectorname] = {}
    yamldict = add_sectorinfo_to_yamldict(yamldict, sectorname, fields)
    sector_start_datetime = fields['synoptic_time'] + timedelta(minutes=0)
    sector_end_datetime = sector_start_datetime + timedelta(minutes=359)
    yamldict = add_dynamic_datetime_to_yamldict(yamldict, sectorname, sector_start_datetime, sector_end_datetime)
    yamldict = add_description_to_yamldict(yamldict, sectorname,
                                           sector_type='atcf',
                                           sector_start_datetime=sector_start_datetime,
                                           info_dict=fields)
    yamldict = add_projection_to_yamldict(yamldict, sectorname,
                                          TC_SECTOR_PROJECTION,
                                          fields['clat'], fields['clon'],
                                          center_x=0, center_y=0,
                                          pix_x=TC_SECTOR_NUM_SAMPLES, pix_y=TC_SECTOR_NUM_LINES,
                                          pix_width_m=TC_SECTOR_PIXEL_WIDTH_M, pix_height_m=TC_SECTOR_PIXEL_HEIGHT_M)
    return yamldict


def create_atcf_sector_info_dict(clat, clon, synoptic_time, storm_year, storm_basin, storm_num, track_type=None,
                                 storm_name=None, final_storm_name=None,
                                 deck_line=None, source_sector_file=None,
                                 pressure=None, wind_speed=None):
    ''' Create storm info dictionary from items

    Args:
        clat (float) : center latitude of storm
        clon (float) : center longitude of storm
        synoptic_time (datetime) : time of storm location
        storm_year (int) : 4 digit year of storm
        storm_basin (str) : 2 digit basin identifier
        storm_num (int) : 2 digit storm number
        storm_name (str) : Common name of storm
        deck_line (str) :  source deck line for storm information
        pressure (float) : minimum pressure
        wind_speed (float) : maximum wind speed
    '''
    fields = {}
    fields['clat'] = clat
    fields['clon'] = clon
    fields['synoptic_time'] = synoptic_time
    fields['storm_year'] = storm_year
    fields['storm_basin'] = storm_basin
    fields['storm_num'] = storm_num
    fields['storm_name'] = 'unknown'
    fields['track_type'] = 'unknown'
    fields['final_storm_name'] = 'unknown'
    fields['source_sector_file'] = 'unknown'
    if track_type:
        fields['track_type'] = track_type
    if storm_name:
        fields['storm_name'] = storm_name
    if final_storm_name:
        fields['final_storm_name'] = final_storm_name
    if source_sector_file:
        fields['source_sector_file'] = source_sector_file
    fields['pressure'] = pressure
    fields['deck_line'] = deck_line
    fields['wind_speed'] = wind_speed
    return fields


def parse_atcf_deck_line(line, storm_year, final_storm_name=None):
    ''' Retrieve the storm information from the current line from the deck file

    Args:
        line (str) : Current line from the deck file including all storm information

    Returns:
        (dict) : Dictionary of the fields from the current storm location from the deck file
                    Valid fields can be found in geoips2.sector_utils.utils.SECTOR_INFO_ATTRS
    '''
    parts = line.split(',', 40)
    fields = {}
    fields['deck_line'] = line.strip()
    fields['storm_basin'] = parts[0]
    fields['storm_num'] = parts[1]
    fields['synoptic_time'] = datetime.strptime(parts[2], '%Y%m%d%H')
    fields['track_type'] = parts[4]
    fields['clat'] = parts[6]
    fields['clon'] = parts[7]
    fields['clat'] = float(fields['clat'])
    fields['clon'] = float(fields['clon'])
    fields['wind_speed'] = parts[8]
    if fields['wind_speed']:
        fields['wind_speed'] = float(fields['wind_speed'])
    fields['pressure'] = parts[9]
    if fields['pressure']:
        fields['pressure'] = float(fields['pressure'])

    fields['storm_name'] = parts[39]
    fields['final_storm_name'] = 'unknown'
    if final_storm_name:
        fields['final_storm_name'] = final_storm_name
    fields['storm_year'] = storm_year
    return fields


def set_atcf_proj_info(clat, clon, pr_proj=TC_SECTOR_PROJECTION,
                       num_samples=TC_SECTOR_NUM_SAMPLES, num_lines=TC_SECTOR_NUM_LINES,
                       pixel_width=TC_SECTOR_PIXEL_WIDTH_M, pixel_height=TC_SECTOR_PIXEL_HEIGHT_M):
    ''' Take the current storm location, and create the standard atcf projection from those fields

    Args:
        fields (dict) : dictionary of storm info, including clat and clon
                            Valid fields can be found in geoips2.sector_utils.utils.SECTOR_INFO_ATTRS
    '''
    width_m = num_samples * pixel_width
    height_m = num_lines * pixel_height

    proj4_dict = {'proj': pr_proj,
                  'a': 6371228.0,
                  'lat_0': clat,
                  'lon_0': clon,
                  'units': 'm',
                 }
    area_left = -width_m / 2.0
    area_right = width_m / 2.0
    area_bot = -height_m / 2.0
    area_top = height_m / 2.0
    area_extent = (area_left, area_bot, area_right, area_top)
    return proj4_dict, area_extent


def get_atcf_sectorname(fields, finalstormname, tcyear):
    if not finalstormname:
        finalstormname = fields['storm_name']
    newname = '{0}{1}{2}'.format(fields['storm_basin'].lower(),
                                 fields['storm_num'],
                                 finalstormname.lower())

    newname = newname.replace('_', '').replace('.', '').replace('-', '')

    # This ends up being tc2016io01one
    area_id = 'tc'+str(tcyear)+newname
    return area_id


def recenter_area_def(area_def, archer_out_dict):
    ''' Use information from archer output dictionary to recenter the storm specified in area_def'''
    new_sector_info = area_def.sector_info.copy()
    if not archer_out_dict or not archer_out_dict['center_lat'] or not archer_out_dict['center_lon']:
        LOG.warning('ARCHER returned no center lat/lon values, not recentering')
        return area_def
    new_sector_info['clat'] = float(archer_out_dict['center_lat'])
    new_sector_info['clon'] = float(archer_out_dict['center_lon'])
    new_sector_info['source_sector_file'] = 'archer recenter'
    new_sector_info['deck_line'] = 'archer recenter'
    archer_area_def = set_atcf_area_def(new_sector_info)
    return archer_area_def 


def set_atcf_area_def(fields, tcyear=None,
                      finalstormname=None, source_sector_file=None,
                      clat=None, clon=None,
                      num_lines=None, num_samples=None,
                      pixel_width=None, pixel_height=None,
                      track_type=None):
    ''' This is copied from geoips.sectorfile.dynamic.py, and still relies heavily on geoips.sectorfile'''
    if not pixel_width:
        pixel_width = TC_SECTOR_PIXEL_WIDTH_M
    if not pixel_height:
        pixel_height = TC_SECTOR_PIXEL_HEIGHT_M
    if not num_samples:
        num_samples = TC_SECTOR_NUM_SAMPLES
    if not num_lines:
        num_lines = TC_SECTOR_NUM_LINES
    if not finalstormname and 'final_storm_name' in fields:
        finalstormname = fields['final_storm_name']
    if not source_sector_file and 'source_sector_file' in fields:
        source_sector_file = fields['source_sector_file']
    if not tcyear:
        tcyear = fields['storm_year']
    if clat is None:
        clat = fields['clat']
    if clon is None:
        clon = fields['clon']

    area_id = get_atcf_sectorname(fields, finalstormname, tcyear)

    long_description = '{0} synoptic_time {1}'.format(area_id, str(fields['synoptic_time']))

    proj4_dict, area_extent = set_atcf_proj_info(clat=clat, clon=clon,
                                                 num_samples=num_samples, num_lines=num_lines,
                                                 pixel_width=pixel_width, pixel_height=pixel_height)

    # Create the AreaDefinition object from given fields.  We are currently relying on Sector objects
    # for some information - need to decide how to handle this directly.
    # This is area_id= then name= for Python2, area_id= then description= for Python3
    from pyresample import AreaDefinition
    try:
        # Backwards compatibility for Python 2 version of pyresample
        area_def = AreaDefinition(area_id,
                                  long_description,
                                  proj_id='{0}_{1}'.format(proj4_dict['proj'], area_id),
                                  proj_dict=proj4_dict,
                                  x_size=num_samples,
                                  y_size=num_lines,
                                  area_extent=area_extent)
    except TypeError:
        area_def = AreaDefinition(area_id,
                                  long_description,
                                  proj_id='{0}_{1}'.format(proj4_dict['proj'], area_id),
                                  projection=proj4_dict,
                                  width=num_samples,
                                  height=num_lines,
                                  area_extent=area_extent)

    area_def.sector_start_datetime = fields['synoptic_time']
    area_def.sector_end_datetime = fields['synoptic_time']
    area_def.sector_type = 'atcf'
    area_def.sector_info = {}

    # area_def.description is Python3 compatible, and area_def.name is Python2 compatible
    area_def.description = long_description
    if not hasattr(area_def, 'name'):
        area_def.name = long_description

    area_def.sector_info['source_sector_file'] = source_sector_file
    # area_def.sector_info['sourcetemplate'] = dynamic_templatefname
    # area_def.sector_info['sourcedynamicxmlpath'] = dynamic_xmlpath
    # FNMOC sectorfile doesn't have pressure
    for fieldname in fields.keys():
        area_def.sector_info[fieldname] = fields[fieldname]
    area_def.sector_info['storm_year'] = tcyear

    # If storm_name is undefined in the current deck line, set it to finalstormname
    if area_def.sector_info['storm_name'] == '' and finalstormname:
        LOG.info('USING finalstormname "%s" rather than deck storm name "%s"',
                 finalstormname,
                 area_def.sector_info['storm_name'])
        area_def.sector_info['storm_name'] = finalstormname

    LOG.debug('      Current TC sector: %s', fields['deck_line'])
    return area_def


def get_final_storm_name(deck_lines, tcyear):
    finalstormname = 'INVEST'
    for line in deck_lines:
        curr_fields = parse_atcf_deck_line(line, tcyear, finalstormname)
        if curr_fields['storm_name']:
            finalstormname = curr_fields['storm_name']
    return finalstormname


def deckfile_to_area_defs(deckfile_name, pixel_size_x=TC_SECTOR_PIXEL_WIDTH_M, pixel_size_y=TC_SECTOR_PIXEL_HEIGHT_M,
                          num_pixels_x=TC_SECTOR_NUM_SAMPLES, num_pixels_y=TC_SECTOR_NUM_LINES):
    ''' This is copied from geoips.sectorfile.dynamic, but simplified.'''
    # dynamic_xmlpath = gpaths['SATOPS']+'/intermediate_files/sectorfiles/atcf_xml'

    # CHANGED FROM geoips/geoips/sectorfile/dynamic.py
    # dynamic_templatefname = None
    # for templatefname in gpaths['TEMPLATEPATHS']:
    #     # Find the one that exists
    #     if os.path.exists(templatefname+'/template_atcf_sectors.xml'):
    #         dynamic_templatefname = templatefname+'/template_atcf_sectors.xml'
    #     # Take the first one
    #     if dynamic_templatefname:
    #         continue
    # dynamic_templatefname = gpaths['ATCF_TEMPLATE']
    # LOG.info(dynamic_templatefname)

    # Must get tcyear out of the filename in case a storm crosses TC vs calendar years.
    tcyear = os.path.basename(deckfile_name)[5:9]
    # print tcyear

    flatsf_lines = open(deckfile_name).readlines()
    finalstormname = get_final_storm_name(flatsf_lines, tcyear)

    # flatsf_lines go from OLDEST to NEWEST (so firsttime is the OLDEST
    # storm location)
    all_fields = []
    for line in flatsf_lines:
        curr_fields = parse_atcf_deck_line(line, tcyear, finalstormname)
        if curr_fields['storm_name']:
            finalstormname = curr_fields['storm_name']
        all_fields += [curr_fields]

    area_defs = []
    for fields in all_fields:
        # area_defs += [set_atcf_sector(fields, dynamic_templatefname, finalstormname, tcyear, sfname, dynamic_xmlpath)]
        area_defs += [set_atcf_area_def(fields, tcyear, finalstormname=finalstormname,
                                        source_sector_file=deckfile_name,
                                        num_lines=num_pixels_y, num_samples=num_pixels_x,
                                        pixel_width=pixel_size_x, pixel_height=pixel_size_y)]

    return area_defs


def interpolate_storm_location(interp_dt, longitudes, latitudes, synoptic_times):
    ''' Interpolate the storm location at a specific time based on a list of known locations and times'''
    LOG.info('interp_dt: %s\nlatitudes:\n%s\nlongitudes:\n%s\nsynoptic_times:\n%s',
             interp_dt, latitudes, longitudes, synoptic_times)
    # from IPython import embed as shell; shell()
