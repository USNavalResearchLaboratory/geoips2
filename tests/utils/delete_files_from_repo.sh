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

if [[ "$1" == "" ]]; then
    echo ""
    echo "Usage: $0 <repo_name>"
    echo ""
    echo "Where <repo_name> either"
    echo "    $GEOIPS2_PACKAGES_DIR/<repo_name>"
    echo "    $GEOIPS2_BASEDIR/test_data/<repo_name>"
    exit 1
fi

repo_name=$1

echo "Deleting bad files from test repos"
# Include 2 levels - some repos have a subdirectory organization.
for fname in $GEOIPS2_BASEDIR/test_data/$repo_name/outputs/*/diff_test_output*/rm_*; do source $fname; done
for fname in $GEOIPS2_BASEDIR/test_data/$repo_name/outputs/*/*/diff_test_output*/rm_*; do source $fname; done

for fname in $GEOIPS2_PACKAGES_DIR/$repo_name/tests/outputs/*/diff_test_output*/rm_*; do source $fname; done
for fname in $GEOIPS2_PACKAGES_DIR/$repo_name/tests/outputs/*/*/diff_test_output*/rm_*; do source $fname; done

# Get rid of all the comparison files in preparation for commiting new/removed/modified files
$GEOIPS2_PACKAGES_DIR/geoips2/tests/utils/delete_diff_dirs.sh $repo_name

echo "Now go to the individual "
echo "    $GEOIPS2_BASEDIR/test_data/$repo_name/outputs"
echo "    $GEOIPS2_PACKAGES_DIR/$repo_name/tests/outputs"
echo "directories and add/commit new/removed/modified files"
