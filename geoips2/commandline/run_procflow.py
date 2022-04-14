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

''' Command line script for kicking off geoips2 based procflows. MUST call with --procflow'''


def main():
    ''' Script to kick off processing based on command line args '''
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

    import sys
    LOG.info('COMMANDLINE CALL: \n    %s', '\n        '.join([currarg+' \\' for currarg in sys.argv]))
   

    COMMAND_LINE_ARGS = ARGS.__dict__
    # LOG.info(COMMAND_LINE_ARGS)
    from geoips2.dev.procflow import get_procflow
    LOG.info('GETTING PROCFLOW MODULE')
    PROCFLOW = get_procflow(COMMAND_LINE_ARGS['procflow'])

    LOG.info('CALLING PROCFLOW MODULE')
    if PROCFLOW:
        RETVAL = PROCFLOW(COMMAND_LINE_ARGS['filenames'], COMMAND_LINE_ARGS)
        LOG.info('Completed geoips2 PROCFLOW %s processing, done!', COMMAND_LINE_ARGS['procflow'])
        LOG.info('Starting time: %s', DATETIMES['start'])
        LOG.info('Ending time: %s', datetime.utcnow())
        LOG.info('Total time: %s', datetime.utcnow() - DATETIMES['start'])
        if isinstance(RETVAL, list):
            for ret in RETVAL:
                LOG.info('GEOIPS2PROCFLOWSUCCESS %s', ret)
            if len(RETVAL) > 2:
                LOG.info('GEOIPS2TOTALSUCCESS %s %s products generated, total time %s',
                         str(COMMAND_LINE_ARGS['sectorfiles']), len(RETVAL), datetime.utcnow() - DATETIMES['start'])
            else:
                LOG.info('GEOIPS2NOSUCCESS %s %s products generated, total time %s',
                         str(COMMAND_LINE_ARGS['sectorfiles']), len(RETVAL), datetime.utcnow() - DATETIMES['start'])
            sys.exit(0)
        # LOG.info('Return value: %s', bin(RETVAL))
        LOG.info('Return value: %d', RETVAL)
        sys.exit(RETVAL)

    else:
        raise IOError('FAILED no geoips2*/{0}.py with def {0}'.format(COMMAND_LINE_ARGS['procflow']))


if __name__ == '__main__':
    main()
