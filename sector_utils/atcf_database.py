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

from geoips2.filenames.base_paths import PATHS as gpaths
from geoips2.sector_utils.atcf_tracks import TC_SECTOR_NUM_LINES
from geoips2.sector_utils.atcf_tracks import TC_SECTOR_NUM_SAMPLES
from geoips2.sector_utils.atcf_tracks import TC_SECTOR_PROJECTION
from geoips2.sector_utils.atcf_tracks import TC_SECTOR_PIXEL_WIDTH_M
from geoips2.sector_utils.atcf_tracks import TC_SECTOR_PIXEL_HEIGHT_M
import logging
LOG = logging.getLogger(__name__)

ATCF_DECKS_DB = gpaths['SATOPS']+'/longterm_files/atcf/atcf_decks.db'
ATCF_DECKS_DIR = gpaths['SATOPS']+'/longterm_files/atcf/decks'


def open_atcf_db(dbname=ATCF_DECKS_DB):
    '''Open the ATCF Decks Database, create it if it doesn't exist'''

    # Make sure the directory exists.  If the db doesn't exist,
    # the sqlite3.connect command will create it - which will
    # fail if the directory doesn't exist.
    from os.path import dirname as pathdirname
    from geoips2.filenames.base_paths import make_dirs
    make_dirs(pathdirname(dbname))

    import sqlite3
    conn = sqlite3.connect(dbname)
    conn_cursor = conn.cursor()
    # Try to create the table - if it already exists, it will just fail
    # trying to create, pass, and return the already opened db.
    try:
        conn_cursor.execute('''CREATE TABLE atcf_deck_stormfiles
            (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                filename text,
                last_updated timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
                storm_num integer,
                storm_basin text,
                start_datetime timestamp,
                start_lat real,
                start_lon real,
                start_vmax real,
                start_name real,
                vmax real,
                end_datetime timestamp)''')
        # Add in at some point?
        # storm_start_datetime timestamp,
    except sqlite3.OperationalError:
        pass
    return conn_cursor, conn


def check_db(filenames=None, process=False):
    '''filenames is a list of filenames and directories.
        if a list element is a string directory name, it expands to list of files in dir'''

    from os.path import join as pathjoin
    from os.path import dirname as pathdirname
    from glob import glob

    if filenames is None:
        filenames = glob(pathjoin(ATCF_DECKS_DIR, '*'))

    updated_files = []
    cc,conn = open_atcf_db()

    # We might want to rearrange this so we don't open up every file... Check timestamps first.
    for filename in filenames:
        updated_files += update_fields(filename, cc, conn, process=process)

    cc.execute("SELECT * FROM atcf_deck_stormfiles")
    # data = cc.fetchall()
    conn.close()
    # return data
    return updated_files


