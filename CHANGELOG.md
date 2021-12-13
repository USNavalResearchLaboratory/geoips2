#### # # DISTRIBUTION STATEMENT A. Approved for public release: distribution unlimited.
#### # # 
#### # # Author:
#### # # Naval Research Laboratory, Marine Meteorology Division
#### # # 
#### # # This program is free software: you can redistribute it and/or modify it under
#### # # the terms of the NRLMMD License included with this program.  If you did not
#### # # receive the license, see http://www.nrlmry.navy.mil/geoips for more
#### # # information.
#### # # 
#### # # This program is distributed WITHOUT ANY WARRANTY; without even the implied
#### # # warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#### # # included license for more details.


# v1.3.0: 2021-11-24, atcf->tc, remove "satops"

### Breaking Interface Changes
    * Replaced instances of "atcf" within geoips2 repo with "tc"
        * --atcfdb command line option with --tcdb
        * --get_atcf_area_defs_for_xarray -> get_tc_area_defs_for_xarray
        * "atcf" -> "tc" sector_type 
    * Removed support for SATOPS, GEOIPSFINAL, and GEOIPSTEMP environment variables / base_paths
        * GEOIPSFINAL -> ANNOTATED_IMAGERY_PATH
        * GEOIPSTEMP -> CLEAN_IMAGERY_PATH
        * PREGENERATED_IMAGERY_PATH -> CLEAN_IMAGERY_PATH
    * Moved "geoips_outdirs/satops" subdirectories into "geoips_outdirs"
        * geoips_outdirs/satops/intermediate_files/GeoIPSfinal -> geoips_outdirs/preprocessed/annotated_imagery
        * geoips_outdirs/satops/intermediate_files/GeoIPStemp -> geoips_outdirs/preprocessed/clean_imagery
        * geoips_outdirs/satops/longterm_files -> geoips_outdirs/longterm_files
    * Moved TCWWW, PUBLICWWW, and PRIVATEWWW directly under geoips_outdirs/preprocessed
        * Previously were under ANNOTATED_IMAGERY_PATH

### Breaking Test Repo Updates
    * Replaced sector_type "atcf" with "tc" in all TC metadata YAML outputs
    * Updated "geoips_outdirs/satops" paths in metadata YAML outputs
        * geoips_outdirs/satops/intermediate_files/GeoIPSfinal -> geoips_outdirs/preprocessed/annotated_imagery
        * geoips_outdirs/satops/intermediate_files/GeoIPStemp -> geoips_outdirs/preprocessed/clean_imagery
    * Updated TCWWW, PUBLICWWW, and PRIVATEWWW paths in metadata YAML outputs
        * preprocessed/annotated_imagery/tcwww -> preprocessed/tcwww
        * preprocessed/annotated_imagery/publicwww -> preprocessed/publicwww
        * preprocessed/annotated_imagery/privatewww -> preprocessed/privatewww

### Improvements
    * Simplified top level scripts
        * Moved Pull Request and Ticket Resolution templates into sphinx documentation
        * Moved entry point READMEs into sphinx documentation
    * Updated copy_diffs_for_eval.sh, delete_files_from_repo.sh, and delete_diff_dirs.sh to take "repo_name"
        * Previously ran on ALL repos.
        * Force user to select a specific repo to udpate
    * Updated tests README to include specific instructions for generating new test scripts
    * Added support for external compare_outputs module (to allow output type comparisons not specified within geoips2)


# v1.2.5: 2021-11-18, bdeck parser, updated test scripts, test_interfaces.py, SMOS text winds

### Major New Functionality
    * bdeck parser in "trackfile_parsers"
    * SMOS 'unsectored' and 'sectored' text windspeed products
    * test_interfaces.py script to successfully test EVERY dev and stable interface module
        * Required non-breaking updates to attribute names and call signatures of some functionality modules

