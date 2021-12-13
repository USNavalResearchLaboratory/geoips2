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

''' Coverage check routine for 
'''

import logging

import numpy

LOG = logging.getLogger(__name__)


def create_radius(tempArr, radius = 300, x = 0, y = 0):
    """Function to create a radius around given x,y coordinates in the 2d array.

    Given the radius and the x,y coordinates it creates a circle around those points using the skimage.draw library

    Args:
        tempArr (int): The 2D array.
        radius (int): The radius of the circle. 500 is default value.
        x (int): The x coordinate of middle circle point. 0 is default value.
        y (int): The x coordinate of middle circle point. 0 is default value.

    Returns:
        2D array with circle created at the x,y coordinate with the given radius. All circles are marked as 1.
    """
    
    from skimage.draw import disk
    dumby_arr = numpy.zeros((tempArr.shape), dtype=numpy.uint8)
    rr, cc = disk((x, y), radius, shape = dumby_arr.shape)
    dumby_arr[rr, cc] = 1
    
    return dumby_arr


def center_radius(xarray_obj, variable_name, area_def=None, radius_km=300):
    ''' Coverage check routine for xarray objects with masked projected arrays.

    Args:
        xarray_obj (xarray.Dataset) :  xarray object containing variable "variable_name"
        variable_name (str) : variable name to check percent unmasked
        radius_km (float) : Radius of center disk to check for coverage

    Returns:
        float : Percent coverage of variable_name
    '''
    tempArr = xarray_obj[variable_name].to_masked_array()
    dumby_arr = create_radius(tempArr, radius=radius_km, x=tempArr.shape[0] / 2, y=tempArr.shape[1] / 2)
    num_valid_in_radius = numpy.count_nonzero(numpy.where(dumby_arr & ~tempArr.mask, 1, 0))
    num_total_in_radius = numpy.count_nonzero(dumby_arr)
    return (float(num_valid_in_radius) / num_total_in_radius)*100.0
