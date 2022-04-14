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

run_procflow $GEOIPS2_BASEDIR/test_data/test_data_viirs/data/jpss/20210209/073600/VJ102DNB.A2021040.0736.002.2021040145245.nc \
             $GEOIPS2_BASEDIR/test_data/test_data_viirs/data/jpss/20210209/073600/VJ102MOD.A2021040.0736.002.2021040145245.nc \
             $GEOIPS2_BASEDIR/test_data/test_data_viirs/data/jpss/20210209/073600/VJ103DNB.A2021040.0736.002.2021040142228.nc \
             $GEOIPS2_BASEDIR/test_data/test_data_viirs/data/jpss/20210209/073600/VJ103MOD.A2021040.0736.002.2021040142228.nc \
             $GEOIPS2_BASEDIR/test_data/test_data_viirs/data/jpss/20210209/074200/VJ102DNB.A2021040.0742.002.2021040143010.nc \
             $GEOIPS2_BASEDIR/test_data/test_data_viirs/data/jpss/20210209/074200/VJ102MOD.A2021040.0742.002.2021040143010.nc \
             $GEOIPS2_BASEDIR/test_data/test_data_viirs/data/jpss/20210209/074200/VJ103DNB.A2021040.0742.002.2021040140938.nc \
             $GEOIPS2_BASEDIR/test_data/test_data_viirs/data/jpss/20210209/074200/VJ103MOD.A2021040.0742.002.2021040140938.nc \
             --procflow single_source \
             --reader_name viirs_netcdf \
             --product_name Night-Vis-IR \
             --filename_format tc_fname \
             --output_format imagery_annotated \
             --boundaries_params tc_visir \
             --gridlines_params tc_visir \
             --metadata_filename_format metadata_default_fname \
             --metadata_output_format metadata_default \
             --trackfile_parser bdeck_parser \
             --trackfiles $GEOIPS2/tests/sectors/bsh192021.dat \
             --compare_path "$GEOIPS2/tests/outputs/viirsday_<product>" \
             --product_params_override '{}' \
             --output_format_kwargs '{}' \
             --filename_format_kwargs '{}' \
             --metadata_output_format_kwargs '{}' \
             --metadata_filename_format_kwargs '{}'
ss_retval=$?

exit $((ss_retval))
