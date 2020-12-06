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

'''Read Microwave Imagery from NRL TC (MINT) data products'''
import logging

LOG = logging.getLogger(__name__)

STORM_NAMES = {'al132003': 'ISABEL'}

ROI_INFO = {'BGHI':  {'ssmi': 10000,
                      'ssmis': 10000},
            'BGLO':  {'ssmi': 20000,
                      'ssmis': 20000},
            'HI':    {'ssmi': 10000,
                      'ssmis': 10000,
                      'tmi': 10000,
                      'amsre': 10000},
            'LO':    {'ssmi': 20000,
                      'tmi': 20000,
                      'amsre': 20000,
                      'ssmis': 20000},
            'LO37':  {'ssmi': 20000,
                      'tmi': 20000,
                      'amsre': 20000,
                      'ssmis': 20000},
            'SSMIS_HIER': {'ssmis': 10000},
            'SSMIS_LAS':  {'ssmis': 10000},
            'SSMIS_UAS':  {'ssmis': 10000}}

# Each variable should only be listed ONCE in this dictionary - separate datasets for different sets of lat/lons,
# since we have standard 'latitude' and 'longitude' and 'timestamp' variables for sectoring purposes.
DATASET_INFO = {'BGHI':  ['BG89h', 'BG89v'],    # ssmi, ssmis
                'BGLO':  ['BG37h', 'BG37v'],    # ssmi, ssmis
                'HI':    ['tb89h', 'tb89v',     # ssmi, ssmis, tmi, amsre
                          'tb85h', 'tb85v',     # ssmi, tmi
                          'tb91h', 'tb91v'],    # ssmis
                # 'LO':    ['tb37h', 'tb37v',     # ssmi, tmi, amsre, ssmis has a different set of lat lons for 37GHz
                'LO':    ['tb22v',              # ssmis, tmi
                          'tb19h', 'tb19v',     # ssmis, tmi, amsre
                          'tb10h', 'tb10v',     # tmi
                          'tb24h', 'tb24v',     # amsre
                          'tb11h', 'tb11v', 'tb7h', 'tb7v'],  # amsre
                'LO37': ['tb37h', 'tb37v'],  # ssmis
                'SSMIS_HIER': ['tb150h', 'tb183h_1', 'tb183h_3', 'tb183h_7'],  # ssmis
                'SSMIS_LAS':  ['tb50h', 'tb52h', 'tb53h', 'tb54h', 'tb55h', 'tb57rc', 'tb59rc', 'tb60rc_ch24'],  # ssmis
                'SSMIS_UAS':  ['tb60rc_ch21', 'tb60rc_ch22', 'tb60rc_ch23', 'tb60rc_ch20', 'tb604c_ch19']}  # ssmis

# These are automatically set on the new DataArrays when the corresponding variables are set.  Just map them
# from their internal names to 'latitude' and 'longitude'
GVARS_INFO = {'BGlat_hi': 'latitude',
              'BGlon_hi': 'longitude',
              'BGlat_lo': 'latitude',
              'BGlon_lo': 'longitude',
              'lat_hi': 'latitude',
              'lon_hi': 'longitude',
              'lat_lo': 'latitude',
              'lon_lo': 'longitude',
              'lat_37': 'latitude',  # ssmis
              'lon_37': 'longitude',  # ssmis
              'lat_hier': 'latitude',
              'lon_hier': 'longitude',
              'lat_las': 'latitude',
              'lon_las': 'longitude',
              'lat_uas': 'latitude',
              'lon_uas': 'longitude'}

TYPE_INFO = {'SSM/I > Special Sensor Microwave/Imager':  ['SSMI_BGHI', 'SSMI_BGLO', 'SSMI_HI', 'SSMI_LO'],
             'SSMIS > Special Sensor Microwave Imager/Sounder':  ['SSMIS_BGHI', 'SSMIS_BGLO', 'SSMIS_HI', 'SSMIS_LO37',
                                                                  'SSMIS_LO', 'SSMIS_HIER', 'SSMIS_LAS', 'SSMIS_UAS'],
             'TRMM/TMI':  ['TMI_HI', 'TMI_LO'],
             'AMSR-E':  ['AMSRE_HI', 'AMSRE_LO']}

