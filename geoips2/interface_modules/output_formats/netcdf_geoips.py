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

import os
import logging

LOG = logging.getLogger(__name__)

output_type = 'xarray_data'


def netcdf_geoips(xarray_obj,
                  product_names,
                  output_fnames):

    import xarray
    prod_xarray = xarray.Dataset()

    from geoips2.dev.utils import copy_standard_metadata
    copy_standard_metadata(xarray_obj, prod_xarray)
    for product_name in product_names:
        prod_xarray[product_name] = xarray_obj[product_name]

    from geoips2.interface_modules.output_formats.netcdf_xarray import write_xarray_netcdf
    for ncdf_fname in output_fnames:
        write_xarray_netcdf(prod_xarray, ncdf_fname)
    return output_fnames
