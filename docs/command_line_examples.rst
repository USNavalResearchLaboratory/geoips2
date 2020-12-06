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

Example Command Line Calls
==================================

The amsr2 test data repository contains sample data for producing representative GeoIPS 2.0 product output.

.. code-block:: bash
    :linenos:

    source $HOME/satproc/geoips2_modules/geoips2/setup/config_geoips2

    # Obtain test data repo for functionality test
    cd $GEOIPS2_BASEDIR
    ### Request test data repo from geoips@nrlmry.navy.mil

    cd $GEOIPS2_BASEDIR/geoips_test_data_amsr2


Geostationary VIS/IR imagery
---------------------------------

Geostationary visible and IR processing (from AHI, ABI, or SEVIRI), produces both standalone imagery products as
well as intermediate data files.  The intermediate data files can then be used for future fused products.

Note the first time processing ABI or AHI data can take several minutes, as it is pre-generating geolocation files
to cache for use in subsequent runs.

.. code-block:: bash
    :linenos:

    python $GEOIPS2_MODULES_DIR/geoips2/commandline/run_driver.py \
                      bg_data/ahi_20200518_0740/* \
                      --driver visir_driver \
                      --readername ahi_hsd \
                      --sectorfiles sectors/2020051806_IO01.yaml \
                      -s tc2020io01amphan

.. image:: images/20200518_074000_IO012020_ahi_himawari8_Infrared-Gray_140kts_100p00_1p0.png
   :width: 600


Passive Microwave 89H and 37H imagery
-------------------------------------

89H and 37H products plot the individual 89GHz and 37GHz AMSR2 channels - including:
    * "clean" png with no mapping or title information,
    * annotated png using cartopy and matplotlib
    * METOCTIFF tif image with appropriate mtif headers.
    * associated metadata YAML files

.. code-block:: bash
    :linenos:

    python $GEOIPS2_MODULES_DIR/geoips2/commandline/run_driver.py
                      data/20200518.062048.*.mbt.*.nc \
                      --driver pmw_tbs \
                      --readername amsr2_ncdf \
                      --sectorfiles sectors/2020051806_IO01.yaml \
                      -s tc2020io01amphan
                      -p 89H 37H

.. image:: images/20200518_073601_IO012020_amsr2_gcom-w1_89H_140kts_99p73_1p0.png
   :width: 600

Passive Microwave 89pct and 37pct imagery
-----------------------------------------

89pct and 37pct products plot include combinations of multiple channels into a single channel output array.
    * "clean" png with no mapping or title information,
    * annotated png using cartopy and matplotlib
    * METOCTIFF tif image with appropriate mtif headers.
    * associated metadata YAML files

.. code-block:: bash
    :linenos:

    python $GEOIPS2_MODULES_DIR/geoips2/commandline/run_driver.py \
                      data/20200518.062048.*.mbt.*.nc \
                      --driver pmw_tbs \
                      --readername amsr2_ncdf \
                      --sectorfiles sectors/2020051806_IO01.yaml \
                      -s tc2020io01amphan
                      -p 89pct 37pct

.. image:: images/20200518_073601_IO012020_amsr2_gcom-w1_89pct_140kts_28p31_1p0.png
   :width: 600


Passive Microwave color89 and color37 imagery
---------------------------------------------

color89 and color37 products include multiple channels into a RGB output array
    * "clean" png with no vis/ir overlay, mapping, or title information,
    * annotated png using cartopy and matplotlib
    * METOCTIFF tif image with appropriate mtif headers.
    * associated metadata YAML files

.. code-block:: bash
    :linenos:

    python $GEOIPS2_MODULES_DIR/geoips2/commandline/run_driver.py \
                      data/20200518.062048.*.mbt.*.nc \
                      --driver pmw_tbs \
                      --readername amsr2_ncdf \
                      --sectorfiles sectors/2020051806_IO01.yaml \
                      -s tc2020io01amphan
                      -p color89 color37

.. image:: images/20200518_073601_IO012020_amsr2_gcom-w1_color89_140kts_99p73_1p0.png
   :width: 600
