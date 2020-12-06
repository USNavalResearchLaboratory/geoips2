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

#!/bin/env python
''' Command line script for kicking off geoips2 based drivers. MUST call with --driver'''


if __name__ == '__main__':
    from datetime import datetime
    DATETIMES = {}
    DATETIMES['start'] = datetime.utcnow()
    from geoips2.commandline.log_setup import setup_logging
    LOG = setup_logging()

    from geoips2.commandline.args import get_command_line_args
    LOG.info('GETTING COMMAND LINE ARGUMENTS')
    # arglist=None allows all possible arguments.
    ARGS = get_command_line_args(arglist=None,
                                 description='Run data file processing')

    COMMAND_LINE_ARGS = ARGS.__dict__
    LOG.info(COMMAND_LINE_ARGS)
    from geoips2.geoips2_utils import find_module_in_geoips2_packages

    LOG.info('GETTING DRIVER MODULE')
    # arglist=None allows all possible arguments.
    DRIVER = find_module_in_geoips2_packages(module_name='drivers',
                                               method_name=COMMAND_LINE_ARGS['driver'])
    LOG.info('CALLING DRIVER MODULE')
    if DRIVER:
        RETVAL = DRIVER(COMMAND_LINE_ARGS['filenames'], COMMAND_LINE_ARGS)
        LOG.info('Completed geoips2 DRIVER processing, done!')
        LOG.info('Starting time: %s', DATETIMES['start'])
        LOG.info('Ending time: %s', datetime.utcnow())
        LOG.info('Total time: %s', datetime.utcnow() - DATETIMES['start'])
        import sys
        if isinstance(RETVAL, list):
            for ret in RETVAL:
                LOG.info('DRIVERSUCCESS %s', ret)
            sys.exit(0)
        LOG.info('Return value: %s', RETVAL)
        sys.exit(RETVAL)

    else:
        raise IOError('FAILED no geoips2*/{0}.py with def {0}'.format(COMMAND_LINE_ARGS['driver']))
