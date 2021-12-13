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

''' Reader to read pre-processed data, which has been written as a geoips2 formatted netcdf
'''

# Python Standard Libraries

import logging
LOG = logging.getLogger(__name__)

reader_type = 'standard'


def geoips2_netcdf(fnames, metadata_only=False, chans=None, area_def=None, self_register=False):
    ''' Read preprocessed geoips2 netcdf output.

    All GeoIPS 2.0 readers read data into xarray Datasets - a separate
    dataset for each shape/resolution of data - and contain standard metadata information.

    Args:
        fnames (list): List of strings, full paths to files
        metadata_only (Optional[bool]):
            * DEFAULT False
            * return before actually reading data if True
        chans (Optional[list of str]):
            * NOT YET IMPLEMENTED
                * DEFAULT None (include all channels)
                * List of desired channels (skip unneeded variables as needed)
        area_def (Optional[pyresample.AreaDefinition]):
            * NOT YET IMPLEMENTED
                * DEFAULT None (read all data)
                * Specify region to read
        self_register (Optional[str]):
            * NOT YET IMPLEMENTED
                * DEFAULT False (read multiple resolutions of data)
                * register all data to the specified resolution.

    Returns:
        dict of xarray.Datasets: dict of xarray.Dataset objects with required
            Variables and Attributes: (See geoips2/docs :doc:`xarray_standards`),
            dict key can be any descriptive dataset id
            
    '''

    LOG.info('Reading files %s', fnames)

    from os.path import basename
    xarray_objs = {}
    for fname in fnames:
        xarray_objs[basename(fname)] = read_xarray_netcdf(fname)

    xarray_objs['METADATA'] = list(xarray_objs.values())[0][[]]

    return xarray_objs


def read_xarray_netcdf(ncdf_fname):
    import xarray
    from datetime import datetime
    try:
        xarray_obj = xarray.open_dataset(ncdf_fname)
    except IOError:
        raise IOError
    for attr in xarray_obj.attrs.keys():
        if 'datetime' in attr:
            xarray_obj.attrs[attr] = datetime.strptime(xarray_obj.attrs[attr], '%c')
        if attr == 'None':
            xarray_obj.attrs[attr] = None
        if attr == 'True':
            xarray_obj.attrs[attr] = True
        if attr == 'False':
            xarray_obj.attrs[attr] = False
    return xarray_obj
