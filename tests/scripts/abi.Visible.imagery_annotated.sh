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
run_procflow $GEOIPS2/tests/data/goes16_20200918_1950/* \
             --procflow single_source \
             --reader_name abi_netcdf \
             --product_name Visible \
             --compare_path "$GEOIPS2/tests/outputs/abi_static/<product>_image" \
             --output_format imagery_annotated \
             --filename_format geoips_fname \
             --resampled_read \
             --sector_list goes16 \
             --sectorfiles $GEOIPS2/tests/sectors/goes16.yaml
retval=$?

exit $retval