SENSOR_DISPLAY_INFO = {'SSM/I > Special Sensor Microwave/Imager':  'SSM/I',
                       'SSMIS > Special Sensor Microwave Imager/Sounder':  'SSMIS',
                       'TRMM/TMI':  'TMI',
                       'AMSR-E':  'AMSR-E'}

PLATFORM_DISPLAY_INFO = {'DMSP 5D-2/F08 > Defense Meteorological Satellite Program-F08':  'F08',
                         'DMSP 5D-2/F10 > Defense Meteorological Satellite Program-F10':  'F10',
                         'DMSP 5D-2/F11 > Defense Meteorological Satellite Program-F11':  'F11',
                         'DMSP 5D-2/F13 > Defense Meteorological Satellite Program-F13':  'F13',
                         'DMSP 5D-2/F14 > Defense Meteorological Satellite Program-F14':  'F14',
                         'DMSP 5D-3/F15 > Defense Meteorological Satellite Program-F15':  'F15',
                         'DMSP 5D-3/F16 > Defense Meteorological Satellite Program-F16':  'F16',
                         'DMSP 5D-3/F17 > Defense Meteorological Satellite Program-F17':  'F17',
                         'DMSP 5D-3/F18 > Defense Meteorological Satellite Program-F18':  'F18',
                         'TRMM':  'TRMM',
                         'EOS-PM1':  'Aqua'}

INSTITUTIONS_INFO = {'Naval Research Laboratory, Monterey CA (NRL-MRY)': 'nrlmryMINT'}

GEOIPS_SENSOR_IDS = {'SSM/I > Special Sensor Microwave/Imager':  'ssmi',
                     'SSMIS > Special Sensor Microwave Imager/Sounder':  'ssmis',
                     'TRMM/TMI':  'tmi',
                     'AMSR-E':  'amsre'}

GEOIPS_PLATFORM_IDS = {'DMSP 5D-2/F08 > Defense Meteorological Satellite Program-F08':  'f08',
                       'DMSP 5D-2/F10 > Defense Meteorological Satellite Program-F10':  'f10',
                       'DMSP 5D-2/F11 > Defense Meteorological Satellite Program-F11':  'f11',
                       'DMSP 5D-2/F13 > Defense Meteorological Satellite Program-F13':  'f13',
                       'DMSP 5D-2/F14 > Defense Meteorological Satellite Program-F14':  'f14',
                       'DMSP 5D-3/F15 > Defense Meteorological Satellite Program-F15':  'f15',
                       'DMSP 5D-3/F16 > Defense Meteorological Satellite Program-F16':  'f16',
                       'DMSP 5D-3/F17 > Defense Meteorological Satellite Program-F17':  'f17',
                       'DMSP 5D-3/F18 > Defense Meteorological Satellite Program-F18':  'f18',
                       'TRMM':  'trmm',
                       'EOS-PM1':  'aqua'}


