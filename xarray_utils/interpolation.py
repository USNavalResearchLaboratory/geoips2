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

''' Xarray wrappers for driving the interpolation routines with basic Python inputs and outputs'''
import logging
LOG = logging.getLogger(__name__)

#from IPython import embed as shell

def interp_nearest(area_def, xarray_obj, array_num=None, varlist=None):
    ''' Set up the call to interp_kd_tree using standard attributes and variables in a given xarray object.
        Returns:
            list of numpy.ma.MaskedArray'''

    LOG.info('Interpolating nearest using standard scifile register method: kd_tree nearest')

    vars_to_interp = []
    if array_num is not None:
        lons = xarray_obj['longitude'].to_masked_array()[:, :, array_num]
        lats = xarray_obj['latitude'].to_masked_array()[:, :, array_num]
        for varname in varlist:
            vars_to_interp += [xarray_obj[varname].to_masked_array()[:, :, array_num]]
    else:
        lons = xarray_obj['longitude'].to_masked_array()
        lats = xarray_obj['latitude'].to_masked_array()
        for varname in varlist:
            vars_to_interp += [xarray_obj[varname].to_masked_array()]

    # Use standard scifile / pyresample registration
    from geoips2.interpolation.interp_pyresample import interp_kd_tree, get_data_box_definition
    data_box_definition = get_data_box_definition(xarray_obj.source_name,
                                                  lons,
                                                  lats)

    interp_data = interp_kd_tree(vars_to_interp,
                                 area_def,
                                 data_box_definition,
                                 float(xarray_obj.interpolation_radius_of_influence),
                                 interp_type='nearest')

    from geoips2.data_manipulations.info import percent_unmasked

    for arr, orig, varname in zip(interp_data, vars_to_interp, varlist):
        LOG.info('%s min/max before: %s to %s', varname, orig.min(), orig.max())
        LOG.info('%s min/max after:  %s to %s', varname, arr.min(), arr.max())
        LOG.info('%s Percent unmasked before %s', varname, percent_unmasked(orig))
        LOG.info('%s Percent unmasked after  %s', varname, percent_unmasked(arr))

    return interp_data


def interp_gauss(area_def, xarray_obj, sigmaval=None, array_num=None, varlist=None):
    ''' Use pyresample gaussian interpolation from interp_kd_tree:  return of list of numpy.ma.MaskedArray '''
    LOG.info('Interpolating using standard scifile register method: kd_tree gauss sigmaval %s', sigmaval)

    vars_to_interp = []
    if array_num is not None:
        lons = xarray_obj['longitude'].to_masked_array()[:, :, array_num]
        lats = xarray_obj['latitude'].to_masked_array()[:, :, array_num]
        for varname in varlist:
            vars_to_interp += [xarray_obj[varname].to_masked_array()[:, :, array_num]]
    else:
        lons = xarray_obj['longitude'].to_masked_array()
        lats = xarray_obj['latitude'].to_masked_array()
        for varname in varlist:
            vars_to_interp += [xarray_obj[varname].to_masked_array()]

    # Use standard scifile / pyresample registration
    from geoips2.interpolation.interp_pyresample import interp_kd_tree, get_data_box_definition
    data_box_definition = get_data_box_definition(xarray_obj.source_name,
                                                  lons,
                                                  lats)

    # Set s default value of igmaval as 10000

    if sigmaval is None:
        sigmaval = 10000

    interp_data = interp_kd_tree(vars_to_interp,
                                   area_def,
                                   data_box_definition,
                                   xarray_obj.interpolation_radius_of_influence,
                                   interp_type='gauss',
                                   sigmas=sigmaval)
    return interp_data


def interp_kde(area_def, wind_xarray, bwmethod='scott'):
    ''' Set imgkey as 'KDE<bwmethod>' where <method> is one of 'scott' or
    'silverman' NOTE THIS DOESN'T WORK 
     This function is not completed yet because interp_gaussian_kde is not finished'''
    LOG.info('Interpolating using scipy.stats.gaussian_kde %s', bwmethod)
    from geoips2.interpolation.interp_scipy import interp_gaussian_kde
    target_lons, target_lats = area_def.get_lonlats()
    interp_data = interp_gaussian_kde(wind_xarray['wind_speed_kts'].to_masked_array(),
                                      wind_xarray['longitude'].to_masked_array(),
                                      wind_xarray['latitude'].to_masked_array(),
                                      target_lons,
                                      target_lats,
                                      bwmethod)
    return interp_data


def interp_scipy_grid(area_def, xarray_obj, varname, method=None, array_num=None):
    ''' Set imgkey as 'Griddata<method>' where <method> is one of 'cubic', 'linear' or 'nearest' '''
    LOG.info('Interpolating using scipy.interpolate.griddata %s', method)

    if array_num is not None:
        lons = xarray_obj['longitude'].to_masked_array()[:, :, array_num]
        lats = xarray_obj['latitude'].to_masked_array()[:, :, array_num]
        var_to_interp = xarray_obj[varname].to_masked_array()[:, :, array_num]
    else:
        lons = xarray_obj['longitude'].to_masked_array()
        lats = xarray_obj['latitude'].to_masked_array()
        var_to_interp = xarray_obj[varname].to_masked_array()
    
    from geoips2.interpolation.interp_scipy import interp_griddata
    min_gridlon = area_def.area_extent_ll[0]
    max_gridlon = area_def.area_extent_ll[2]
    min_gridlat = area_def.area_extent_ll[1]
    max_gridlat = area_def.area_extent_ll[3]
    numx_grid = area_def.pixel_size_x
    numy_grid = area_def.pixel_size_y
    
    interp_data = interp_griddata(var_to_interp,
                                  lons,
                                  lats,
                                  min_gridlon,
                                  max_gridlon,
                                  min_gridlat,
                                  max_gridlat,
                                  numx_grid,
                                  numy_grid,
                                  method)
    
    return interp_data
