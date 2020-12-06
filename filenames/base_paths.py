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

''' Collection of base path names used throughout GeoIPS.  Everything defaults to subdirectories relative to
    the REQUIRED environment variable GEOIPS_OUTDIRS.  Individual GEOIPS_OUTDIRS relative paths can be overridden
    by setting appropriate environment variables. '''


# Python Standard Libraries
import logging
from os import getenv, listdir
from os.path import exists, dirname, join as pathjoin, split as pathsplit
import socket

LOG = logging.getLogger(__name__)

PATHS = {}

PATHS['GEOIPS_OPERATIONAL_USER'] = False
if getenv('GEOIPS_OPERATIONAL_USER'):
    PATHS['GEOIPS_OPERATIONAL_USER'] = getenv('GEOIPS_OPERATIONAL_USER')

# At a minimum, GEOIPS_OUTDIRS must be defined.
PATHS['GEOIPS_OUTDIRS'] = getenv('GEOIPS_OUTDIRS')
if not PATHS['GEOIPS_OUTDIRS']:
    raise KeyError('GEOIPS_OUTDIRS must be set in your environment.  Please set GEOIPS_OUTDIRS and try again')

# If GEOIPS is not defined, we must have a system install.
# Set GEOIPS to current path (get rid of utils/plugin_paths.py)
PATHS['GEOIPS'] = getenv('GEOIPS')
if not getenv('GEOIPS'):
    PATHS['GEOIPS'] = pathjoin(pathsplit(dirname(__file__))[0], '..')

PATHS['GEOIPS2'] = getenv('GEOIPS2')
if not getenv('GEOIPS2'):
    PATHS['GEOIPS2'] = pathjoin(pathsplit(dirname(__file__))[0], '..', '..')

PATHS['GEOIPS2_MODULES'] = ['geoips2']
if getenv('GEOIPS2_MODULES_DIR') and exists(getenv('GEOIPS2_MODULES_DIR')):
    PATHS['GEOIPS2_MODULES'] = listdir(getenv('GEOIPS2_MODULES_DIR'))

# Location for writing out presectored data files, but unregistered
if getenv('PRESECTORED_DATA_PATH'):
    PATHS['PRESECTORED_DATA_PATH'] = getenv('PRESECTORED_DATA_PATH')
else:
    PATHS['PRESECTORED_DATA_PATH'] = pathjoin(PATHS['GEOIPS_OUTDIRS'], 'preprocessed', 'sectored')

# Location for writing out preread, but unsectored/registered, data files
if getenv('PREREAD_DATA_PATH'):
    PATHS['PREREAD_DATA_PATH'] = getenv('PREREAD_DATA_PATH')
else:
    PATHS['PREREAD_DATA_PATH'] = pathjoin(PATHS['GEOIPS_OUTDIRS'], 'preprocessed', 'unsectored')

# Location for writing out preregistered data files, but no algorithms applied
if getenv('PREREGISTERED_DATA_PATH'):
    PATHS['PREREGISTERED_DATA_PATH'] = getenv('PREREGISTERED_DATA_PATH')
else:
    PATHS['PREREGISTERED_DATA_PATH'] = pathjoin(PATHS['GEOIPS_OUTDIRS'], 'preprocessed', 'registered')

# Location for writing out precalculated data files (algorithms applied)
if getenv('PRECALCULATED_DATA_PATH'):
    PATHS['PRECALCULATED_DATA_PATH'] = getenv('PRECALCULATED_DATA_PATH')
else:
    PATHS['PRECALCULATED_DATA_PATH'] = pathjoin(PATHS['GEOIPS_OUTDIRS'], 'preprocessed', 'algorithms')

# Location for writing out pregenerated geolocation netcdf files
if getenv('PREGENERATED_GEOLOCATION_PATH'):
    PATHS['PREGENERATED_GEOLOCATION_PATH'] = getenv('PREGENERATED_GEOLOCATION_PATH')
else:
    PATHS['PREGENERATED_GEOLOCATION_PATH'] = pathjoin(PATHS['GEOIPS_OUTDIRS'], 'preprocessed', 'geolocation')

# GEOIPS_COPYRIGHT determines what organization name displays in imagery titles, etc.
PATHS['GEOIPS_COPYRIGHT'] = 'NRL-Monterey'
if getenv('GEOIPS_COPYRIGHT'):
    PATHS['GEOIPS_COPYRIGHT'] = getenv('GEOIPS_COPYRIGHT')

PATHS['GEOIPS_RCFILE'] = ''
if getenv('GEOIPS_RCFILE'):
    PATHS['GEOIPS_RCFILE'] = getenv('GEOIPS_RCFILE')

PATHS['ATCF_TEMPLATE'] = pathjoin(PATHS['GEOIPS'], 'geoips', 'sectorfiles', 'dynamic', 'template_atcf_sectors.xml')
if getenv('ATCF_TEMPLATE'):
    PATHS['ATCF_TEMPLATE'] = getenv('ATCF_TEMPLATE')

PATHS['DEFAULT_QUEUE'] = None
if getenv('DEFAULT_QUEUE'):
    PATHS['DEFAULT_QUEUE'] = getenv('DEFAULT_QUEUE')

PATHS['BOXNAME'] = socket.gethostname()
PATHS['HOME'] = getenv('HOME')
if not getenv('HOME'):
    # Windows
    PATHS['HOME'] = getenv('HOMEDRIVE')+getenv('HOMEPATH')

