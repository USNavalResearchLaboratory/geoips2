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

''' General high level utilities for geoips2 processing '''

import logging
LOG = logging.getLogger(__name__)


def output_process_times(process_datetimes, num_jobs=None):
    ''' Output process times stored within the process_datetimes dictionary
    Args:
        process_datetimes (dict) : dictionary formatted as follows:
            process_datetimes['overall_start'] - overall start datetime of the entire script
            process_datetimes['overall_end'] - overall end datetime of the entire script
            process_datetimes[process_name]['start'] - start time of an individual process
            process_datetimes[process_name]['end'] - end time of an individual process
    '''

    if 'overall_end' in process_datetimes and 'overall_start' in process_datetimes:
        LOG.info('Total Time GeoIPS 2: %s Num jobs: %s',
                 process_datetimes['overall_end'] - process_datetimes['overall_start'],
                 num_jobs)
    for process_name in process_datetimes.keys():
        if process_name in ['overall_start', 'overall_end']:
            continue
        if 'end' in process_datetimes[process_name]:
            LOG.info('    SUCCESS Process Time GeoIPS 2 Sector %-20s: %s',
                     process_name,
                     process_datetimes[process_name]['end'] - process_datetimes[process_name]['start'])
        elif 'fail' in process_datetimes[process_name]:
            LOG.info('    FAILED  Process Time GeoIPS 2 Sector %-20s: %s',
                     process_name,
                     process_datetimes[process_name]['fail'] - process_datetimes[process_name]['start'])
        else:
            LOG.info('    MISSING Process Time GeoIPS 2 Sector %s', process_name)



def find_module_in_geoips2_packages(module_name, method_name):
    ''' Given 'module_name' and 'method_name', find matching module within GEOIPS2 packages

    Args:
        module_name (str) : module name to look for,
                                ie from geoips2.<module_name>.<method_name> import <method_name>
        method_name (str) : method name to look for,
                                ie from geoips2.<module_name>.<method_name> import <method_name>

    Returns:
        (module) : Actual callable Python module found within any available geoips2 packages
    '''
    from geoips2.filenames.base_paths import PATHS as gpaths
    from importlib import import_module
    module = None
    for package_name in gpaths['GEOIPS2_MODULES']:
        try:
            module = getattr(import_module('{0}.{1}.{2}'.format(package_name,
                                                                module_name,
                                                                method_name)),
                             method_name)
            LOG.info('Using %s %s from %s.', module, module_name, package_name)
        except (ImportError, AttributeError, TypeError) as resp:
            # This will be a different missing package within the desired module. Make sure we raise it.
            if module_name not in str(resp) and method_name not in str(resp):
                raise
            LOG.info('No %s %s in module %s, trying next package',
                     module_name, method_name, package_name)
    return module
