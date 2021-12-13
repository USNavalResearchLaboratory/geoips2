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

''' Module containing matplotlib information for standard imagery with an existing system colormap'''
import logging

LOG = logging.getLogger(__name__)

cmap_type = 'builtin_matplotlib_cmap'


def matplotlib_linear_norm(data_range, cmap_name='Greys', cbar_label=None, create_colorbar=True):
    ''' Set the matplotlib colors information appropriately, for use in colorbar and image production.

    Args:
        data_range (list) : [min_val, max_val]
        cmap_name (str) : Default 'Greys' - specify the standard matplotlib colormap.
        cbar_label (str) : Default None - If specified, use cbar_label string as colorbar label.
        create_colorbar (bool) : Default True - Specify whether the image should contain a colorbar or not.

    Returns:
        mpl_colors_info (dict) Specifies matplotlib Colors parameters for use in both plotting and colorbar generation
                                See geoips2.image_utils.mpl_utils.create_colorbar for field descriptions.
    '''

    min_val = int(data_range[0])
    max_val = int(data_range[1])

    from matplotlib import cm
    # cmap = cm.ScalarMappable(norm=colors.NoNorm(), cm.get_cmap(cmap_name))
    mpl_cmap = cm.get_cmap(cmap_name)

    LOG.info('Setting norm')
    from matplotlib.colors import Normalize
    mpl_norm = Normalize(vmin=min_val, vmax=max_val)
    mpl_ticks = [min_val, max_val]

    # Must be uniform or proportional, None not valid for Python 3
    cbar_spacing = 'proportional'
    mpl_tick_labels = None
    mpl_boundaries = None

    mpl_colors_info = {'cmap': mpl_cmap,
                       'norm': mpl_norm,
                       'cbar_ticks': mpl_ticks,
                       'cbar_tick_labels': mpl_tick_labels,
                       'cbar_label': cbar_label,
                       'boundaries': mpl_boundaries,
                       'cbar_spacing': cbar_spacing,
                       'colorbar': create_colorbar}

    return mpl_colors_info
