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

# Python Standard Libraries
from datetime import timedelta
import os

# Third Party Installed Libraries
import logging
import numpy

from geoips2.filenames.base_paths import PATHS as gpaths

LOG = logging.getLogger(__name__)

SAT_CONFIG = {}
# This is set up to merge channel data together from multiple platforms, then various algorithms can be applied
# to that merged channel data
SAT_CONFIG['sectors'] = {}

# This specifies how the sectors should be merged together
SAT_CONFIG['sectors']['GlobalGlobal'] = {
                      'merge_lines': {'GlobalGlobal': [0, 1000],
                                      'GlobalArctic': [0, 200],
                                      'GlobalAntarctic': [800, 1000],
                                      },
                      'merge_samples': {'GlobalGlobal': [0, 2000],
                                        'GlobalArctic': [0, 2000],
                                        'GlobalAntarctic': [0, 2000],
                                        },
                      }

# This merges channel data together appropriately - do VIIRS first so it goes in the back.
SAT_CONFIG['platforms'] = {'merge_platforms': ['jpss', 'npp', 'goes17', 'goes16', 'himawari8',
                                               'meteoIO', 'meteoEU'],
                           'merge_sources': ['viirs', 'viirs', 'abi', 'abi', 'ahi',
                                             'seviri', 'seviri'],
                           'merge_max_time_diffs': [1400, 1400, 30, 30, 30,
                                                   30, 30],
                           'run_on_sources': ['ahi', 'abi', 'seviri'],
                           'roi': {'viirs': 100000,
                                   'abi': 100000,
                                   'ahi': 100000,
                                   'seviri': 100000},
                           'merge_channels': {'product_name': '11um',
                                              'abi': 'B14BT',
                                              'ahi': 'B14BT',
                                              'seviri': 'B09BT',
                                              'viirs': 'SVM16BT'
                                              },
                           }


