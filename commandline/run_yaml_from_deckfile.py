# # # DISTRIBUTION STATEMENT A. Approved for public release: distribution unlimited. # # #
# # #  # # #
# # # Author: # # #
# # # Naval Research Laboratory, Marine Meteorology Division # # #
# # #  # # #
# # # This program is free software: you can redistribute it and/or modify it under # # #
# # # the terms of the NRLMMD License included with this program.  If you did not # # #
# # # receive the license, see http://www.nrlmry.navy.mil/geoips for more # # #
# # # information. # # #
# # #  # # #
# # # This program is distributed WITHOUT ANY WARRANTY; without even the implied # # #
# # # warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the # # #
# # # included license for more details. # # #

''' Command line script for converting an ATCF deck file to YAML files'''

if __name__ == '__main__':
    from geoips2.sector_utils.atcf_tracks import deckfile_to_yamlfiles
    from geoips2.commandline.log_setup import setup_logging
    from geoips2.sector_utils.atcf_tracks import get_stormyear_from_deckfilename
    from geoips2.sector_utils.atcf_tracks import get_finalstormname_from_deckfile
    from os.path import exists
    from os import makedirs
    import sys

    LOG = setup_logging()

    # storm_year = 2020
    # final_storm_name = 'GABEKILE'
    # sector_path = join('.', 'sector')
    # deck_filename = join(sector_path, 'Gsh162020.dat')
    if '.py' in sys.argv[0]:
        SCRIPT_NAME = sys.argv.pop(0)
    OUTPUT_PATH = sys.argv.pop()
    DECK_FILENAMES = sys.argv
    if not exists(OUTPUT_PATH):
        makedirs(OUTPUT_PATH, mode=0o755)

    for DECK_FILENAME in DECK_FILENAMES:
        STORM_YEAR = get_stormyear_from_deckfilename(DECK_FILENAME)
        FINAL_STORM_NAME = get_finalstormname_from_deckfile(DECK_FILENAME)

        deckfile_to_yamlfiles(DECK_FILENAME,
                              output_path=OUTPUT_PATH,
                              storm_year=STORM_YEAR,
                              final_storm_name=FINAL_STORM_NAME)
