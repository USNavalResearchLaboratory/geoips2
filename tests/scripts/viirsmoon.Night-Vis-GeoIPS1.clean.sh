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

run_procflow $GEOIPS2_BASEDIR/test_data/test_data_viirs/data/jpss/20210525/191200/VJ102DNB.A2021145.1912.002.2021146004551.nc \
             $GEOIPS2_BASEDIR/test_data/test_data_viirs/data/jpss/20210525/191200/VJ102IMG.A2021145.1912.002.2021146004551.nc \
             $GEOIPS2_BASEDIR/test_data/test_data_viirs/data/jpss/20210525/191200/VJ102MOD.A2021145.1912.002.2021146004551.nc \
             $GEOIPS2_BASEDIR/test_data/test_data_viirs/data/jpss/20210525/191200/VJ103DNB.A2021145.1912.002.2021146002749.nc \
             $GEOIPS2_BASEDIR/test_data/test_data_viirs/data/jpss/20210525/191200/VJ103IMG.A2021145.1912.002.2021146002749.nc \
             $GEOIPS2_BASEDIR/test_data/test_data_viirs/data/jpss/20210525/191200/VJ103MOD.A2021145.1912.002.2021146002749.nc \
             --procflow single_source \
             --reader_name viirs_netcdf \
             --product_name Night-Vis-GeoIPS1 \
             --compare_path "$GEOIPS2/tests/outputs/viirsmoon_<product>" \
             --output_format imagery_clean \
             --filename_format tc_clean_fname \
             --trackfile_parser bdeck_parser \
             --trackfiles $GEOIPS2/tests/sectors/bio022021.dat

ss_retval=$?

exit $((ss_retval))
