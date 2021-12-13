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

''' Coverage check routine for windbarb xarrays
'''

import logging

LOG = logging.getLogger(__name__)


def windbarbs(xarray_obj, variable_name, area_def):
    ''' Coverage check routine for wind barb xarray object.

    This algorithm expects input windspeed with units "kts" and returns in "kts"

    Args:
        xarray_obj (xarray.Dataset) :  xarray object containing variable "variable_name" for registering to
        variable_name (str) : variable name to register to 

    Returns:
        float : Percent coverage of variable_name over area_def
    '''

    xarray_obj[variable_name].to_masked_array()
    from geoips2.dev.interp import get_interp
    interp_func = get_interp('pyresample_wrappers.interp_nearest')
    output_xarray = interp_func(area_def, xarray_obj, None, [variable_name], array_num=0)

    from geoips2.data_manipulations.info import percent_unmasked
    return percent_unmasked(output_xarray[variable_name].to_masked_array())