### Improvements
    * Only use ABI test scripts, since ABI test data can be obtained via rclone commands
        * Includes config-based and explicit call.
    * Add Software Requirements Specification to documentation
    * Update documentation with ABI test calls


# v1.2.4: 2021-11-12, original_source_filename->original_source_filenames, simplify setup

### Breaking Interface Changes
    * Replaced optional original_source_filename attribute with list of original_source_filenames

### Breaking Test Repo Updates
    * Replaced original_source_filename attribute with list of original_source_filenames
        * Updated all metadata YAML outputs
        * Updated all NetCDF outputs for datasets that had implemented the original_source_filename attribute
            in the reader

### Improvements
    * Automatically check command line args (including filenames) before attempting processing
    * Assume standard geoips2_conda installation for standard config_geoips2 usage
        * Simplifies config files
        * Still allows individuals to override functionality and use their own environment
    * Simplified README installation steps
        * Create base_install_and_test.sh script that handles complete consistent conda-based geoips2 installation
        * remove "active_branch" (assume dev)


# v1.2.3: 2021-11-05, text wind outputs, internal dictionary of xarray datasets, unique TC filenames

### Breaking Interface Changes
    * Replaced internal lists of xarray datasets with dictionary of xarray datasets
        * xarray_utils/data.py sector_xarrays function now takes and returns dictionaries
        * procflows/single_source.py get_area_defs_from_command_line_args function now takes dictionary

### Breaking Test Repo Updates
    * Updated filenames to identify product implementation
        * bg<product_name> (ie, bgVisible) if background imagery was applied

### Major New Functionality
    * unsectored_xarray_dict_to_output_format product type
        * Hooks in single_source and config_based procflows to generate product immediately after reading data
    * sectored_xarray_dict_to_output_format product type
        * Hooks in single_source and config_based procflows to generate product immediately after sectoring
    * Text wind output capability
        * 'unsectored' and 'sectored' products
        * 'text_winds_full_fname' and 'text_winds_tc_fname' filename formats 
    * SMAP and AMSR2 config-based processing

### Improvements
    * Updated test_all.sh script set up to take any script that has a valid exit code
        * Previously test scripts called from test_all.sh required specific setup
        * Updated to generically handle return codes from any scripts - simplifies testing setup
    * Updated test_all_run.sh sub-script to check log outputs for "success" strings before returning 0
        * If return is 0, grep the log output for one of a set of "success" strings
            * SETUPSUCCESS
            * FOUNDPRODUCT
            * SUCCESSFUL COMPARISON DIR
            * GOODCOMPARE
        * If no success strings are present, return 42.
        * protects against test scripts that inadvertently do not exit with the proper error code
    * Removed old testing construct - replace with explicit test scripts
        * config-based testing now handles the exhaustive functionality tests (much faster)
            * SMAP fully implemented
            * AMSR2 fully implemented
        * scripts with explicit command line call for minimal single_source and overlay functionality testing
    * Additional information in tc_fname extra field for different product enhancements
        * bg<product_name> (ie, bgVisible) if background imagery was applied
        * cr<radius> (ie, cr300) if center radius coverage check was used

### Bug fixes
    * Update all readers to include 'METADATA' field (now explicitly required)


# v1.2.2: 2021-10-25, config-based processing, global stitching, AWS-based test cases, separate sfc_winds readers

### Breaking Interface Changes
    * Separated all surface winds readers from sfc_winds_netcdf
        * smos_winds_netcdf
        * smap_remss_winds_netcdf
        * amsr2_remss_winds_netcdf
        * windsat_remss_winds_netcdf
        * scat_knmi_winds_netcdf
        * ascat_uhr_netcdf

### Breaking Test Repo Updates
    * Updated default padding amount from 2.5x to 1.5x
        * caused slightly modified output times in titles for some data types (identical data output, slightly modified center time)
            * test_data_ahi_day
            * test_data_amsr2
            * test_data_ascat_bin
            * test_data_smap
            * test_data_viirs

