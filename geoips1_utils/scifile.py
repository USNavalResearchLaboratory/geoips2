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

''' Utilities for obtaining information from GeoIPS 1.0 objects and using within the geoips2 environment'''

import logging
LOG = logging.getLogger(__name__)


def xarray_from_scifile(datafile, area_def=None, dsnames=None, varnames=None, roi=None):
    ''' Create xarray dataset from existing scifile datafile object.  This includes the standard expected attributes

        Args:
            datafile (SciFile) : SciFile object with standard data / metadata fields, used to populate xarray
            dsnames (:obj:`list`, optional) : List of strings indicating desired datasets to include. Default is None,
                                              which indicates including *all* datasets.
            varnames (:obj:`list`, optional) : List of strings indicating desired variables to include. Default is None
                                              which indicates including *all* variables.
            roi (:obj:`int`, optional) : Radius of Influence for interpolation, in meters. Default is None, which
                                              results in attempting to use radius_of_influence from metadata.

        Returns:
            xarray Dataset object with attributes and variables set appropriately
    '''
    import xarray

    xarray_datasets = [xarray.Dataset()]
    for dsname in datafile.datasets.keys():
        if dsnames and dsname not in dsnames:
            continue
        for varname in datafile.datasets[dsname].variables.keys():
            if varnames and varname not in varnames:
                continue
            currvar = datafile.datasets[dsname].variables[varname]
            orig_dims = list(currvar.shape)
            for xarray_dataset in xarray_datasets:
                if len(xarray_dataset.variables.keys()) == 0 or xarray_dataset.dims.values() == orig_dims:
                    xarray_dataset[varname] = xarray.DataArray(currvar)
                    LOG.info('Added %s variable to xarray dataset dims %s', varname, xarray_dataset[varname].dims)
                    if 'timestamp' in varname:
                        from numpy import datetime64
                        xarray_dataset[varname] = (xarray_dataset[varname]*10**9).astype(datetime64)
        for varname in datafile.datasets[dsname].geolocation_variables.keys():
            if varnames and varname not in varnames:
                continue
            xvarname = varname
            if varname == 'Latitude':
                xvarname = 'latitude'
            if varname == 'Longitude':
                xvarname = 'longitude'
            currvar = datafile.datasets[dsname].geolocation_variables[varname]
            orig_dims = list(currvar.shape)
            for xarray_dataset in xarray_datasets:
                if len(xarray_dataset.variables.keys()) == 0 or xarray_dataset.dims.values() == orig_dims:
                    xarray_dataset[xvarname] = xarray.DataArray(currvar)
                    LOG.info('Added %s variable to xarray dataset dims %s', xvarname, xarray_dataset[xvarname].dims)

    for xarray_dataset in xarray_datasets:
        xarray_dataset.attrs['start_datetime'] = datafile.start_datetime
        xarray_dataset.attrs['end_datetime'] = datafile.end_datetime
        xarray_dataset.attrs['source_name'] = datafile.source_name
        xarray_dataset.attrs['platform_name'] = datafile.platform_name
        xarray_dataset.attrs['data_provider'] = datafile.dataprovider
        LOG.info('Added standard attributes to xarray dataset with dims %s', xarray_dataset['latitude'].dims)
    roivar = 'interpolation_radius_of_influence'
    newroi = None
    if roi:
        LOG.info('Added PASSED radius of influence %s to xarray attrs', roi)
        newroi = roi
    elif 'interpolation_radius_of_influence' in datafile.metadata['top'].keys():
        LOG.info('Added scifile READER radius of influence %s to xarray attrs', datafile.metadata['top'][roivar])
        newroi = datafile.metadata['top'][roivar]
    else:
        try:
            from geoips.utils.satellite_info import SatSensorInfo
            sensor_info = SatSensorInfo(datafile.platform_name, datafile.source_name)
            newroi = sensor_info.interpolation_radius_of_influence 
            LOG.info('Added SENSORINFO radius of influence %s to xarray attrs', newroi)
        except (KeyError, AttributeError):
            # If we are registering a non-sat dataset, SatSensorInfo is not defined, and ROI not defined.
            # so open default SatSensorInfo object (which will have default ROI)
            from geoips.utils.satellite_info import SatSensorInfo
            sensor_info = SatSensorInfo()
            newroi = sensor_info.interpolation_radius_of_influence
            LOG.info('        Using DEFAULT SATELLITE_INFO radius of influence: '+str(newroi))
            
    if area_def is not None and hasattr(area_def, 'pixel_size_x') and hasattr(area_def, 'pixel_size_y'):
        if area_def.pixel_size_x > newroi or area_def.pixel_size_y > newroi:
            LOG.info('        Using sector radius of influence: '+str(area_def.pixel_size_x*1.5)+' or '+str(area_def.pixel_size_y*1.5)+', not sensor/product: '+str(newroi))
            newroi = area_def.pixel_size_x * 1.5 if area_def.pixel_size_x > area_def.pixel_size_y else area_def.pixel_size_y * 1.5

    for xarray_dataset in xarray_datasets:
        LOG.info('        Set roi to %s for xarray_dataset with dimensions %s', newroi, xarray_dataset['latitude'].dims)
        xarray_dataset.attrs[roivar] = newroi
    return xarray_datasets
