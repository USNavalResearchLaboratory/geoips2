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

run_procflow $GEOIPS2/tests/data/goes16_20200918_1950/* \
          --procflow single_source \
          --reader_name abi_netcdf \
          --product_name Infrared \
          --compare_paths "$GEOIPS2/tests/outputs/abi_static/<product>_image" \
         --output_format imagery_annotated \
         --filename_format geoips_fname \
         --sector_list goes16 \
         --sectorfiles $GEOIPS2/tests/sectors/goes16.yaml
retval=$?

exit $retval