### Refactor
    * Separated all surface winds readers from sfc_winds_netcdf (see breaking interface changes)

### Major New Functionality:
    * Modular geostationary stitching capability
        * SEVIRI, ABI, and AHI
        * single channel products tested (Infrared-Gray and WV)

### Improvements
    * Single installation script with prompts to step through all installation/testing steps
        * Replaces step-by-step copy-paste in README with single call to full_nrl_installation.sh
    * Installation steps now return 1 for failed pulls and updates and fail catastrophically
        * Ensure timely notification of failure to reduce incomplete installations
        * Does not continue with further steps until all steps complete
    * Standard installation and testing now includes AWS-based ABI testing
        * Prevents requiring separate test data repo for basic testing -
            everything required is included in the geoips2 repo
            (comparison outputs, and commands to obtain test datasets).
    * Added SatZenith, sensor_scan_angle, and channel number attributes to PMW readers (supports CRTM)
        * SSMI/S
        * AMSU-B
        * AMSR2

### Bug fixes
    * Resolved issue with SMAP only processing one of the 2 daily overpasses
        * Previously always filtered dynamic area_defs to return a single area_def based on the data center_time
            * Now only return single area_def for data files covering < 3h
            * Now return ALL area_defs for data files covering > 3h
            * Now filter area_defs during processing - after sectoring datafile,
                check if the current area_def is the "closest", if not, skip.
    * Resolved bug in AMSU-b start and end time
        * Previously pulled start/end time from filename - test datafile actually had incorrect time listed!
        * Updated to pull directly from the metadata.


# v1.2.1: Test repo output updates (remove recentering, updated matplotlib/cartopy), and code refactor/simplification

### Breaking Interface Changes
    * remove_duplicates function now takes the explicit filename_format string, and returns the remove_duplicates
      method within the <filename_format> module.
    * Separated sar_netcdf reader from sfc_winds_netcdf.py
        * Eventually plan to separate all sfc_winds readers - they should all be independent modules.

### Breaking Test Repo Updates
    * Updated cartopy to 0.20.0 and matplotlib to v3.4.3
        * test repo outputs incompatible with matplotlib < 3.4.0 and cartopy < 0.19.0
        * Older versions have figures that are very slightly shifted from later versions
        * Exclusively a qualitative difference, but it *does* cause the test comparisons to fail
    * No longer recentering all TC outputs by default
        * General outputs are *not* recentered as of 1.2.1 - test recentering separately from other functionality

### Refactor
    * Moved metoctiff plugin to a separate installable repository
    * Moved recenter_tc plugin to a separate installable repository

### Major New Functionality:
    * Initial center radius coverage checks, for Tropical Cyclone applications
    * Initial SAR Normalized Radar Cross Section (NRCS) product implementation

### Improvements
    * Standardized and formalized the README, setup script, and test script format for all plugin repos
    * Removed requirement to link test scripts from plugin repos into the main geoips2 test directory

### Bug fixes
    * Added "METADATA" key in sfc_winds_netcdf.py return dictinoary


# v1.2.0: Major backwards incompatible update for stable and dev plugin interface implementation

### Breaking Interface Changes
    * Removed all deprecated code
    * Developed dev interface for accessing modules, moved plugins to geoips2/interface_modules
        * algorithms, area_def_generators, coverage_checks, filename_formats, interpolation,
          mtif_params, output_formats, procflows, trackfile_parsers, user_colormaps
    * Developed finalized stable interface, moved stable plugins to geoips2/interface_modules
        * readers
    * Consolidated YAML config files in geoips2/yaml_configs

### Refactor
    * Moved geoips2 package into subdirectory for pip installability

### Major New Functionality:
    * Exhaustive test scripts with final return value of 0 for successful completion of all functionality
    * dev and stable interfaces, allowing entry point based plugins
    * Initial geotiff output support
    * Initial full disk output support
    * Night Visible products
    * Gdeck and flat sectorfile trackfile parsers

