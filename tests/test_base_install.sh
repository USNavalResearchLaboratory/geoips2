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

#!/bin/sh

# This should contain test calls to cover ALL required functionality tests for the geoips2 repo.

# The $GEOIPS2 tests modules sourced within this script handle:
   # setting up the appropriate associative arrays for tracking the overall return value,
   # calling the test scripts appropriately, and 
   # setting the final return value.

# Note you must use the variable "call" in the for the loop

. $GEOIPS2/tests/utils/test_all_pre.sh geoips2_base

echo ""
# "call" used in test_all_run.sh
for call in \
            "$GEOIPS2/tests/scripts/abi.config_based_output.sh" \
            "$GEOIPS2/tests/scripts/abi.Visible.imagery_annotated.sh" \
            "test_interfaces"
do
    . $GEOIPS2/tests/utils/test_all_run.sh
done

. $GEOIPS2/tests/utils/test_all_post.sh
