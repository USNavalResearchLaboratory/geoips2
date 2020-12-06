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

def remove_duplicates(fnames, area_def, remove_files=False):
    removed_files = []
    saved_files = []
    from geoips2.sector_utils.utils import is_sector_type
    from geoips2.filenames.atcf_filenames import atcf_web_filename_remove_duplicates
    from geoips2.filenames.atcf_filenames import metoctiff_filename_remove_duplicates
    from geoips2.filenames.old_tcweb_fnames import old_tcweb_fnames_remove_duplicates
    from geoips2.filenames.product_filenames import standard_geoips_filename_remove_duplicates
    for fname in fnames:
        if is_sector_type(area_def, 'atcf'):

            curr_removed_files, curr_saved_files = atcf_web_filename_remove_duplicates(fname,
                                                                                       remove_files=remove_files)
            removed_files += curr_removed_files
            saved_files += curr_saved_files

            curr_removed_files, curr_saved_files = old_tcweb_fnames_remove_duplicates(fname,
                                                                                      remove_files=remove_files)
            removed_files += curr_removed_files
            saved_files += curr_saved_files

            curr_removed_files, curr_saved_files = metoctiff_filename_remove_duplicates(fname,
                                                                                        remove_files=remove_files)
            removed_files += curr_removed_files
            saved_files += curr_saved_files

        else:

            curr_removed_files, curr_saved_files = standard_geoips_filename_remove_duplicates(fname,
                                                                                              remove_files=remove_files)
            removed_files += curr_removed_files
            saved_files += curr_saved_files
        # from IPython import embed as shell; shell()

    return removed_files, saved_files


