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

''' Coverage check routine for masked arrays
'''

import logging

LOG = logging.getLogger(__name__)


def rgba(xarray_obj, variable_name, area_def=None):
    ''' Coverage check routine for xarray objects with masked projected arrays.

    Args:
        xarray_obj (xarray.Dataset) :  xarray object containing variable "variable_name"
        variable_name (str) : variable name to check percent unmasked

    Returns:
        float : Percent coverage of variable_name
    '''
    
    from geoips2.image_utils.mpl_utils import percent_unmasked_rgba
    return percent_unmasked_rgba(xarray_obj[variable_name].to_masked_array())
