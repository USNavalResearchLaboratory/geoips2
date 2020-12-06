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

''' Test script for running representative products using data and comparison outputs from geoips_test_data_amsr2 '''

import logging
LOG = logging.getLogger(__name__)


def autotest_amsr2(fnames, command_line_args=None):
    ''' Overall template driver.  This handles reading the datafiles,
    determining appropriate sectors based on file time, then calling the appropriate products on each
    sector.

    Parameters:
        fnames (list): list of strings specifying the files on disk to process
        command_line_args (dict) : dictionary of command line arguments
                                     * Optional: 'sectorfiles': list of YAML sectorfiles
                                              * 'sectorlist': list of desired sectors found in "sectorfiles"
                                                                tc<YYYY><BASIN><NUM><NAME> for TCs,
                                                                ie tc2020sh16gabekile
                                              * 'bgfnames': List of filenames for background vis/ir imagery
                                              * 'bgreadername': Reader used for background imagery
                                              * 'comparepath': Full path to directory of comparison images
                                     * If sectorfiles and sectorlist not included, looks in database

    Returns:
        int: * 0 for successful completion (if comparepath set, successful ONLY if there are
                  no bad comparisons, missing comparisons, or missing tests).
             * Non-zero: bit error codes
                  * XYZ where
                      * X = 1 is for a bad comparison
                      * Y = 1 is for a missing comparison
                      * Z = 1 for a missing test
    '''
    output_products = []
    LOG.info('Starting AMSR2 Autotest')
    comparepaths = command_line_args['comparepaths']
    LOG.info('Importing xarray')
    import xarray

    # If background filenames are specified, preprocess the background vis/ir data
    if command_line_args['bgfnames']:
        LOG.info('Pre-processing background data')
        from geoips2.drivers.visir_driver import visir_driver
        bg_command_line_args = command_line_args.copy()
        bg_command_line_args['readername'] = command_line_args['bgreadername']
        output_products += visir_driver(command_line_args['bgfnames'], bg_command_line_args)

    from geoips2.drivers.sfc_winds import sfc_winds
    from geoips2.drivers.template_driver import template_driver
    from geoips2.drivers.pmw_tbs import pmw_tbs
        
    # Now loop through the AMSR2 filenames.  These include 3 different data types!
    #     MBT files for passive microwave processing
    #     OCEAN files for ocean surface winds data
    #     Remote Sensing Systems for ocean surface winds data from an alternative algorithm

    for fname in fnames:
        LOG.info('NEXT fname %s in autotest_amsr2.py', fname)
        xobj = xarray.open_dataset(fname)

        if 'OCEAN' in xobj.title:
            LOG.info('NEXT sfc_winds for fname %s in autotest_amsr2.py', fname)
            # All surface winds products use the same reader, so no need to specify here.
            # But, the template driver below includes ALL products, so must specify which reader to use.
            output_products += sfc_winds([fname], command_line_args)
            command_line_args['readername'] = 'sfc_winds_ncdf'
            template_files = [fname]
        elif 'MBT' in xobj.title:
            LOG.info('NEXT pmw_tbs for fname %s in autotest_amsr2.py', fname)
            # The pmw_tbs driver includes all PMW products, so must specify which reader to use.
            command_line_args['readername'] = 'amsr2_ncdf'
            output_products += pmw_tbs([fname], command_line_args)
            template_files = [fname]
        elif hasattr(xobj, 'institution') and 'Remote Sensing Systems' in xobj.institution:
            LOG.info('NEXT sfc_winds for fname %s in autotest_amsr2.py', fname)
            # All surface winds products use the same reader, so no need to specify here.
            # But, the template driver below includes ALL products, so must specify which reader to use.
            output_products += sfc_winds([fname], command_line_args)
            command_line_args['readername'] = 'sfc_winds_ncdf'
            template_files = [fname]
        else:
            LOG.info('SKIPPING Currently unsupported file type %s', fname)
            continue

        # If template products were requested command line, then produce them - must explicitly request to avoid
        # accidentally producing template products operationally...
        if command_line_args['product_options'] and 'includetemplate' in command_line_args['product_options']:
            LOG.info('NEXT template_driver for fname %s in autotest_amsr2.py', fname)
            # The template driver includes ALL products, so must specify which reader to use.
            output_products += template_driver(template_files, command_line_args)

    from os.path import basename
    LOG.info('The following products were produced from driver %s', basename(__file__))
    for output_product in output_products:
        LOG.info('    WORKFLOWSUCCESS %s', output_product)

    retval = 0
    if comparepaths:
        from geoips2.test_scripts import compare_outputs
        retval = compare_outputs(comparepaths[0], output_products)

    return retval
