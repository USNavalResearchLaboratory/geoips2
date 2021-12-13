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


def tc_storm_basedir(basedir, tc_year, tc_basin, tc_stormnum):
    ''' Produce base storm directory for TC web output

    Args:
        basedir (str) :  base directory
        tc_year (int) :  Full 4 digit storm year
        tc_basin (str) :  2 character basin designation
                               SH Southern Hemisphere
                               WP West Pacific
                               EP East Pacific
                               CP Central Pacific
                               IO Indian Ocean
                               AL Atlantic
        tc_stormnum (int) : 2 digit storm number
                               90 through 99 for invests
                               01 through 69 for named storms
    Returns:
        (str) : Path to base storm web directory
    '''
    from os.path import join as pathjoin
    path = pathjoin(basedir,
                    'tc{0:04d}'.format(tc_year),
                    tc_basin,
                    '{0}{1:02d}{2:04d}'.format(tc_basin, tc_stormnum, tc_year))
    return path

