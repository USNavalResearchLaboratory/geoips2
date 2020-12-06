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

Xarray and NetCDF Metadata Standards
======================================

All GeoIPS 2.0 readers read data into xarray Datasets - a separate dataset for each shape/resolution
of data - and contain standard metadata information for standardized processing.

Xarray Standard Variables
-------------------------

Internal to GeoIPS 2.0, our xarray standards include the following variables for 
automated temporal and spatial sectoring.

* 'latitude' - REQUIRED 2d array the same shape as data variables
* 'longitude' - REQUIRED 2d array the same shape as data variables
* 'timestamp' - OPTIONAL 2d array the same shape as data variables

*NOTE: Additional methods of storing spatial and temporal information
will be implemented in the future for efficiency, but currently latitude
and longitude arrays are strictly required, and timestamp array is required
for automated temporal sectoring*

Xarray Standard Attributes
--------------------------

The following standard attributes are used internally to GeoIPS 2.0 for consistent
generation of titles, legends, regridding, etc

* 'source_name' - REQUIRED
* 'platform_name' - REQUIRED
* 'data_provider' - REQUIRED
* 'start_datetime' - REQUIRED
* 'end_datetime' - REQUIRED
* 'interpolation_radius_of_influence' - REQUIRED
                                        used for pyresample-based interpolation

The following optional attributes can be used within processing if available.

* 'original_source_filename'
* 'filename_datetime'
* 'minimum_coverage' - OPTIONAL
                       if specified, products will not be generated with
                       coverage < minimum_coverage
* 'sample_distance_km' - OPTIONAL
                         if specified, sample_distance_km can be used to produce
                         a "minimum" sized image.  Web images are often up sampled to
                         provide a conveniently sized image for viewing with titles/legends,
                         this allows producing minimal sized "clean" imagery for overlaying
                         in external viewers (such as the Automated Tropical Cyclone
                         Forecasting System)


NetCDF CF Standards
--------------------------
All additional attributes should follow the **NetCDF Climate and Forecast (CF) Conventions**.

Names of individual products and variables in output NetCDF files should use **CF Standard Names** when available:

* http://cfconventions.org/Data/cf-standard-names/76/build/cf-standard-name-table.html

Attributes and metadata on output NetCDF files should follow the **CF Metadata Conventions**

* http://cfconventions.org/Data/cf-conventions/cf-conventions-1.8/cf-conventions.html
