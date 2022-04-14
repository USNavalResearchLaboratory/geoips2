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
run_procflow $GEOIPS2_BASEDIR/test_data/test_data_gpm/data/1B.GPM.GMI.TB2016.20200917-S171519-E172017.V05A.RT-H5 \
             $GEOIPS2_BASEDIR/test_data/test_data_gpm/data/1B.GPM.GMI.TB2016.20200917-S172019-E172517.V05A.RT-H5 \
             $GEOIPS2_BASEDIR/test_data/test_data_gpm/data/1B.GPM.GMI.TB2016.20200917-S172519-E173017.V05A.RT-H5 \
             --procflow single_source \
             --reader_name gmi_hdf5 \
             --product_name 89pct \
             --filename_format tc_fname \
             --output_format imagery_clean \
             --metadata_filename_format metadata_default_fname \
             --metadata_output_format metadata_default \
             --trackfile_parser bdeck_parser \
             --trackfiles $GEOIPS2/tests/sectors/bal202020.dat \
             --compare_path "$GEOIPS2/tests/outputs/gmi_<product>" \
             --product_params_override '{"89pct": {"covg_func": "center_radius", "covg_args": {"radius_km": 300}}}' \
             --output_format_kwargs '{}' \
             --filename_format_kwargs '{}' \
             --metadata_output_format_kwargs '{}' \
             --metadata_filename_format_kwargs '{}'
ss_retval=$?

exit $((ss_retval))
