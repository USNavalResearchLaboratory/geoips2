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

''' Test script for running representative products using data and comparison outputs from geoips_test_data_smap '''

import logging
LOG = logging.getLogger(__name__)


def autotest_amsub(fnames, command_line_args=None):
    ''' Pass through script to take command line arguments, and create calls to all SMAP drivers

    Args:
        fnames (list): list of strings specifying the files on disk to process
        command_line_args (dict) : dictionary of command line arguments
                                     Optional: 'sectorfiles': list of YAML sectorfiles
                                               'sectorlist': list of desired sectors found in "sectorfiles"
                                                                tc<YYYY><BASIN><NUM><NAME> for TCs,
                                                                ie tc2020sh16gabekile
                                               'comparepath': Full path to directory of comparison images
                                     If sectorfiles and sectorlist not included, drivers will look in database

    Returns:
        (int) - 0 for successful completion (if comparepath sent, successful ONLY if there are
                    no bad comparisons, missing comparisons, or missing tests).
                Non-zero: bit error codes
                    WXYZ where W = 1 is for a bad comparison
                               X = 1 is for one or more missing comparison products
                               Y = 1 for on or more missing tests
                               Z = 1 for one or more missing current products
    '''
    output_products = []
    comparepaths = command_line_args['comparepaths']
    from geoips2.drivers.pmw_tbs import pmw_tbs
    from geoips2.drivers.template_driver import template_driver
    for fname in fnames:
        command_line_args['readername'] = 'amsub_hdf'

        # If template products were requested command line, then produce them - must explicitly request to avoid
        # accidentally producing template products operationally...
        if command_line_args['product_options'] and 'includetemplate' in command_line_args['product_options']:
            # The template driver includes ALL products, so must specify which reader to use.
            output_products += template_driver([fname], command_line_args)

        output_products += pmw_tbs([fname], command_line_args)

    from os.path import basename
    LOG.info('The following products were produced from driver %s', basename(__file__))
    for output_product in output_products:
        LOG.info('    WORKFLOWSUCCESS %s', output_product)

    retval = 0
    if comparepaths:
        from geoips2.test_scripts import compare_outputs
        retval = compare_outputs(comparepaths[0], output_products)

    return retval
