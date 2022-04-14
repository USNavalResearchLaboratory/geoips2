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

# This calls the full "test_base_install.sh" script - so we ensure it is fully tested via test_all.sh
$GEOIPS2/tests/test_base_install.sh

. $GEOIPS2/tests/utils/test_all_pre.sh geoips2_all

# Do not include the calls that are in "test_base_install.sh" within this list.  They are tested above.
echo ""
# "call" used in test_all_run.sh
for call in \
            "$GEOIPS2/tests/scripts/ahi.IR-BD.imagery_clean.sh" \
            "$GEOIPS2/tests/scripts/amsr2.89H-Physical.imagery_annotated.sh" \
            "$GEOIPS2/tests/scripts/amsub_mirs.183-3H.imagery_annotated.sh" \
            "$GEOIPS2/tests/scripts/ascat_knmi.windbarbs.imagery_windbarbs_clean.sh" \
            "$GEOIPS2/tests/scripts/ascat_uhr.wind-ambiguities.imagery_windbarbs.sh" \
            "$GEOIPS2/tests/scripts/gmi.89pct.imagery_clean.sh" \
            "$GEOIPS2/tests/scripts/hy2.windspeed.imagery_annotated.sh" \
            "$GEOIPS2/tests/scripts/imerg.Rain.imagery_clean.sh" \
            "$GEOIPS2/tests/scripts/mimic.TPW_CIMSS.imagery_annotated.sh" \
            "$GEOIPS2/tests/scripts/modis.Infrared.unprojected_image.sh" \
            "$GEOIPS2/tests/scripts/oscat_knmi.windbarbs.imagery_windbarbs.sh" \
            "$GEOIPS2/tests/scripts/sar.nrcs.imagery_annotated.sh" \
            "$GEOIPS2/tests/scripts/seviri.WV-Upper.unprojected_image.sh" \
            "$GEOIPS2/tests/scripts/smap.unsectored.text_winds.sh" \
            "$GEOIPS2/tests/scripts/smos.sectored.text_winds.sh" \
            "$GEOIPS2/tests/scripts/ssmis.color89.unprojected_image.sh" \
            "$GEOIPS2/tests/scripts/viirsday.Night-Vis-IR.imagery_annotated.sh" \
            "$GEOIPS2/tests/scripts/viirsmoon.Night-Vis-GeoIPS1.clean.sh" \
            "$GEOIPS2/tests/scripts/viirsclearnight.Night-Vis-IR-GeoIPS1.unprojected_image.sh"
do
    . $GEOIPS2/tests/utils/test_all_run.sh
done

. $GEOIPS2/tests/utils/test_all_post.sh
