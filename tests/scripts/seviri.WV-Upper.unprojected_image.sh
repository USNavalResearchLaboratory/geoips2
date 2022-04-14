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
run_procflow $GEOIPS2_BASEDIR/test_data/test_data_seviri/data/20200404.0800_meteoIO_tc2020sh24irondro/H-000-MSG1__-MSG1_IODC___-_________-EPI______-202004040800-__ \
             $GEOIPS2_BASEDIR/test_data/test_data_seviri/data/20200404.0800_meteoIO_tc2020sh24irondro/H-000-MSG1__-MSG1_IODC___-_________-PRO______-202004040800-__ \
             $GEOIPS2_BASEDIR/test_data/test_data_seviri/data/20200404.0800_meteoIO_tc2020sh24irondro/H-000-MSG1__-MSG1_IODC___-WV_062___-000001___-202004040800-C_ \
             $GEOIPS2_BASEDIR/test_data/test_data_seviri/data/20200404.0800_meteoIO_tc2020sh24irondro/H-000-MSG1__-MSG1_IODC___-WV_062___-000002___-202004040800-C_ \
             $GEOIPS2_BASEDIR/test_data/test_data_seviri/data/20200404.0800_meteoIO_tc2020sh24irondro/H-000-MSG1__-MSG1_IODC___-WV_062___-000003___-202004040800-C_ \
             $GEOIPS2_BASEDIR/test_data/test_data_seviri/data/20200404.0800_meteoIO_tc2020sh24irondro/H-000-MSG1__-MSG1_IODC___-WV_062___-000004___-202004040800-C_ \
             $GEOIPS2_BASEDIR/test_data/test_data_seviri/data/20200404.0800_meteoIO_tc2020sh24irondro/H-000-MSG1__-MSG1_IODC___-WV_062___-000005___-202004040800-C_ \
             $GEOIPS2_BASEDIR/test_data/test_data_seviri/data/20200404.0800_meteoIO_tc2020sh24irondro/H-000-MSG1__-MSG1_IODC___-WV_062___-000006___-202004040800-C_ \
             $GEOIPS2_BASEDIR/test_data/test_data_seviri/data/20200404.0800_meteoIO_tc2020sh24irondro/H-000-MSG1__-MSG1_IODC___-WV_062___-000007___-202004040800-C_ \
             $GEOIPS2_BASEDIR/test_data/test_data_seviri/data/20200404.0800_meteoIO_tc2020sh24irondro/H-000-MSG1__-MSG1_IODC___-WV_062___-000008___-202004040800-C_ \
             --procflow single_source \
             --reader_name seviri_hrit \
             --product_name WV-Upper \
             --output_format unprojected_image \
             --output_format_kwargs '{"x_size": "1000", "y_size": "1000"}' \
             --filename_format geoips_fname \
             --compare_path "$GEOIPS2/tests/outputs/seviri_<product>" \
             --self_register_dataset 'FULL_DISK' \
             --self_register_source seviri
retval=$?

exit $retval
