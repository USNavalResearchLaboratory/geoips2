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

#!/usr/bin/env python
''' Module for outputting netcdf data file from dictionary of numpy arrays '''

# Standard Python Libraries
import os
import logging

# Installed libraries
import netCDF4

LOG = logging.getLogger(__name__)


def create_dimensions(nc_obj, dimensions_dict):
    ''' Create dimensions for netcdf object'''
    for key, dim in dimensions_dict.items():
        nc_obj.createDimension(key, dim)


def create_variable_sds(nc_obj, var_short_name, var_type, var_dims,
                        var_standard_name=None, var_units=None):
    ''' Create variable sds for netcdf object'''
    sds = nc_obj.createVariable(var_short_name, var_type, var_dims)
    if var_standard_name:
        sds.standard_name = var_standard_name
    if var_units:
        sds.units = var_units


def fill_variable_sds(nc_obj, var_short_name, data):
    ''' Fill variable var_short_name in netcdf file with data from input array data'''
    nc_obj.variables[var_short_name][:] = data


def add_global_attributes(nc_obj, global_atts_dict):
    ''' Add global attributes to netcdf file from dictionary'''
    if isinstance(global_atts_dict, dict):
        for gkey, gatt in global_atts_dict.items():
            if isinstance(gatt, dict):
                continue
            nc_obj.setncattr_string(gkey, gatt)


def write(data_dict, outfile=None, dimensions=None, metadata=None):
    '''
    Write registered data to netCDF file.
    +------------------+-----------+---------------------------------------------------+
    | Parameters:      | Type:     | Description:                                      |
    +==============----+===========+===================================================+
    | data_dict:       | *dict*    | Dictionary holding data to write.                 |
    |                  |           | Each key in data_dict is the name of the variable |
    |                  |           | to store, and holds another dictionary that       |
    |                  |           | should contain the following keys:                |
    |                  |           |        data, name, units, dimensions, and dtype   |
    +------------------+-----------+---------------------------------------------------+
    | outfile:         | *str*     | Name of netcdf file                               |
    +------------------+-----------+---------------------------------------------------+
    | dimensions:      | *dict*    | Dictionary holding dimensions for netcdf variables|
    +------------------+-----------+---------------------------------------------------+
    | metadata:        | *dict*    | Dictionary holding keys with information to write |
    |                  |           | as global attributes to the netcdf file (optional)|
    +------------------+-----------+---------------------------------------------------+

    For example, say we want to store the 11um field, data dict will be the following:
    data_dict = {'11um':{'data':11um_array,'name':'11um brightness temperature',
                         'dimensions':('lines','samples','dtype':np.float64)}
                }
    The dimensions dictionary in this case will be the following:
    dimensions = {'lines':<number_of_lines>,'samples':<number_of_samples>}
    '''
    # Check to see if we have all the information we need
    if not outfile:
        raise ValueError('Must provide name for out name for file!')
    if isinstance(dimensions, type(None)):
        raise ValueError('Must provide dictionary holding netcdf dimensions')

    # Check to see if writing path exists, and add option to create
    # said path if non-existent
    out_dir = os.path.dirname(outfile)
    if not os.path.exists(out_dir):
        LOG.info('Creating Directory: %s', out_dir)
        from geoips2.filenames.base_paths import make_dirs
        make_dirs(out_dir)

    LOG.info('Storing registered data to netCDF file')
    with netCDF4.Dataset(outfile, 'w', format='NETCDF4') as nc_file:
        # Define dimensions for variables
        create_dimensions(nc_file, dimensions)
        # Iterate through keys in data_dict and store to netcdf file
        for key, ncinfo in data_dict.iteritems():
            # Create variable sds
            create_variable_sds(nc_file,
                                var_short_name=key,
                                var_type=ncinfo['dtype'],
                                var_dims=ncinfo['dimensions'],
                                var_standard_name=ncinfo['name'],
                                var_units=ncinfo['units'])
            # Populate variable sds with data
            fill_variable_sds(nc_file, key, ncinfo['data'])
        # Finally add global attributes
        add_global_attributes(nc_file, metadata)
    LOG.info('Created: %s', outfile)