### Improvements
    * YAML based product specifications (references colormaps, algorithms,
      interpolation routines, coverage checks, etc)

### Bug fixes
    * Resolved sectoring issue, allowing complete center coverage
        * Previously when sectoring based on min/max lat/lon, any values outside the explicit
          requested values would be masked, causing masked data on non-square datasets when 
          good data was actually available for the entire requested region. Only drop rows outside
          requested range, do not mask data.

### Performance Upgrades
    * Initial config-based processing implementation, which will allow efficiently processing
      multiple output types in a single run.



# v1.1.17: Rearranged for stable interface implementation

### Removed Code
    * drivers/autotest_*
        * Previously automated test scripts relied on specific autotest drivers for each sensor. Update
          to allow for generalized drivers, and shell scripts that drive for specific sensors.

# v1.1.16: rearranged for pip installability for open source release, product updates per JTWC request

### Refactor:
    * Moved fortran algorithms into separate repositories
    * Identified differences between 1.1.3 and 1.1.16
        * Restored and marked retired code as deprecated

### Major New Functionality:
    * Created sector overpass database
    * Turned on Visible global stitched
    * Allow ASCAT ESA primary solutions text output
    * Implemented API structure for accessing modules from multiple repos
        (unused, but functional)

### Improvements:
    * Updated 89H and 89H-Legacy color schemes per JTWC request
    * Switched active MTIFs from smoothed new colormaps to nearest neighbor "legacy" colormaps
    * Apply color ranges to PMW products directly rather than relying on matplotlibs normalize routine.

### Bug fixes:
    * Partially resolved RGB MTIF color issue (0 is bad val)
    * Corrected TC web output (was matching dictionary keys incorrectly)
    * Resolved multiple errors with MODIS global stitched processing.


# v1.1.15 Change Log

### Refactor:
    * BREAKING CHANGE: Modularized PMW algorithms and colormaps
    * Finalized bash setup to enable Python 3 exclusive operation

### Improvements:
    * Update 37H and 89H colormaps to more closely match Legacy colormaps,
        but with extended range
    * Standardize Visible products

### Features:
    * MODIS reader
    * Finalized stitched product output


# v1.1.14 Change Log

### Refactor:
    * BREAKING CHANGE: "channels" dictionary in algorithms now contains lists of
                    variables by default (rather than a single variable)

### Features:
    * Overpass predictor database - polar orbiting and geostationary satellites
    * Upper and lower level water vapor algorithms, MODIS Visible algorithm
    * Add FINAL_DATA_PATH variable in base_paths for default final processed data output location
    * Allow output netcdf filenames using subset of field names
    * Generalized product stitching capability for single channel products
    * Initial attempt at parallax correction in generalized stitched products
    * Allow text trackfile based processing

### Fix:
    * Resolve errors when XRIT decompress software is missing


# v1.1.3 -> v1.1.13 Change Log


### (Pending) Remove Code:

    * old_tcweb_fnames (Added tc_lon argument to old_tcweb_fnames)
    * Remove products/pmw_mint.py


### (Pending) Deprecation Warnings

    * find_modules_in_geoips2_packages -> find_modules
        *Corrected find module terminology and added support for different module and method names
        * PREVIOUS find_modules_in_geoips2_packages(module_name, method_name)
            * from geoips2.module_name.method_name import method_name  # Always same method name
        * UPDATED find_modules_in_geoips2_packages(subpackage_name, module_name, method_name=None)
            * from geoips2.subpackage_name.module_name import method_name
        * Imports in "drivers" will require updating to new terminology. Note this will all go away with Tim entry points
    
    * geoips2_modules / $GEOIPS2_MODULES_DIR -> geoips2_packages and $GEOIPS2_PACKAGES_DIR
        * These are convenience variables / directory structures for storing multiple geoips2 repositories.
        * Updated modules to packages for accurate naming conventions, handle discrepancies in gpaths/config
        * Note this will also all go away with Tim entry points


