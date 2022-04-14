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
run_procflow ${GEOIPS2_BASEDIR}/test_data/test_data_smos/data/SM_OPER_MIR_SCNFSW_20200216T120839_20200216T135041_110_001_7.nc \
             --procflow single_source \
             --reader_name smos_winds_netcdf \
             --product_name sectored \
             --filename_format text_winds_tc_fname \
             --output_format text_winds \
             --trackfile_parser bdeck_parser \
             --trackfiles $GEOIPS2/tests/sectors/bsh162020.dat \
             --compare_path "$GEOIPS2/tests/outputs/smos_<product>"
ss_retval=$?

exit $((ss_retval))
