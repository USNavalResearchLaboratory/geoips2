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

import os
import numpy
import logging

LOG = logging.getLogger(__name__)


def create_standard_imagery(area_def,
                            plot_data,
                            xarray_obj,
                            product_name_title,
                            clean_fname=None,
                            annotated_fnames=None,
                            mpl_colors_info=None,
                            boundaries_info=None,
                            gridlines_info=None,
                            product_datatype_title=None,
                            bg_data=None,
                            bg_mpl_colors_info=None,
                            bg_xarray=None,
                            bg_product_name_title=None,
                            bg_datatype_title=None,
                            remove_duplicate_minrange=None):

    success_outputs = []
    from geoips2.image_utils.mpl_utils import create_figure_and_main_ax_and_mapobj
    from geoips2.image_utils.mpl_utils import set_matplotlib_colors_standard
    from geoips2.image_utils.mpl_utils import plot_image, save_image, plot_overlays, create_colorbar
    from geoips2.image_utils.mpl_utils import get_title_string_from_objects, set_title

    if not mpl_colors_info:
        # Create the matplotlib color info dict - the fields in this dictionary (cmap, norm, boundaries,
        # etc) will be used in plot_image to ensure the image matches the colorbar.
        mpl_colors_info = set_matplotlib_colors_standard(data_range=[plot_data.min(), plot_data.max()],
                                                         cmap_name=None,
                                                         cbar_label=None)

    mapobj = None
    if clean_fname:
        # Create matplotlib figure and main axis, where the main image will be plotted
        fig, main_ax, mapobj = create_figure_and_main_ax_and_mapobj(area_def.x_size,
                                                                    area_def.y_size,
                                                                    area_def,
                                                                    noborder=True)

        # Plot the actual data on a map
        plot_image(main_ax,
                   plot_data,
                   mapobj,
                   mpl_colors_info=mpl_colors_info)

        LOG.info('Saving the clean image %s', clean_fname)
        # Save the clean image with no gridlines or coastlines
        success_outputs += save_image(fig, clean_fname, is_final=False, image_datetime=xarray_obj.start_datetime,
                                      remove_duplicate_minrange=remove_duplicate_minrange)

    # Create matplotlib figure and main axis, where the main image will be plotted
    fig, main_ax, mapobj = create_figure_and_main_ax_and_mapobj(area_def.x_size,
                                                                area_def.y_size,
                                                                area_def,
                                                                existing_mapobj=mapobj,
                                                                noborder=False)

    # Plot the actual data on a map
    plot_image(main_ax,
               plot_data,
               mapobj,
               mpl_colors_info=mpl_colors_info)

    if bg_data is not None and hasattr(plot_data, 'mask'):
        if not bg_mpl_colors_info:
            bg_mpl_colors_info = set_matplotlib_colors_standard(data_range=[plot_data.min(), plot_data.max()],
                                                                cmap_name=None,
                                                                cbar_label=None,
                                                                create_colorbar=False)
        # Plot the background data on a map
        plot_image(main_ax,
                   numpy.ma.masked_where(~plot_data.mask, bg_data),
                   mapobj,
                   mpl_colors_info=bg_mpl_colors_info)

    # Set the title for final image
    title_string = get_title_string_from_objects(area_def, xarray_obj, product_name_title,
                                                 product_datatype_title=product_datatype_title,
                                                 bg_xarray=bg_xarray,
                                                 bg_product_name_title=bg_product_name_title,
                                                 bg_datatype_title=bg_datatype_title)
    set_title(main_ax, title_string, area_def.y_size)

    if mpl_colors_info['colorbar'] is True:
        # Create the colorbar to match the mpl_colors
        create_colorbar(fig, mpl_colors_info)

    # Plot gridlines and boundaries overlays
    plot_overlays(mapobj, main_ax, area_def, boundaries_info=boundaries_info, gridlines_info=gridlines_info)

    if annotated_fnames is not None:
        for annotated_fname in annotated_fnames:
            # Save the final image
            success_outputs += save_image(fig, annotated_fname, is_final=True, image_datetime=xarray_obj.start_datetime,
                                          remove_duplicate_minrange=remove_duplicate_minrange)

    return success_outputs
