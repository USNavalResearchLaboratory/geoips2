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

''' Data manipulation steps for "37pct" product.

    This algorithm expects Brightness Temperatures in units of degrees Kelvin
'''

import logging

LOG = logging.getLogger(__name__)

alg_func_type = 'list_numpy_to_numpy'


def pmw_37pct(arrays, output_data_range=None, min_outbounds='crop', max_outbounds='mask', norm=False, inverse=False):
    ''' Data manipulation steps for "37pct" product algorithm.

    This algorithm expects Brightness Temperatures in units of degrees Kelvin, and returns degrees Kelvin

    Args:
        data (list[numpy.ndarray]) : 
            * numpy.ndarray or numpy.MaskedArray of channel data, in order of sensor "channels" list
            * Degrees Kelvin

    Returns:
        numpy.ndarray : numpy.ndarray or numpy.MaskedArray of appropriately scaled channel data,
                        in degrees Kelvin.
    '''

    h37 = arrays[0]
    v37 = arrays[1]

    out = (2.15*v37)-(1.15*h37)

    if output_data_range is None:
        output_data_range = [230.0, 280.0]

    from geoips2.data_manipulations.corrections import apply_data_range
    data = apply_data_range(out,
                            min_val=output_data_range[0], max_val=output_data_range[1],
                            min_outbounds=min_outbounds, max_outbounds=max_outbounds,
                            norm=norm, inverse=inverse)
    return data
