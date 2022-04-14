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
run_procflow $GEOIPS2_BASEDIR/test_data/test_data_gpm/data/3B-HHR-L.MS.MRG.3IMERG.20200917-S170000-E172959.1020.V06B.RT-H5 \
          --procflow single_source \
          --reader_name imerg_hdf5 \
          --product_name Rain \
          --filename_format tc_fname \
          --output_format imagery_clean \
          --trackfile_parser bdeck_parser \
          --trackfiles $GEOIPS2/tests/sectors/bal202020.dat \
          --compare_path "$GEOIPS2/tests/outputs/imerg_<product>"
ss_retval=$?

exit $((ss_retval))