def update_fields(atcf_stormfilename, cc, conn, process=False):
    # Must be of form similar to 
    # Gal912016.dat

    import re
    from datetime import datetime, timedelta
    from os.path import basename as pathbasename
    from os import stat as osstat

    updated_files = []

    LOG.info('Checking '+atcf_stormfilename+' ... process '+str(process))

    # Check if we match Gxxdddddd.dat filename format. If not just return and don't do anything.
    if not re.compile('G\D\D\d\d\d\d\d\d\.\d\d\d\d\d\d\d\d\d\d.dat').match(pathbasename(atcf_stormfilename)) and \
       not re.compile('G\D\D\d\d\d\d\d\d\.dat').match(pathbasename(atcf_stormfilename)):
        LOG.info('')
        LOG.warning('    DID NOT MATCH REQUIRED FILENAME FORMAT, SKIPPING: '+atcf_stormfilename)
        return []

    # Get all fields for the database entry for the current filename
    cc.execute("SELECT * FROM atcf_deck_stormfiles WHERE filename = ?", (atcf_stormfilename,))
    data=cc.fetchone()

    file_timestamp = datetime.fromtimestamp(osstat(atcf_stormfilename).st_mtime)
    # Reads timestamp out as string - convert to datetime object.
    # Check if timestamp on file is newer than timestamp in database - if not, just return and don't do anything.
    if data: 
        database_timestamp = datetime.strptime(cc.execute("SELECT last_updated from atcf_deck_stormfiles WHERE filename = ?", (atcf_stormfilename,)).fetchone()[0],'%Y-%m-%d %H:%M:%S.%f')
        if file_timestamp < database_timestamp:
            LOG.info('')
            LOG.info(atcf_stormfilename+' already in '+ATCF_DECKS_DB+' and up to date, not doing anything.')
            return []

    lines = open(atcf_stormfilename,'r').readlines()
    start_line = lines[0].split(',')
    # Start 24h prior to start in sectorfile, for initial processing
    #storm_start_datetime = datetime.strptime(start_line[2],'%Y%m%d%H')
    start_datetime = datetime.strptime(start_line[2],'%Y%m%d%H') - timedelta(hours=24)
    end_datetime = datetime.strptime(lines[-1].split(',')[2],'%Y%m%d%H')
    start_vmax= start_line[8]
    vmax=0
    for line in lines:
        currv = line.split(',')[8]
        track = line.split(',')[4]
        if currv and track == 'BEST' and float(currv) > vmax:
            vmax = float(currv)

    if data and database_timestamp < file_timestamp:
        LOG.info('')
        LOG.info('Updating start/end datetime and last_updated fields for '+atcf_stormfilename+' in '+ATCF_DECKS_DB)
        old_start_datetime,old_end_datetime,old_vmax = cc.execute("SELECT start_datetime,end_datetime,vmax from atcf_deck_stormfiles WHERE filename = ?", (atcf_stormfilename,)).fetchone()
        # Eventually add in storm_start_datetime
        #old_storm_start_datetime,old_start_datetime,old_end_datetime,old_vmax = cc.execute("SELECT storm_start_datetime,start_datetime,end_datetime,vmax from atcf_deck_stormfiles WHERE filename = ?", (atcf_stormfilename,)).fetchone()
        if old_start_datetime == start_datetime.strftime('%Y-%m-%d %H:%M:%S'):
            LOG.info('    UNCHANGED start_datetime: '+old_start_datetime)
        else:
            LOG.info('    Old start_datetime: '+old_start_datetime+' to new: '+start_datetime.strftime('%Y-%m-%d %H:%M:%S'))
            updated_files += [atcf_stormfilename]
        #if old_storm_start_datetime == storm_start_datetime.strftime('%Y-%m-%d %H:%M:%S'):
        #    LOG.info('    UNCHANGED storm_start_datetime: '+old_storm_start_datetime)
        #else:
        #    LOG.info('    Old storm_start_datetime: '+old_storm_start_datetime+' to new: '+storm_start_datetime.strftime('%Y-%m-%d %H:%M:%S'))
        if old_end_datetime == end_datetime.strftime('%Y-%m-%d %H:%M:%S'):
            LOG.info('    UNCHANGED end_datetime: '+old_end_datetime)
        else:
            LOG.info('    Old end_datetime: '+old_end_datetime+' to new: '+end_datetime.strftime('%Y-%m-%d %H:%M:%S'))
            updated_files += [atcf_stormfilename]
        if database_timestamp == file_timestamp:
            LOG.info('    UNCHANGED last_updated: '+database_timestamp.strftime('%Y-%m-%d %H:%M:%S'))
        else:
            LOG.info('    Old last_updated: '+database_timestamp.strftime('%Y-%m-%d %H:%M:%S')+' to new: '+file_timestamp.strftime('%Y-%m-%d %H:%M:%S'))
            updated_files += [atcf_stormfilename]
        if old_vmax == vmax:
            LOG.info('    UNCHANGED vmax: '+str(old_vmax))
        else:
            LOG.info('    Old vmax: '+str(old_vmax)+' to new: '+str(vmax))
            updated_files += [atcf_stormfilename]
        cc.execute('''UPDATE atcf_deck_stormfiles SET 
                        last_updated=?,
                        start_datetime=?,
                        end_datetime=?,
                        vmax=? 
                      WHERE filename = ?''', 
                      #Eventually add in ?
                      #storm_start_datetime=?,
                        (file_timestamp,
                        #storm_start_datetime,
                        start_datetime,
                        end_datetime,
                        str(vmax),
                        atcf_stormfilename,))
        conn.commit()
        return updated_files

    start_lat = start_line[6]
    start_lon = start_line[7]
    storm_basin = start_line[0]
    storm_num = start_line[1]
    try:
        start_name= start_line[48]+start_line[49]
    except IndexError:
        start_name= start_line[41]

    if data == None:
        #print '    Adding '+atcf_stormfilename+' to '+ATCF_DECKS_DB
        cc.execute('''insert into atcf_deck_stormfiles(
                        filename,
                        last_updated,
                        vmax,
                        storm_num,
                        storm_basin,
                        start_datetime,
                        start_lat,
                        start_lon,
                        start_vmax,
                        start_name,
                        end_datetime) values(?, ?,?, ?,?,?,?,?,?,?,?)''', 
                        # Eventually add in ?
                        #end_datetime) values(?, ?, ?,?, ?,?,?,?,?,?,?,?)''', 
                        #storm_start_datetime,
                        (atcf_stormfilename,
                            file_timestamp,
                            str(vmax),
                            storm_num,
                            storm_basin,
                            #storm_start_datetime,
                            start_datetime,
                            start_lat,
                            start_lon,
                            start_vmax,
                            start_name,
                            end_datetime,))
        LOG.info('')
        LOG.info('    Adding '+atcf_stormfilename+' to '+ATCF_DECKS_DB) 
        updated_files += [atcf_stormfilename]
        conn.commit()

        # This ONLY runs if it is a brand new storm file and we requested 
        # processing.
        if process:
            reprocess_storm(atcf_stormfilename)
    return updated_files


