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
# https://www.nrlmry.navy.mil/tcdat/tc2021/WP/WP022021/txt/SCT_winds_knmi_metop-c_WP02_202104210141
run_procflow $GEOIPS2_BASEDIR/test_data/test_data_scat/data/metopc_byu_uhr/210421_0142_12730_SURIGAE_210421_0000.WRave3.nc \
          --procflow single_source \
          --reader_name ascat_uhr_netcdf \
          --product_name wind-ambiguities \
          --filename_format tc_fname \
          --output_format imagery_windbarbs \
          --metadata_filename_format metadata_default_fname \
          --metadata_output_format metadata_default \
          --tc_template_yaml $GEOIPS2/geoips2/yaml_configs/sectors_dynamic/tc_web_ascatuhr_barbs_template.yaml \
          --trackfile_parser bdeck_parser \
          --trackfiles $GEOIPS2/tests/sectors/bwp022021.dat \
          --compare_path "$GEOIPS2/tests/outputs/ascat_uhr_<product>" \
          --product_params_override '{}' \
          --output_format_kwargs '{}' \
          --filename_format_kwargs '{}' \
          --metadata_output_format_kwargs '{}' \
          --metadata_filename_format_kwargs '{}'
ss_retval=$?

exit $((ss_retval))
