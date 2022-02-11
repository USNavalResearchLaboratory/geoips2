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

'''Installation instructions for base geoips2 package'''

from os.path import realpath, join, dirname

import setuptools

with open(join(dirname(realpath(__file__)), 'VERSION'), encoding='utf-8') as version_file:
    version = version_file.read().strip()

setuptools.setup(
    name='geoips2',
    version=version,
    packages=setuptools.find_packages(),
    install_requires=['pyresample',         # Base requirement
                      'numpy',              # Base requirement
                      'xarray',             # Base requirement
                      'matplotlib==3.4.3',  # Base requirement - Previously v3.3 required for test outputs, using latest
                      'scipy',              # Base requirement
                      'netcdf4',            # Base requirement
                      'pyyaml',             # Base requirement
                      'pyaml_env',          # Required for config-based processing
                      'ipython',            # Required for Debugging purposes
                      'sphinx',             # Required for building documentation
                      'satpy',              # Geostationary readers
                      'numexpr',            # Geostationary readers
                      'pyorbital',          # required by satpy
                      #'rasterio',           # GEOTIFF output
                      'pyhdf',              # hdf4 readers (MODIS)
                      'h5py',               # hdf5 readers (GMI)
                      'tifffile',
                      'pillow',
                      'scikit-image',
                      'flake8',             # Syntax checking
                      'pylint',             # Syntax checking
                      'bandit',             # Syntax/security checking
                      'ephem',              # Required for overpass predictor
                      'isodate',            # Required for overpass predictor
                      # 'cartopy==0.20.0',    # Currently must install via conda
                      ],
    entry_points={
        'console_scripts': [
            'run_procflow=geoips2.commandline.run_procflow:main',
            'convert_trackfile_to_yaml=geoips2.commandline.convert_trackfile_to_yaml:main',
            'update_tc_tracks_database=geoips2.commandline.update_tc_tracks_database:main',
            'xml_to_yaml_sector=geoips2.commandline.xml_to_yaml_sector:main',
            'test_interfaces=geoips2.commandline.test_interfaces:main',
            'list_available_modules=geoips2.commandline.list_available_modules:main',
        ],
        'geoips2.readers': [
            'abi_netcdf=geoips2.interface_modules.readers.abi_netcdf:abi_netcdf',
            'abi_l2_netcdf=geoips2.interface_modules.readers.abi_l2_netcdf:abi_l2_netcdf',
            'ahi_hsd=geoips2.interface_modules.readers.ahi_hsd:ahi_hsd',
            'amsr2_netcdf=geoips2.interface_modules.readers.amsr2_netcdf:amsr2_netcdf',
            'amsub_hdf=geoips2.interface_modules.readers.amsub_hdf:amsub_hdf',
            'amsub_mirs=geoips2.interface_modules.readers.amsub_mirs:amsub_mirs',
            'ewsg_netcdf=geoips2.interface_modules.readers.ewsg_netcdf:ewsg_netcdf',
            'geoips2_netcdf=geoips2.interface_modules.readers.geoips2_netcdf:geoips2_netcdf',
            'gmi_hdf5=geoips2.interface_modules.readers.gmi_hdf5:gmi_hdf5',
            'imerg_hdf5=geoips2.interface_modules.readers.imerg_hdf5:imerg_hdf5',
            'mimic_netcdf=geoips2.interface_modules.readers.mimic_netcdf:mimic_netcdf',
            'modis_hdf4=geoips2.interface_modules.readers.modis_hdf4:modis_hdf4',
            'saphir_hdf5=geoips2.interface_modules.readers.saphir_hdf5:saphir_hdf5',
            'seviri_hrit=geoips2.interface_modules.readers.seviri_hrit:seviri_hrit',
            'ascat_uhr_netcdf=geoips2.interface_modules.readers.ascat_uhr_netcdf:ascat_uhr_netcdf',
            'smap_remss_winds_netcdf=geoips2.interface_modules.readers.smap_remss_winds_netcdf:smap_remss_winds_netcdf',
            'smos_winds_netcdf=geoips2.interface_modules.readers.smos_winds_netcdf:smos_winds_netcdf',
            'scat_knmi_winds_netcdf=geoips2.interface_modules.readers.scat_knmi_winds_netcdf:scat_knmi_winds_netcdf',
            'windsat_remss_winds_netcdf=geoips2.interface_modules.readers.windsat_remss_winds_netcdf:windsat_remss_winds_netcdf',
            'amsr2_remss_winds_netcdf=geoips2.interface_modules.readers.amsr2_remss_winds_netcdf:amsr2_remss_winds_netcdf',
            'sar_winds_netcdf=geoips2.interface_modules.readers.sar_winds_netcdf:sar_winds_netcdf',
            'sfc_winds_text=geoips2.interface_modules.readers.sfc_winds_text:sfc_winds_text',
            'ssmi_binary=geoips2.interface_modules.readers.ssmi_binary:ssmi_binary',
            'ssmis_binary=geoips2.interface_modules.readers.ssmis_binary:ssmis_binary',
            'viirs_netcdf=geoips2.interface_modules.readers.viirs_netcdf:viirs_netcdf',
            'wfabba_ascii=geoips2.interface_modules.readers.wfabba_ascii:wfabba_ascii',
            'windsat_idr37_binary=geoips2.interface_modules.readers.windsat_idr37_binary:windsat_idr37_binary',
        ],
        'geoips2.output_formats': [
            'full_disk_image=geoips2.interface_modules.output_formats.full_disk_image:full_disk_image',
            'geotiff_standard=geoips2.interface_modules.output_formats.geotiff_standard:geotiff_standard',
            'imagery_annotated=geoips2.interface_modules.output_formats.imagery_annotated:imagery_annotated',
            'imagery_clean=geoips2.interface_modules.output_formats.imagery_clean:imagery_clean',
            'imagery_windbarbs=geoips2.interface_modules.output_formats.imagery_windbarbs:imagery_windbarbs',
            'netcdf_geoips=geoips2.interface_modules.output_formats.netcdf_geoips:netcdf_geoips',
            'netcdf_xarray=geoips2.interface_modules.output_formats.netcdf_xarray:netcdf_xarray',
            'text_winds=geoips2.interface_modules.output_formats.text_winds:text_winds',
        ],
        'geoips2.algorithms': [
            'single_channel=geoips2.interface_modules.algorithms.single_channel:single_channel',
            'pmw_tb.pmw_37pct=geoips2.interface_modules.algorithms.pmw_tb.pmw_37pct:pmw_37pct',
            'pmw_tb.pmw_89pct=geoips2.interface_modules.algorithms.pmw_tb.pmw_89pct:pmw_89pct',
            'pmw_tb.pmw_color37=geoips2.interface_modules.algorithms.pmw_tb.pmw_color37:pmw_color37',
            'pmw_tb.pmw_color89=geoips2.interface_modules.algorithms.pmw_tb.pmw_color89:pmw_color89',
            'sfc_winds.windbarbs=geoips2.interface_modules.algorithms.sfc_winds.windbarbs:windbarbs',
            'visir.Night_Vis_IR=geoips2.interface_modules.algorithms.visir.Night_Vis_IR:Night_Vis_IR',
            'visir.Night_Vis=geoips2.interface_modules.algorithms.visir.Night_Vis:Night_Vis',
        ],
        'geoips2.procflows': [
            'single_source=geoips2.interface_modules.procflows.single_source:single_source',
            'config_based=geoips2.interface_modules.procflows.config_based:config_based',
            'overlay=geoips2.interface_modules.procflows.overlay:overlay',
        ],
        'geoips2.trackfile_parsers': [
            'flat_sectorfile_parser=geoips2.interface_modules.trackfile_parsers.flat_sectorfile_parser:flat_sectorfile_parser',
            'bdeck_parser=geoips2.interface_modules.trackfile_parsers.bdeck_parser:bdeck_parser',
        ],
        'geoips2.area_def_generators': [
            'clat_clon_resolution_shape=geoips2.interface_modules.area_def_generators.clat_clon_resolution_shape:clat_clon_resolution_shape',
        ],
        'geoips2.interpolation': [
            'pyresample_wrappers.interp_nearest=geoips2.interface_modules.interpolation.pyresample_wrappers.interp_nearest:interp_nearest',
            'pyresample_wrappers.interp_gauss=geoips2.interface_modules.interpolation.pyresample_wrappers.interp_gauss:interp_gauss',
            'scipy_wrappers.interp_grid=geoips2.interface_modules.interpolation.scipy_wrappers.interp_grid:interp_grid',
        ],
        'geoips2.user_colormaps': [
            'cmap_rgb=geoips2.interface_modules.user_colormaps.cmap_rgb:cmap_rgb',
            'matplotlib_linear_norm=geoips2.interface_modules.user_colormaps.matplotlib_linear_norm:matplotlib_linear_norm',
            'pmw_tb.cmap_150H=geoips2.interface_modules.user_colormaps.pmw_tb.cmap_150H:cmap_150H',
            'pmw_tb.cmap_37H_Legacy=geoips2.interface_modules.user_colormaps.pmw_tb.cmap_37H_Legacy:cmap_37H_Legacy',
            'pmw_tb.cmap_37H_Physical=geoips2.interface_modules.user_colormaps.pmw_tb.cmap_37H_Physical:cmap_37H_Physical',
            'pmw_tb.cmap_37H=geoips2.interface_modules.user_colormaps.pmw_tb.cmap_37H:cmap_37H',
            'pmw_tb.cmap_37pct=geoips2.interface_modules.user_colormaps.pmw_tb.cmap_37pct:cmap_37pct',
            'pmw_tb.cmap_89H_Legacy=geoips2.interface_modules.user_colormaps.pmw_tb.cmap_89H_Legacy:cmap_89H_Legacy',
            'pmw_tb.cmap_89H_Physical=geoips2.interface_modules.user_colormaps.pmw_tb.cmap_89H_Physical:cmap_89H_Physical',
            'pmw_tb.cmap_89H=geoips2.interface_modules.user_colormaps.pmw_tb.cmap_89H:cmap_89H',
            'pmw_tb.cmap_89pct=geoips2.interface_modules.user_colormaps.pmw_tb.cmap_89pct:cmap_89pct',
            'pmw_tb.cmap_89HW=geoips2.interface_modules.user_colormaps.pmw_tb.cmap_89HW:cmap_89HW',
            'pmw_tb.cmap_Rain=geoips2.interface_modules.user_colormaps.pmw_tb.cmap_Rain:cmap_Rain',
            'tpw.tpw_cimss=geoips2.interface_modules.user_colormaps.tpw.tpw_cimss:tpw_cimss',
            'tpw.tpw_purple=geoips2.interface_modules.user_colormaps.tpw.tpw_purple:tpw_purple',
            'tpw.tpw_pwat=geoips2.interface_modules.user_colormaps.tpw.tpw_pwat:tpw_pwat',
            'visir.Infrared=geoips2.interface_modules.user_colormaps.visir.Infrared:Infrared',
            'visir.IR_BD=geoips2.interface_modules.user_colormaps.visir.IR_BD:IR_BD',
            'visir.WV=geoips2.interface_modules.user_colormaps.visir.WV:WV',
            'winds.wind_radii_transitions=geoips2.interface_modules.user_colormaps.winds.wind_radii_transitions:wind_radii_transitions',
        ],
        'geoips2.filename_formats': [
            'geoips_fname=geoips2.interface_modules.filename_formats.geoips_fname:geoips_fname',
            'geoips_netcdf_fname=geoips2.interface_modules.filename_formats.geoips_netcdf_fname:geoips_netcdf_fname',
            'geotiff_fname=geoips2.interface_modules.filename_formats.geotiff_fname:geotiff_fname',
            'tc_fname=geoips2.interface_modules.filename_formats.tc_fname:tc_fname',
            'tc_clean_fname=geoips2.interface_modules.filename_formats.tc_clean_fname:tc_clean_fname',
            'text_winds_full_fname=geoips2.interface_modules.filename_formats.text_winds_full_fname:text_winds_full_fname',
            'text_winds_tc_fname=geoips2.interface_modules.filename_formats.text_winds_tc_fname:text_winds_tc_fname',
        ],
        'geoips2.coverage_checks': [
            'masked_arrays=geoips2.interface_modules.coverage_checks.masked_arrays:masked_arrays',
            'center_radius=geoips2.interface_modules.coverage_checks.center_radius:center_radius',
            'rgba=geoips2.interface_modules.coverage_checks.rgba:rgba',
            'windbarbs=geoips2.interface_modules.coverage_checks.windbarbs:windbarbs',
        ],
        'geoips2.output_comparisons': [
            'compare_outputs=geoips2.compare_outputs:compare_outputs',
        ],
    }
)