PATHS['SCRATCH'] = getenv('SCRATCH')
if not getenv('SCRATCH'):
    PATHS['SCRATCH'] = pathjoin(getenv('GEOIPS_OUTDIRS'), 'scratch')
PATHS['LOCALSCRATCH'] = getenv('LOCALSCRATCH')
if not getenv('LOCALSCRATCH'):
    PATHS['LOCALSCRATCH'] = PATHS['SCRATCH']
PATHS['SHAREDSCRATCH'] = getenv('SHAREDSCRATCH')
if not getenv('SHAREDSCRATCH'):
    PATHS['SHAREDSCRATCH'] = PATHS['SCRATCH']

# SATOPS is the default intermediate and ancillary data location.
PATHS['SATOPS'] = getenv('SATOPS')
if not getenv('SATOPS'):
    PATHS['SATOPS'] = pathjoin(getenv('GEOIPS_OUTDIRS'), 'satops')

# This is the default ANCILDATDIR specified in $GEOIPS/geoips/geoalgs/Makefile
# These MUST match or geoalgs won't find ancildat files (ANCILDATDIR gets built into fortran
# routines).
# Used to be $GEOIPS/geoips/geoalgs/dat, but decided it shouldn't be relative to
# source by default...
# Also note I added GEOALGSAUTOGENDATA - these were going directly in ancildat previously, which
# can get rather crowded with TCs and other dynamic sectors.  Also, separating the auto-generated
# files from the source files allows for individual users to read from the shared ancildat, and write to
# their own auto-generated location
if not getenv('ANCILDATDIR'):
    PATHS['ANCILDATDIR'] = pathjoin(PATHS['SATOPS'], 'longterm_files', 'ancildat')
    PATHS['ANCILDATAUTOGEN'] = pathjoin(PATHS['SATOPS'], 'longterm_files', 'ancildat_autogen')
else:
    PATHS['ANCILDATDIR'] = getenv('ANCILDATDIR')
    PATHS['ANCILDATAUTOGEN'] = pathjoin(getenv('ANCILDATDIR'), 'autogen')

PATHS['LOGDIR'] = getenv('LOGDIR')
if not getenv('LOGDIR'):
    PATHS['LOGDIR'] = pathjoin(PATHS['GEOIPS_OUTDIRS'], 'logs')

PATHS['GEOIPSDATA'] = getenv('GEOIPSDATA')
if not getenv('GEOIPSDATA'):
    PATHS['GEOIPSDATA'] = pathjoin(PATHS['GEOIPS_OUTDIRS'], 'geoips2data')


PATHS['GEOIPSTEMP'] = getenv('GEOIPSTEMP')
if not getenv('GEOIPSTEMP'):
    PATHS['GEOIPSTEMP'] = pathjoin(PATHS['SATOPS'], 'intermediate_files', 'GeoIPStemp')
PATHS['GEOIPSFINAL'] = getenv('GEOIPSFINAL')
if not getenv('GEOIPSFINAL'):
    PATHS['GEOIPSFINAL'] = pathjoin(PATHS['SATOPS'], 'intermediate_files', 'GeoIPSfinal')

PATHS['ARCHDATWWW'] = pathjoin(PATHS['GEOIPSFINAL'], 'archdatwww')
if getenv('ARCHDATWWW'):
    PATHS['ARCHDATWWW'] = getenv('ARCHDATWWW')

PATHS['TCWWW'] = pathjoin(PATHS['GEOIPSFINAL'], 'tcwww')
if getenv('TCWWW'):
    PATHS['TCWWW'] = getenv('TCWWW')

PATHS['PUBLICWWW'] = pathjoin(PATHS['GEOIPSFINAL'], 'publicwww')
if getenv('PUBLICWWW'):
    PATHS['PUBLICWWW'] = getenv('PUBLIC')

PATHS['ATCFDROPBOX'] = pathjoin(PATHS['GEOIPSFINAL'], 'for_atcf')
if getenv('ATCFDROPBOX'):
    PATHS['ATCFDROPBOX'] = getenv('ATCFDROPBOX')

PATHS['MAPROOMDROPBOX'] = pathjoin(PATHS['GEOIPS_OUTDIRS'], 'for_maproom')
if getenv('MAPROOMDROPBOX'):
    PATHS['MAPROOMDROPBOX'] = getenv('MAPROOMDROPBOX')

PATHS['ATCF_DECKS_DB'] = pathjoin(PATHS['SATOPS'], 'longterm_files', 'atcf', 'atcf_decks.db')
if getenv('ATCF_DECKS_DB'):
    PATHS['ATCF_DECKS_DB'] = getenv('ATCF_DECKS_DB')

PATHS['ATCF_DECKS_DIR'] = pathjoin(PATHS['SATOPS'], 'longterm_files', 'atcf', 'decks')
if getenv('ATCF_DECKS_DIR'):
    PATHS['ATCF_DECKS_DIR'] = getenv('ATCF_DECKS_DIR')


def make_dirs(path):
    ''' Make directories, catching exceptions if directory already exists

    Args:
        path (str) : Path to directory to create

    Returns:
        (str) : Path if successfully created
    '''
    from os import makedirs
    if not exists(path):
        try:
            LOG.info('Creating directory %s', path)
            makedirs(path, mode=0o755)
        except OSError as resp:
            LOG.warning('%s: We thought %s did not exist, but then it did. Not trying to make directory',
                        resp, path)
    return path
