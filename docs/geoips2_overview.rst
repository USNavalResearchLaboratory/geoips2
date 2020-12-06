 | # # # DISTRIBUTION STATEMENT A. Approved for public release: distribution unlimited. # # #
 | # # #  # # #
 | # # # Author: # # #
 | # # # Naval Research Laboratory, Marine Meteorology Division # # #
 | # # #  # # #
 | # # # This program is free software: you can redistribute it and/or modify it under # # #
 | # # # the terms of the NRLMMD License included with this program.  If you did not # # #
 | # # # receive the license, see http://www.nrlmry.navy.mil/geoips for more # # #
 | # # # information. # # #
 | # # #  # # #
 | # # # This program is distributed WITHOUT ANY WARRANTY; without even the implied # # #
 | # # # warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the # # #
 | # # # included license for more details. # # #

GeoIPS 2.0 Overview
=========================

GeoIPS 2.0 is a collection of modules that provide generalized functionality for processing of
geolocated information - including satellite data, numerical weather prediction model output,
elevation and topography information, radar data, and other remotely sensed and in situ data.

GeoIPS 2.0 acts as a toolbox for product development - all modules are expected to have simple
inputs and outputs (Python numpy or dask arrays, dictionaries, strings, lists), to enable portability
and simplified interfacing between modules.

The general layout of the GeoIPS 2.0 module setup is as follows:

.. image:: images/geoips2_flow_chart.png
   :width: 800


:doc:`geoips2.drivers`
----------------------------------

These are high level modules that drive processing for a given data type or 
data types - input is a list of filenames, and a dictionary of command line
arguments. Drivers handle reading data (:doc:`geoips2.readers`),
and kicking off product generation (:doc:`geoips2.products`).

All drivers should have a standard call signature:

    Args: 
        * fnames (list): List of filenames to read and process
        * command_line_arguments (dictionary): Dictionary of command line arguments used in processing fnames
    
    Returns:
        * list: List of strings containing successfully produced products
           


:doc:`geoips2.readers`
--------------------------------

Data readers within GeoIPS 2.0 follow a xarray based approach. All readers should have a standard call signature, taking
a list of filenames and optional specifications for reading only a subset of the data, and should return a list of
xarray objects populated with the appropriate data, and containing standard metadata fields within the xarray
attributes.

    Args: 
        * fnames (list): List of filenames to read
        * metadata_only (Optional[bool]): DEFAULT False.
                                  * If metadata_only is True, do not read any data or calculate geolocation
        * chans (Optional[list]): Default None.
                                  * List of desired channels (skip unneeded variables as needed)
                                  * If None, include all channels.
    
    Returns:
        * list: Returns a list of xarray.Dataset objects - one Dataset for each shape/resolution of data
       

:doc:`geoips2.products`
---------------------------------

All products should have a standard call signature to enhance portability and interoperability.

Products are responsible for applying :doc:`geoips2.algorithms` to the xarray objects as needed, applying 
additional data manipulation steps from the `GeoIPS 2.0 Toolbox`_ as needed, plotting the data, and exporting imagery
or data products.


    Args:
        * xarray_objs (list): List of xarray.Dataset objects (one Dataset for each shape/resolution)
        * area_def (AreaDefinition): pyresample Area_Definition object defining the sector
    
    Returns:
        * list: List of strings containing all processing and output completed within the product call.
    '''


GeoIPS 2.0 Toolbox
-----------------------------------

The bulk of GeoIPS 2.0 is made up of various low level modules to handle data manipulation, merging,
image enhancements, and other more complex algorithms. These modules should all have simple Python inputs and outputs -
numpy ndarrays, dask arrays, strings, dictionaries, ints, floats, etc.  The backend functionality can be written in
other programming languages for efficiency, but all modules should have a simple Python interface.

We want to keep these interfaces simple to enable portability of the code, and reduce reliance on specific packages.

    * :doc:`geoips2.algorithms`
    * :doc:`geoips2.data_manipulations`
    * :doc:`geoips2.image_utils`
    * :doc:`geoips2.sector_utils`
    * :doc:`geoips2.interpolation`

