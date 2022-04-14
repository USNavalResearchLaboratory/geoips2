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

#!/bin/bash

# Default values - if you do not have this exact test case available, call with available data files / sectors.

# This exact test case required for valid comparisons - remove "compare_path" argument if running a different
# set of arguments.

run_procflow $GEOIPS2_BASEDIR/test_data/test_data_viirs/data/npp/20220211/131200/VNP02DNB.A2022042.1312.001.2022042183606.nc \
             $GEOIPS2_BASEDIR/test_data/test_data_viirs/data/npp/20220211/131200/VNP02IMG.A2022042.1312.001.2022042183606.nc \
             $GEOIPS2_BASEDIR/test_data/test_data_viirs/data/npp/20220211/131200/VNP02MOD.A2022042.1312.001.2022042183606.nc \
             $GEOIPS2_BASEDIR/test_data/test_data_viirs/data/npp/20220211/131200/VNP03DNB.A2022042.1312.001.2022042182240.nc \
             $GEOIPS2_BASEDIR/test_data/test_data_viirs/data/npp/20220211/131200/VNP03IMG.A2022042.1312.001.2022042182240.nc \
             $GEOIPS2_BASEDIR/test_data/test_data_viirs/data/npp/20220211/131200/VNP03MOD.A2022042.1312.001.2022042182240.nc \
             $GEOIPS2_BASEDIR/test_data/test_data_viirs/data/npp/20220211/131800/VNP02DNB.A2022042.1318.001.2022042183444.nc \
             $GEOIPS2_BASEDIR/test_data/test_data_viirs/data/npp/20220211/131800/VNP02IMG.A2022042.1318.001.2022042183444.nc \
             $GEOIPS2_BASEDIR/test_data/test_data_viirs/data/npp/20220211/131800/VNP02MOD.A2022042.1318.001.2022042183444.nc \
             $GEOIPS2_BASEDIR/test_data/test_data_viirs/data/npp/20220211/131800/VNP03DNB.A2022042.1318.001.2022042182210.nc \
             $GEOIPS2_BASEDIR/test_data/test_data_viirs/data/npp/20220211/131800/VNP03IMG.A2022042.1318.001.2022042182210.nc \
             $GEOIPS2_BASEDIR/test_data/test_data_viirs/data/npp/20220211/131800/VNP03MOD.A2022042.1318.001.2022042182210.nc \
             --procflow single_source \
             --reader_name viirs_netcdf \
             --product_name Night-Vis-IR-GeoIPS1 \
             --output_format unprojected_image \
             --output_format_kwargs '{"x_size": "500"}' \
             --filename_format geoips_fname \
             --compare_path "$GEOIPS2/tests/outputs/viirsclearnight_<product>" \
             --self_register_dataset 'DNB' \
             --self_register_source viirs

ss_retval=$?

exit $((ss_retval))
