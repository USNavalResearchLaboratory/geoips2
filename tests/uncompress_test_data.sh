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

out_path=$GEOIPS2/tests/outputs

# Ensure netcdf output files are gunzipped
    date -u
    if ls $out_path/*/*.gz >& /dev/null; then
        echo "gunzip output files $out_path/*/*.gz"
        gunzip -f $out_path/*/*.gz
    fi