def reprocess_storm(atcf_stormfilename):

    from IPython import embed as shell; shell()

    datelist = [startdt.strftime('%Y%m%d')]
    for nn in range((enddt - startdt).days + 2):
        datelist += [(startdt + timedelta(nn)).strftime('%Y%m%d')]

    hourlist = []
    for ii in range(24):
        hourlist += [(enddt-timedelta(hours=ii)).strftime('%H')]
    hourlist.sort()
    # Do newest first
    datelist.sort(reverse=True)

    for sat,sensor in [('gcom-w1','amsr2'),
                       ('gpm','gmi'),
                       ('npp','viirs'),
                       ('aqua','modis'),
                       ('terra','modis'),
                       ('himawari8','ahi'),
                       ('goesE','gvar'),
                       ('goesW','gvar')
                       ]:
        for datestr in datelist:
            process_overpass(sat,sensor,
                productlist=None,
                sectorlist=[startstormsect.name],
                sectorfiles=None,
                extra_dirs=None,
                sector_file=sector_file,
                datelist=[datestr],
                hourlist=hourlist,
                queue=os.getenv('DEFAULT_QUEUE'),
                mp_max_cpus=3,
                allstatic=False,
                alldynamic=True,
                # list=True will just list files and not actually run
                #list=True,
                list=False,
                quiet=True,
                start_datetime = startdt,
                end_datetime = enddt,
                )
    #shell()


def get_all_storms_from_db(start_datetime, end_datetime,
                           pixel_size_x=TC_SECTOR_PIXEL_WIDTH_M, pixel_size_y=TC_SECTOR_PIXEL_HEIGHT_M,
                           num_pixels_x=TC_SECTOR_NUM_SAMPLES, num_pixels_y=TC_SECTOR_NUM_LINES):
    '''Get all entries from all storms within a specific range of time from the ATCF database
        Parameters:
            start_datetime (datetime) : Start time of desired range
            end_datetime (datetime) : End time of desired range

        Returns:
            list of Sectors: List of GeoIPS 1.0 Sector objects, each storm location that falls within the desired
                             time range.

        Usage:
            >>> startdt = datetime.strptime('20200216', '%Y%m%d')
            >>> enddt = datetime.strptime('20200217', '%Y%m%d')
            >>> get_storm_from_db(startdt, enddt)
    '''
    connection_cursor, connection = open_atcf_db()
    LOG.info('connection: %s', connection)
    connection_cursor.execute('''SELECT filename from atcf_deck_stormfiles WHERE
                                 end_datetime >= ?
                                 AND start_datetime <= ?''', (start_datetime,
                                                              end_datetime))
    deck_filenames = connection_cursor.fetchall()
    return_area_defs = []
    from geoips2.sector_utils.atcf_tracks import deckfile_to_area_defs
    for deck_filename in deck_filenames:
        if deck_filename is not None:
            # Is a tuple
            deck_filename, = deck_filename
        LOG.info('deck_filename %s', deck_filename)
        area_defs = deckfile_to_area_defs(deck_filename, pixel_size_x=pixel_size_x, pixel_size_y=pixel_size_y,
                                          num_pixels_x=num_pixels_x, num_pixels_y=num_pixels_y)
        for area_def in area_defs:
            if area_def.sector_start_datetime > start_datetime and area_def.sector_start_datetime < end_datetime:
                return_area_defs+= [area_def]
    # return None if no storm matched
    return return_area_defs


def get_storm_from_db(storm_num, storm_basin, start_datetime, end_datetime):
    '''Get all entries from a specific storm within a specific range of time from the ATCF database
        Args:
            storm_num (int) : 2 digit storm number
                                   90 through 99 for invests
                                   01 through 69 for named storms
            storm_basin (str) : 2 character basin designation
                                   SH Southern Hemisphere
                                   WP West Pacific
                                   EP East Pacific
                                   CP Central Pacific
                                   IO Indian Ocean
                                   AL Atlantic
            start_datetime (datetime) : Start time of desired range
            end_datetime (datetime) : End time of desired range

        Args:
            list of Sectors: List of pyresample AreaDefinition objects, each storm location that falls within the
                             desired time range and track type.

        Usage:
            >>> startdt = datetime.strptime('20200216', '%Y%m%d')
            >>> enddt = datetime.strptime('20200217', '%Y%m%d')
            >>> get_storm_from_db(16, 'SH', startdt, enddt)
    '''
    connection_cursor, connection = open_atcf_db()
    LOG.info('connection: %s', connection)
    connection_cursor.execute('''SELECT filename from atcf_deck_stormfiles WHERE
                                 storm_num=?
                                 AND storm_basin=?
                                 AND end_datetime >= ?
                                 AND start_datetime <= ?''', (storm_num,
                                                              storm_basin,
                                                              start_datetime,
                                                              end_datetime))

    deck_filename = connection_cursor.fetchone()
    if deck_filename is not None:
        # Is a tuple
        deck_filename, = deck_filename
    return_area_defs = []
    if deck_filename is not None:
        LOG.info('deck_filename %s', deck_filename)
        area_defs = deckfile_to_area_defs(deck_filename)
        for area_def in area_defs:
            if area_def.sector_start_datetime > start_datetime and area_def.sector_start_datetime < end_datetime:
                return_area_defs+= [area_def]
        return return_area_defs
    # return None if no storm matched
    return return_area_defs