def global_stitched(full_xarray, area_def):
    '''
    Stitching geostationary and polar imagery into a single product
      NOTE in geoips/geoimg/plot/prototypealg.py
          scifile is converted to xarray BEFORE being passed
          sector is converted to area_def BEFORE being passed
      from geoips2.geoips1_utils.scifile import xarray_from_scifile
      from geoips2.geoips1_utils.sector import area_def_from_sector
    '''
    # Run stuff like this to produce a global stitched image over time:
    # ./geoips/geoips/driver.py /data/20190529.11/goes16/20190529.1100/ -s globalglobal -p global-stitched
    # ./geoips/geoips/driver.py /data/20190529.11/goes17/20190529.1100/ -s globalglobal -p global-stitched
    # ./geoips/geoips/driver.py /data/20190529.11/ahi/20190529.1100/ -s globalglobal -p global-stitched
    # ./geoips/geoips/driver.py /data/20190529.11/meteo11EU/20190529.1100/ -s globalglobal -p global-stitched
    # ./geoips/geoips/driver.py /data/20190529.11/meteo8EU/20190529.1100/ -s globalglobal -p global-stitched
    # ./geoips/geoips/driver.py /data/20190529.11/npp/20190529.1100/ -s globalarctic -p global-stitched
    # ./geoips/geoips/driver.py /data/20190529.11/jpss/20190529.1100/ -s globalantarctic -p global-stitched

    # MLS5 Turn this off completely for now.  We can move the return farther and farther down the line as we go!
    # return


    if full_xarray.source_name in SAT_CONFIG['platforms']['roi'].keys():
        roi = SAT_CONFIG['platforms']['roi'][full_xarray.source_name]
        full_xarray.attrs['interpolation_radius_of_influence'] = roi

    varname = SAT_CONFIG['platforms']['merge_channels'][full_xarray.source_name]
    prodname = SAT_CONFIG['platforms']['merge_channels']['product_name']

    from geoips2.xarray_utils.data import sector_xarray_dataset
    sect_xarray = sector_xarray_dataset(full_xarray, area_def, [varname])
    if sect_xarray is None:
        LOG.info('NO COVERAGE, SKIPPING')
        return None
    sect_xarray.attrs['sector_name'] = area_def.area_id
    sect_xarray[prodname] = sect_xarray[varname]

    from geoips2.xarray_utils.interpolation import interp_nearest
    [interp_data] = interp_nearest(area_def,
                                   sect_xarray,
                                   varlist=[prodname])

    import xarray
    alg_xarray = xarray.Dataset()
    target_lons, target_lats = area_def.get_lonlats()
    alg_xarray[prodname] = xarray.DataArray(interp_data)
    alg_xarray['latitude'] = xarray.DataArray(target_lats)
    alg_xarray['longitude'] = xarray.DataArray(target_lons)
    alg_xarray.attrs = sect_xarray.attrs.copy()

    from geoips2.filenames.product_filenames import netcdf_write_filename
    # Use %H%M time format so we don't try to match seconds.
    ncdf_fname = netcdf_write_filename(gpaths['PRECALCULATED_DATA_PATH'],
                                       product_name=prodname,
                                       source_name=alg_xarray.source_name,
                                       platform_name=alg_xarray.platform_name,
                                       sector_name=area_def.area_id,
                                       product_datetime=alg_xarray.start_datetime,
                                       time_format='%H%M')

    from geoips2.xarray_utils.outputs import write_xarray_netcdf
    write_xarray_netcdf(alg_xarray, ncdf_fname)

    if alg_xarray.source_name in SAT_CONFIG['platforms']['run_on_sources']:
        from geoips2.data_manipulations.merge import get_matching_files, merge_data
        import geoips.sectorfile as sectorfile

        for primary_sector_name in SAT_CONFIG['sectors'].keys():
            # Use %H%M time format so we don't try to match seconds, and so we match written filename above.
            match_fnames = get_matching_files(primary_sector_name,
                                              subsector_names=SAT_CONFIG['sectors'][primary_sector_name]['merge_lines'],
                                              platforms=SAT_CONFIG['platforms']['merge_platforms'],
                                              sources=SAT_CONFIG['platforms']['merge_sources'],
                                              max_time_diffs=SAT_CONFIG['platforms']['merge_max_time_diffs'],
                                              basedir=gpaths['PRECALCULATED_DATA_PATH'],
                                              merge_datetime=full_xarray.start_datetime,
                                              product_name=prodname,
                                              time_format='%H%M')

            # Open the primary_sector_name to get the lat/lons and resolution of the overall sector
            main_sector = sectorfile.open(sectorlist=[primary_sector_name]).open_sector(primary_sector_name)
            sectlons, sectlats = main_sector.area_definition.get_lonlats()

            finaldata, attrs = merge_data(match_fnames, sectlons.shape, variable_name=prodname,
                                          merge_samples=SAT_CONFIG['sectors'][primary_sector_name]['merge_samples'],
                                          merge_lines=SAT_CONFIG['sectors'][primary_sector_name]['merge_lines'])

            stitched_xarray = xarray.Dataset()
            stitched_xarray[prodname] = xarray.DataArray(finaldata).astype(numpy.float32)
            latdims = stitched_xarray.dims.keys()[0]
            londims = stitched_xarray.dims.keys()[1]
            stitched_xarray['latitude'] = xarray.DataArray(sectlats[:, 0], dims=latdims).astype(numpy.float32)
            stitched_xarray['longitude'] = xarray.DataArray(sectlons[0, :], dims=londims).astype(numpy.float32)
            stitched_xarray.attrs = attrs
            stitched_xarray.attrs['start_datetime'] = full_xarray.start_datetime
            stitched_xarray.attrs['platform_name'] = 'stitched'
            stitched_xarray.attrs['source_name'] = 'stitched'
            stitched_xarray.attrs['data_provider'] = 'stitched'
            # ## from geoips2.output_formats.image import plot_image, set_plotting_params, coverage
            # ## set_plotting_params(geoimg_obj,
            # ##                     finaldata,
            # ##                     cmap_name='Blues',
            # ##                     title_str='This is\nMy Title',
            # ##                     is_final=True)
            from geoips2.data_manipulations.info import percent_unmasked
            from geoips2.xarray_utils.outputs import output_geoips_fname
            web_fname = output_geoips_fname(area_def, stitched_xarray, prodname, percent_unmasked(finaldata))
            web_fname_clear = output_geoips_fname(area_def, stitched_xarray, prodname+'Clear', percent_unmasked(finaldata))

            from geoips2.image_utils.mpl_utils import create_figure_and_main_ax_and_mapobj
            from geoips2.image_utils.mpl_utils import set_matplotlib_colors_standard
            from geoips2.image_utils.mpl_utils import plot_image, save_image, plot_overlays
            from geoips2.image_utils.mpl_utils import get_title_string_from_objects, set_title
            from geoips2.image_utils.mpl_utils import create_colorbar

            # Create matplotlib figure and main axis, where the main image will be plotted
            fig, main_ax, mapobj = create_figure_and_main_ax_and_mapobj(area_def.x_size,
                                                                        area_def.y_size,
                                                                        area_def)

            # Create the matplotlib color info dict - the fields in this dictionary (cmap, norm, boundaries,
            # etc) will be used in plot_image to ensure the image matches the colorbar.
            mpl_colors_info = set_matplotlib_colors_standard(data_range=[finaldata.min(), finaldata.max()],
                                                             cmap_name=None,
                                                             cbar_label=None)

            # Plot the actual data on a basemap or cartopy instance
            plot_image(main_ax, finaldata, mapobj, mpl_colors_info=mpl_colors_info)

            # Save the clean image with no gridlines or coastlines
            save_image(fig, web_fname_clear, is_final=False)

            # Set the title for final image
            title_string = get_title_string_from_objects(area_def, sect_xarray, prodname)
            set_title(main_ax, title_string, area_def.y_size)

            # Create the colorbar to match the mpl_colors
            create_colorbar(fig, mpl_colors_info)

            # Plot gridlines and boundaries overlays
            plot_overlays(mapobj, main_ax, area_def, boundaries_info=None, gridlines_info=None)

            # Save the final image
            save_image(fig, web_fname, is_final=True)

            from geoips2.filenames.product_filenames import netcdf_write_filename
            del(stitched_xarray.attrs['start_datetime'])
            stitched_xarray.attrs['valid_datetime'] = full_xarray.start_datetime
            # Use %H%M time format so we don't try to match seconds.
            ncdf_fname = netcdf_write_filename(gpaths['MAPROOMDROPBOX'],
                                               product_name=prodname,
                                               source_name=full_xarray.source_name,
                                               platform_name=full_xarray.platform_name,
                                               sector_name=area_def.area_id,
                                               product_datetime=stitched_xarray.valid_datetime,
                                               time_format='%H%M')

            from geoips2.xarray_utils.outputs import write_xarray_netcdf
            write_xarray_netcdf(full_xarray, ncdf_fname)
    else:
        LOG.info('SKIPPING Not specified to run on %s, exiting', alg_xarray.source_name)

    return None