def mint_ncdf(fname, metadata_only=False, variables=None):
    ''' Read TC MINT netcdf data products.

    Args:
        fname (str): Required full path to netcdf file

    Returns:
        (list of xarray.Dataset) with required Variables and Attributes in each Dataset:
            Variables: 'latitude', 'longitude', 'timestamp'
            Attributes: 'source_name', 'platform_name', 'data_provider', 'interpolation_radius_of_influence'
                        'start_datetime', 'end_datetime'
            Optional Attrs: 'original_source_filename', 'filename_datetime'
    '''
    import xarray
    xarray_obj = xarray.open_dataset(str(fname))

    if xarray_obj.institution in INSTITUTIONS_INFO.keys():
        xarray_obj.attrs['data_provider'] = INSTITUTIONS_INFO[xarray_obj.institution]
    else:
        xarray_obj.attrs['data_provider'] = xarray_obj.institution
    xarray_obj.attrs['original_source_filename'] = fname
    xarray_obj.attrs['source_name'] = GEOIPS_SENSOR_IDS[xarray_obj.sensor]
    xarray_obj.attrs['platform_name'] = GEOIPS_PLATFORM_IDS[xarray_obj.platform]
    xarray_obj.attrs['interpolation_radius_of_influence'] = 10000
    from datetime import datetime
    xarray_obj.attrs['start_datetime'] = datetime.strptime(xarray_obj.TC_atcf_linint_dtg, '%Y%m%d%H%M%S')
    xarray_obj.attrs['end_datetime'] = datetime.strptime(xarray_obj.TC_atcf_linint_dtg, '%Y%m%d%H%M%S')
    xarray_obj.attrs['filename_datetime'] = xarray_obj.attrs['start_datetime']
    xarray_obj.attrs['dataprovider_display'] = xarray_obj.institution

    xarray_obj.attrs['source_name_product'] = GEOIPS_SENSOR_IDS[xarray_obj.sensor]
    xarray_obj.attrs['source_name_display'] = SENSOR_DISPLAY_INFO[xarray_obj.sensor]
    xarray_obj.attrs['platform_name_product'] = GEOIPS_PLATFORM_IDS[xarray_obj.platform]
    xarray_obj.attrs['platform_name_display'] = PLATFORM_DISPLAY_INFO[xarray_obj.platform]

    xarray_obj.attrs['sector_name_product'] = xarray_obj.TC_atcf_id
    xarray_obj.attrs['sector_name_display'] = xarray_obj.TC_atcf_id

    tcyear = int(xarray_obj.TC_atcf_id[4:8])  # 2003
    finalstormname = 'unknown'
    if xarray_obj.TC_atcf_id in STORM_NAMES.keys():
        finalstormname = STORM_NAMES[xarray_obj.TC_atcf_id]
    from geoips2.sector_utils.atcf_tracks import set_atcf_area_def, create_atcf_sector_info_dict
    fields = create_atcf_sector_info_dict(float(xarray_obj.TC_atcf_lat),
                                          float(xarray_obj.TC_atcf_lon),
                                          synoptic_time=datetime.strptime(xarray_obj.TC_atcf_dtg, '%Y%m%d%H'),
                                          storm_year=tcyear,  # 2003
                                          storm_basin=xarray_obj.TC_atcf_id[0:2].upper(),  # AL
                                          storm_num=int(xarray_obj.TC_atcf_id[2:4]),  # 13
                                          storm_name=finalstormname,
                                          final_storm_name=finalstormname,
                                          deck_line=xarray_obj.original_source_filename,
                                          source_file=xarray_obj.original_source_filename,
                                          pressure=float(xarray_obj.TC_atcf_mslp),
                                          wind_speed=float(xarray_obj.TC_atcf_vmax))
    xarray_obj.attrs['area_def'] = set_atcf_area_def(fields)

    if metadata_only:
        return [xarray_obj]

    xarray_objs = []
    for dsname in DATASET_INFO:
        sub_xarray = xarray.Dataset()
        sub_xarray.attrs = xarray_obj.attrs.copy()

        # Add all variables in the current dataset
        for varname in DATASET_INFO[dsname]:
            if varname in xarray_obj.variables.keys():
                if variables and varname not in variables:
                    continue
                sub_xarray[varname] = xarray_obj[varname]

        # If there were any variables from the current dataset, then add it to the list of xarray Datasets.
        # NOTE: when the variables are added to the DataArray above, the associated lat/lon "coordinate" variables
        # are added as well. We do not have to explicitly add the lat/lon variables, but we do need to rename them
        if sub_xarray.variables.keys():
            for varname in GVARS_INFO:
                if varname in sub_xarray.variables.keys():
                    sub_xarray = sub_xarray.rename({varname: GVARS_INFO[varname]})
                    sub_xarray = sub_xarray.set_coords(GVARS_INFO[varname])
            # Set the dataset name on the xarray object, for reference
            sub_xarray.attrs['dataset_name'] = dsname
            sub_xarray.attrs['interpolation_radius_of_influence'] = ROI_INFO[dsname][sub_xarray.source_name]
            xarray_objs += [sub_xarray]
        else:
            LOG.info('SKIPPING: NO VARIABLES FOR DATASET %s', dsname)
            continue
    return xarray_objs