### Breaking Changes

    * BREAKING CHANGE: standardized platform names
        * sen1 -> sentinel-1, metopa -> metop-a, metopb -> metop-b, metopc -> metop-c, radarsat2 -> radarsat-2
        * NOAA-19 -> noaa-19, NOAA-18 -> noaa-18, amsub -> amsu-b, 

    * BREAKING CHANGE: Changed wind_speed to vmax in sector_info dictionary for TCs ALSO CHANGED IN PYROCB!!!!!!!
        * Change track_type -> aid_type

    * BREAKING CHANGE: Renamed area_def -> area_definition xarray attribute


### Deprecation Warnings

    * get_area_defs_for_xarray -> get_static_area_defs_for_xarray AND get_atcf_area_defs_for_xarray
        * (added get_trackfile_area_defs)

    * commandline run_yaml_from_deckfile.py -> convert_trackfile_to_yaml.py 

    * commandline update_atcf_database.py -> update_tc_tracks_database.py

    * sector_utils/atcf_tracks.py -> sector_utils/tc_tracks.py
        * sector_utils/atcf_database.py -> tc_tracks_database.py

    * colormaps.py -> colormap_utils.py - moved colormaps into subpackage user_colormaps

    * moved set_matplotlib_colors_standard from mpl_utils to colormap_utils
        * -    from geoips2.image_utils.mpl_utils import set_matplotlib_colors_standard
        * +    from geoips2.image_utils.colormap_utils import set_matplotlib_colors_standard

    * products/global_stitched -> products/stitched

    * some imports from mpl_utils moved to user_colormaps and/or colormap_utils
        * -from geoips2.image_utils.mpl_utils import set_matplotlib_colors_37H
        * +from geoips2.image_utils.user_colormaps.pmw import set_matplotlib_colors_37H
        * +from geoips2.image_utils.colormap_utils import set_matplotlib_colors_standard
        * +from geoips2.image_utils.user_colormaps.winds import set_matplotlib_colors_winds


### Refactoring

    * Created separate modules for each visir and pmw products within algorithms/visir and algorithms/pmw
        * Previously all separate products were combined within products/visir.py and products/pmw_tb.py

    * Standardized geolocation generation for ABI/AHI/SEVIRI


### New Readers

    * Added amsu-b MIRS reader

    * Added MIMIC reader

    * Added MODIS hdf4 reader


### Performance Upgrades

    * For xarray sectoring - pass "check_center" and "drop" to allow checking coverage based on the center of the image,
        and completely dropping rows and columns that are unneeded


### New functionality

    * Added additional command line arguments:
        * atcf_db, atcf_db_sectorlist to specify TC processing based on the TC database
        * trackfiles, trackfile_parser, and trackfile_sectorlist to specify processing based on the flat sectorfile
    * Added support for arbitrary TC trackfile parsing - currently flat sectorfile and G-decks
    *  Added xml_to_yaml geoips1 sectorfile conversion utility
    *  Added parallax_correction argument to data_manipulations.merge.merge_data
        * Currently does not blend msg-1 with AHI near the equator, later could implement optical flow based corrections
    *  Allow building documentation for alternative geoips packages, not only geoips2
    *  Added ambiguity wind barb plotting
    *  Added global stitched imagery capability
    *  Added TPW processing
    *  Allow optional fields for netcdf output filename
    *  Fully support xml -> yaml conversions for geoips1 sectorfiles.
    *  Replace '-' with '_' in method and module names for find_modules
    *  Added overpass predictor
    *  Added static sector database
    *  Added database of TC overpasses


### Bug Fixes

    * Resolved bug with transparency behind titles / borders for cartopy plotting
    * Ensure metadata goes in _dev directory if product is in _dev directory
    * Use make_dirs for netcdf write (sets permissions) rather than os.makedirs()
