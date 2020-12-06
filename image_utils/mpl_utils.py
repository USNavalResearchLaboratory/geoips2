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

''' matplotlib utilities '''

# Python Standard Libraries
import logging
import matplotlib

LOG = logging.getLogger(__name__)


def percent_unmasked_rgba(rgba):
    ''' Return percentage of array that is NOT fully transparent / masked (ie, non-zero values in the 4th dimension)

    Args:
        rgba (numpy.ndarray) : 4 dimensional array where the 4th dimension is the alpha transparency array:
                               1 is fully opaque, 0 is fully transparent

    Returns:
        float : Coverage in percentage, between 0 and 100.
    '''
    import numpy
    return 100.0 * numpy.count_nonzero(rgba[:, :, 3]) / rgba[:, :, 3].size


def rgba_from_arrays(red, grn, blu, alp=None):
    ''' Return rgba for plotting in matplot lib from red, green, blue, and alpha arrays

    Args:
        red (numpy.ndarray) : numpy masked array of red gun values
        grn (numpy.ndarray) : numpy masked array of green gun values
        blu (numpy.ndarray) : numpy masked array of blue gun values
        alp (numpy.ndarray) : DEFAULT None, numpy.ndarray of alpha values 1 is fully opaque, 0 is fully transparent
                                If none, calculate alpha from red, grn, blu guns

    Returns:
        (numpy.ndarray) : 4 layer dimensional numpy.ndarray
    '''

    import numpy
    if alp is None:
        alp = alpha_from_masked_arrays([red, grn, blu])
    red.fill_value = 0
    grn.fill_value = 0
    blu.fill_value = 0
    return numpy.dstack([red.filled(), grn.filled(), blu.filled(), alp])


def alpha_from_masked_arrays(arrays):
    ''' Return an alpha transparency array based on the masks from a list of masked arrays. 0=transparent, 1=opaque

    Args:
        arrays (list): list of numpy masked arrays, must all be the same shape

    Returns:
        numpy.ndarray : Returns a numpy array of floats to be used as the alpha transparency layer in matplotlib,
                          values between 0 and 1, where
                            0 is fully transparent and
                            1 is fully opaque
    '''
    import numpy
    alp = numpy.zeros(arrays[0].shape, dtype=numpy.bool)
    for img in arrays:
        try:
            if img.mask is not numpy.False_:
                alp += img.mask
        except AttributeError:
            pass
    # You will get yelled at by numpy if you removed the "alp.dtype" portion of this.
    #   It thinks you are trying to cast alp to be an integer.
    alp = numpy.array(alp, dtype=numpy.float)
    alp -= numpy.float(1)
    alp *= numpy.float(-1)
    return alp


def plot_overlays(mapobj, curr_ax, area_def, boundaries_info, gridlines_info):
    ''' Plot specified coastlines and gridlines on the matplotlib axes.

    Args:
        mapobj (map object): Basemap or CRS object for boundary and gridline plotting.
        ax (matplotlib.axes._axes.Axes): matplotlib Axes object for boundary and gridline plotting.
        area_def (AreaDefinition) : pyresample AreaDefinition object specifying the area covered by the current plot
        boundaries_info (dict) : Dictionary of parameters for plotting map boundaries.
                                 See geoips2.image_utils.maps.set_boundaries_info_dict
                                     for required fields and defaults
        gridlines_info (dict) : Dictionary of parameters for plotting gridlines.
                                If a field is not included in the dictionary, the default is used for that field.
                                 See geoips2.image_utils.maps.set_gridlines_info_dict
                                     for required fields and defaults
    Returns:
        No return values. Overlays are plotted directly on the mapobj and ax instances.

    '''

    from geoips2.image_utils.maps import set_boundaries_info_dict, set_gridlines_info_dict
    use_boundaries_info = set_boundaries_info_dict(boundaries_info)
    use_gridlines_info = set_gridlines_info_dict(gridlines_info, area_def)

    from geoips2.image_utils.maps import draw_boundaries
    draw_boundaries(mapobj, curr_ax, use_boundaries_info)

    from geoips2.image_utils.maps import draw_gridlines
    draw_gridlines(mapobj, area_def, curr_ax, use_gridlines_info)


def save_image(fig, out_fname, is_final=True, image_datetime=None, remove_duplicate_minrange=None):
    ''' Save the image specified by the matplotlib figure "fig" to the filename out_fname.

    Args:
        fig (Figure) : matplotlib.figure.Figure object that needs to be written to a file.
        out_fname (str) : string specifying the full path to the output filename
        is_final (bool) : Default True. Final imagery must set_axis_on for all axes. Non-final imagery must be
                                        transparent with set_axis_off for all axes, and no pad inches.

    Returns:
        No return values (image is written to disk and IMAGESUCCESS is written to log file)
    '''
    import matplotlib
    import matplotlib.pyplot as plt
    matplotlib.use('agg')
    rc_params = matplotlib.rcParams
    from os.path import dirname, exists as pathexists
    from geoips2.filenames.base_paths import make_dirs
    if is_final:
        if not pathexists(dirname(out_fname)):
            make_dirs(dirname(out_fname))
        for ax in fig.axes:
            LOG.info('Adding ax to %s', ax)
            ax.set_axis_on()
        # final with titles, labels, etc.  Note bbox_inches='tight' removes white space, pad_inches=0.1 puts back in
        # a bit of white space.
        LOG.info('Writing %s', out_fname)
        fig.savefig(out_fname, dpi=rc_params['figure.dpi'], pad_inches=0.1, bbox_inches='tight', transparent=False)
        if remove_duplicate_minrange is not None:
            remove_duplicates(out_fname, remove_duplicate_minrange)
    else:
        # Get rid of the colorbar axis for non-final imagery
        if not pathexists(dirname(out_fname)):
            make_dirs(dirname(out_fname))
        # no annotations
        # frameon=False makes it have no titles / lat/lons. does not avoid colorbar, since that is its own ax 
        for ax in fig.axes:
            LOG.info('Removing ax from %s', ax)
            ax.set_axis_off()
        LOG.info('Writing %s', out_fname)
        fig.savefig(out_fname, dpi=rc_params['figure.dpi'], pad_inches=0.0,
                    transparent=True, frameon=False)
        if remove_duplicate_minrange is not None:
            remove_duplicates(out_fname, remove_duplicate_minrange)

    LOG.info('IMAGESUCCESS wrote %s', out_fname)
    if image_datetime is not None:
        from datetime import datetime
        LOG.info('LATENCY %s %s', out_fname, datetime.utcnow() - image_datetime)
    return [out_fname]


def remove_duplicates(fname, min_range):
    pass


def set_mpl_colors_info_dict(cmap, norm, cbar_ticks, cbar_tick_labels=None, boundaries=None,
                             cbar_label=None, cbar_spacing='proportional', create_colorbar=True,
                             cbar_full_width=False):
    ''' Create the mpl_colors_info dictionary directly from passed arguments

    Args:
        cmap (Colormap) : This is a valid matplotlib cm Colormap object that can be used for both plotting and colorbar
                            creation
        norm (Normalize) : This is a valid matplotlib Normalize object that can be used for both plotting and colorbar
                            creation.
        cbar_ticks (list) : List of values where tick marks should be placed on colorbar
        boundaries (list) :  List of boundaries to use in matplotlib plotting and oclorbar creation
        cbar_spacing (string) : Default 'proportional': One of 'proportional' or 'uniform'
        colorbar (bool) : True if colorbar should be created with the set of color info, False otherwise
        cbar_full_width (bool) : default False, True if colorbar should be full width of figure, center 50% if False

    Returns:
        (dict) : Dictionary of mpl_colors_info for use in plotting and colorbar creation.
    '''

    mpl_colors_info = {}
    mpl_colors_info['cmap'] = cmap
    mpl_colors_info['norm'] = norm
    mpl_colors_info['cbar_ticks'] = cbar_ticks
    mpl_colors_info['cbar_tick_labels'] = cbar_tick_labels
    mpl_colors_info['cbar_label'] = cbar_label
    mpl_colors_info['boundaries'] = boundaries
    mpl_colors_info['cbar_spacing'] = cbar_spacing
    mpl_colors_info['colorbar'] = create_colorbar
    mpl_colors_info['cbar_full_width'] = cbar_full_width
    return mpl_colors_info


def set_matplotlib_colors_standard(data_range, cmap_name='Greys', cbar_label=None, create_colorbar=True):
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

    min_val = data_range[0]
    max_val = data_range[1]
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


def set_matplotlib_colors_rgb():
    ''' For rgb imagery, we require no color information (it is entirely specified by the RGB(A) arrays)
    
    Args:
        No arguments

    Returns:
        mpl_colors_info (dict) Specifies matplotlib Colors parameters for use in both plotting and colorbar generation
                               For RGBA arrays, all fields are "None"
    '''
    mpl_colors_info = {'cmap': None,
                       'norm': None,
                       'cbar_ticks': None,
                       'cbar_tick_labels': None,
                       'cbar_label': None,
                       'boundaries': None,
                       'cbar_spacing': 'proportional',
                       'colorbar': False}
    return mpl_colors_info

def set_matplotlib_colors_150H(min_tb=110, max_tb=310):

    from geoips2.image_utils.colormaps import create_linear_segmented_colormap
    transition_vals = [(min_tb, 130),
                       (130, 160),
                       (160, 180),
                       (180, 210),
                       (210, 230),
                       (230, 250),
                       (250, 270),
                       (270, 290),
                       (290, max_tb)]
    transition_colors = [('black', 'blue'),
                         ('blue', 'cyan'),
                         ('cyan', 'green'),
                         ('green', 'yellow'),
                         ('yellow', 'orange'),
                         ('orange', 'red'),
                         ('red', 'maroon'),
                         ('maroon', 'darkmagenta'),
                         ('darkmagenta', 'white')]

    #ticks = [xx[0] for xx in transition_vals]

    #special selection of label

    ticks = [110, 130, 150, 170, 190, 210, 230, 250, 270, 290, 310]
  
    # selection of min and max values for colormap if needed
    min_tb = transition_vals[0][0]
    max_tb = transition_vals[-1][1]

    LOG.info('Setting cmap')
    mpl_cmap = create_linear_segmented_colormap('150h_cmap',
                                                min_tb,
                                                max_tb,
                                                transition_vals,
                                                transition_colors)

    LOG.info('Setting norm')
    from matplotlib.colors import Normalize
    mpl_norm = Normalize(vmin=min_tb, vmax=max_tb)

    cbar_label = 'TB (K)'

    # Must be uniform or proportional, None not valid for Python 3
    cbar_spacing = 'proportional'
    mpl_tick_labels = None
    mpl_boundaries = None

    # from geoips2.image_utils.mpl_utils import create_colorbar
    # only create colorbar for final imagery
    # cbar = create_colorbar(fig, mpl_cmap, mpl_norm, ticks, cbar_label=cbar_label)
    mpl_colors_info = {'cmap': mpl_cmap,
                       'norm': mpl_norm,
                       'cbar_ticks': ticks,
                       'cbar_tick_labels': mpl_tick_labels,
                       'cbar_label': cbar_label,
                       'boundaries': mpl_boundaries,
                       'cbar_spacing': cbar_spacing,
                       'colorbar': True}

    return mpl_colors_info

def set_matplotlib_colors_89H(min_tb=105, max_tb=305):

    from geoips2.image_utils.colormaps import create_linear_segmented_colormap
    transition_vals = [(min_tb, 125),
                       (125, 150),
                       (150, 175),
                       (175, 212),
                       (212, 230),
                       (230, 250),
                       (250, 265),
                       (265, 280),
                       (280, max_tb)]
    transition_colors = [('orange', 'chocolate'),
                         ('chocolate', 'indianred'),
                         ('indianred', 'firebrick'),
                         ('firebrick', 'red'),
                         ('gold', 'yellow'),
                         ('lime', 'limegreen'),
                         ('deepskyblue', 'blue'),
                         ('navy', 'slateblue'),
                         ('magenta', 'white')]

    #ticks = [xx[0] for xx in transition_vals]

    #special selection of label

    ticks = [105, 125, 150, 175, 200, 225, 250, 275, 305]
  
    # selection of min and max values for colormap if needed
    min_tb = transition_vals[0][0]
    max_tb = transition_vals[-1][1]

    LOG.info('Setting cmap')
    mpl_cmap = create_linear_segmented_colormap('89h_cmap',
                                                min_tb,
                                                max_tb,
                                                transition_vals,
                                                transition_colors)

    LOG.info('Setting norm')
    from matplotlib.colors import Normalize
    mpl_norm = Normalize(vmin=min_tb, vmax=max_tb)

    cbar_label = 'TB (K)'

    # Must be uniform or proportional, None not valid for Python 3
    cbar_spacing = 'proportional'
    mpl_tick_labels = None
    mpl_boundaries = None

    # from geoips2.image_utils.mpl_utils import create_colorbar
    # only create colorbar for final imagery
    # cbar = create_colorbar(fig, mpl_cmap, mpl_norm, ticks, cbar_label=cbar_label)
    mpl_colors_info = {'cmap': mpl_cmap,
                       'norm': mpl_norm,
                       'cbar_ticks': ticks,
                       'cbar_tick_labels': mpl_tick_labels,
                       'cbar_label': cbar_label,
                       'boundaries': mpl_boundaries,
                       'cbar_spacing': cbar_spacing,
                       'colorbar': True}

    # return cbar, min_tb, max_tb
    return mpl_colors_info


def set_matplotlib_colors_37pct(min_tb=230, max_tb=280):

    from geoips2.image_utils.colormaps import create_linear_segmented_colormap
    transition_vals = [(min_tb, 240),
                       (240, 260),
                       (260, max_tb)]
    transition_colors = [('cyan', 'yellow'),
                         ('yellow', 'red'),
                         ('red', 'darkred')]

    #special selection of label

    ticks = [230, 240, 250, 260, 270, 280]
  
    # selection of min and max values for colormap if needed
    min_tb = transition_vals[0][0]
    max_tb = transition_vals[-1][1]

    LOG.info('Setting cmap')
    mpl_cmap = create_linear_segmented_colormap('37pct_cmap',
                                                min_tb,
                                                max_tb,
                                                transition_vals,
                                                transition_colors)

    LOG.info('Setting norm')
    from matplotlib.colors import Normalize
    mpl_norm = Normalize(vmin=min_tb, vmax=max_tb)

    cbar_label = 'TB (K)'

    # Must be uniform or proportional, None not valid for Python 3
    cbar_spacing = 'proportional'
    mpl_tick_labels = None
    mpl_boundaries = None

    # from geoips2.image_utils.mpl_utils import create_colorbar
    # only create colorbar for final imagery
    # cbar = create_colorbar(fig, mpl_cmap, mpl_norm, ticks, cbar_label=cbar_label)
    mpl_colors_info = {'cmap': mpl_cmap,
                       'norm': mpl_norm,
                       'cbar_ticks': ticks,
                       'cbar_tick_labels': mpl_tick_labels,
                       'cbar_label': cbar_label,
                       'boundaries': mpl_boundaries,
                       'cbar_spacing': cbar_spacing,
                       'colorbar': True}

    # return cbar, min_tb, max_tb
    return mpl_colors_info

def set_matplotlib_colors_IR(min_tb=-90, max_tb=30):

    # for Infrared images at 11 um.  Unit: Celsius

    if min_tb > -90 or max_tb < 30:
        raise('Infrared TB range must include -90 and 30')

    from geoips2.image_utils.colormaps import create_linear_segmented_colormap
    transition_vals = [(min_tb, -80),
                       (-80, -70),
                       (-70, -50),
                       (-50, -40),
                       (-40, -30),
                       (-30, -15),
                       (-15,   0),
                       (  0,  15),
                       ( 15, max_tb)]
    transition_colors = [('darkorange', 'yellow'),
                         ('darkred', 'red'),
                         ('green', 'palegreen'),
                         ('navy', 'royalblue'),
                         ('royalblue','deepskyblue'),
                         ('whitesmoke', 'silver'),
                         ('silver','grey'),
                         ('grey','dimgrey'),
                         ('dimgrey', 'black')]

    #ticks = [int(xx[0]) for xx in transition_vals]

    #special selection of label

    ticks = [min_tb, -80, -70, -60,-50, -40, -30, -20, -10, 0, 10, 20, 30, max_tb]
  
    # selection of min and max values for colormap if needed
    min_tb = transition_vals[0][0]
    max_tb = transition_vals[-1][1]
    ticks = ticks + [int(max_tb)]

    LOG.info('Setting cmap')
    mpl_cmap = create_linear_segmented_colormap('89pct_cmap',
                                                min_tb,
                                                max_tb,
                                                transition_vals,
                                                transition_colors)

    LOG.info('Setting norm')
    from matplotlib.colors import Normalize
    mpl_norm = Normalize(vmin=min_tb, vmax=max_tb)

    cbar_label = '11um BT (C)'

    # Must be uniform or proportional, None not valid for Python 3
    cbar_spacing = 'proportional'
    mpl_tick_labels = None
    mpl_boundaries = None

    # from geoips2.image_utils.mpl_utils import create_colorbar
    # only create colorbar for final imagery
    # cbar = create_colorbar(fig, mpl_cmap, mpl_norm, ticks, cbar_label=cbar_label)
    mpl_colors_info = {'cmap': mpl_cmap,
                       'norm': mpl_norm,
                       'cbar_ticks': ticks,
                       'cbar_tick_labels': mpl_tick_labels,
                       'cbar_label': cbar_label,
                       'boundaries': mpl_boundaries,
                       'cbar_spacing': cbar_spacing,
                       'colorbar': True,
                       'cbar_full_width': True}

    # return cbar, min_tb, max_tb
    return mpl_colors_info

def set_matplotlib_colors_89pct(min_tb=105, max_tb=280):

    if min_tb >= 125 or max_tb <= 265:
        raise('89pct range must include 125 and 265')

    from geoips2.image_utils.colormaps import create_linear_segmented_colormap
    transition_vals = [(min_tb, 125),
                       (125, 150),
                       (150, 175),
                       (175, 212),
                       (212, 230),
                       (230, 250),
                       (250, 265),
                       (265, max_tb)]
                       # (280, max_tb)]
    transition_colors = [('orange', 'chocolate'),
                         ('chocolate', 'indianred'),
                         ('indianred', 'firebrick'),
                         ('firebrick', 'red'),
                         ('gold', 'yellow'),
                         ('lime', 'limegreen'),
                         ('deepskyblue', 'blue'),
                         ('navy', 'slateblue')]
                         # ('magenta', 'white')]

    ticks = [int(xx[0]) for xx in transition_vals]

    #special selection of label

    # ticks = [min_tb, 125, 150, 175, 200, 225, 250, 275, max_tb]
  
    # selection of min and max values for colormap if needed
    min_tb = transition_vals[0][0]
    max_tb = transition_vals[-1][1]
    ticks = ticks + [int(max_tb)]

    LOG.info('Setting cmap')
    mpl_cmap = create_linear_segmented_colormap('89pct_cmap',
                                                min_tb,
                                                max_tb,
                                                transition_vals,
                                                transition_colors)

    LOG.info('Setting norm')
    from matplotlib.colors import Normalize
    mpl_norm = Normalize(vmin=min_tb, vmax=max_tb)

    cbar_label = 'TB (K)'

    # Must be uniform or proportional, None not valid for Python 3
    cbar_spacing = 'proportional'
    mpl_tick_labels = None
    mpl_boundaries = None

    # from geoips2.image_utils.mpl_utils import create_colorbar
    # only create colorbar for final imagery
    # cbar = create_colorbar(fig, mpl_cmap, mpl_norm, ticks, cbar_label=cbar_label)
    mpl_colors_info = {'cmap': mpl_cmap,
                       'norm': mpl_norm,
                       'cbar_ticks': ticks,
                       'cbar_tick_labels': mpl_tick_labels,
                       'cbar_label': cbar_label,
                       'boundaries': mpl_boundaries,
                       'cbar_spacing': cbar_spacing,
                       'colorbar': True,
                       'cbar_full_width': True}

    # return cbar, min_tb, max_tb
    return mpl_colors_info


def set_matplotlib_colors_37H(min_tb=125, max_tb=300):

    if min_tb >= 185 or max_tb <= 280:
        raise('89pct range must include 125 and 265')

    from geoips2.image_utils.colormaps import create_linear_segmented_colormap
    transition_vals = [(min_tb, 185),
                       (185, 210),
                       (210, 240),
                       (240, 260),
                       (260, 280),
                       (280, max_tb)]
    transition_colors = [('lightyellow', 'darkmagenta'),
                         ('purple', 'cyan'),
                         ('cyan', 'yellow'),
                         ('yellow', 'red'),
                         ('red', 'darkred'),
                         ('silver', 'black')]

    ticks = [xx[0] for xx in transition_vals]

    #special selection of label

    # ticks = [125, 150, 175, 200, 225, 250, 275, 300]
  
    # selection of min and max values for colormap if needed
    min_tb = transition_vals[0][0]
    max_tb = transition_vals[-1][1]
    ticks = ticks + [int(max_tb)]

    LOG.info('Setting cmap')
    mpl_cmap = create_linear_segmented_colormap('37h_cmap',
                                                min_tb,
                                                max_tb,
                                                transition_vals,
                                                transition_colors)

    LOG.info('Setting norm')
    from matplotlib.colors import Normalize
    mpl_norm = Normalize(vmin=min_tb, vmax=max_tb)

    cbar_label = 'TB (K)'

    # Must be uniform or proportional, None not valid for Python 3
    cbar_spacing = 'proportional'
    mpl_tick_labels = None
    mpl_boundaries = None

    # from geoips2.image_utils.mpl_utils import create_colorbar
    # only create colorbar for final imagery
    # cbar = create_colorbar(fig, mpl_cmap, mpl_norm, ticks, cbar_label=cbar_label)
    mpl_colors_info = {'cmap': mpl_cmap,
                       'norm': mpl_norm,
                       'cbar_ticks': ticks,
                       'cbar_tick_labels': mpl_tick_labels,
                       'cbar_label': cbar_label,
                       'boundaries': mpl_boundaries,
                       'cbar_spacing': cbar_spacing,
                       'colorbar': True,
                       'cbar_full_width': True}

    # return cbar, min_tb, max_tb
    return mpl_colors_info

def set_matplotlib_colors_rain(min_tb=0, max_tb=50):

    '''
    from geoips2.image_utils.colormaps import create_linear_segmented_colormap
    transition_vals = [(min_tb, 0.1),
                       (0.1, 0.2),
                       (0.2, 0.3),
                       (0.3, 0.5),
                       (0.5, 1),
                       (1, 2),
                       (2, 3),
                       (3, 5),
                       (5, 10),
                       (10, 15),
                       (15, 20),
                       (20, 30),
                       (30, 40),
                       (40, 49.9),
                       (49.9, max_tb)]
    transition_colors = [('white', 'silver'),
                         ('slategray', 'slategray'),
                         ('navy', 'navy'),
                         ('blue', 'blue'),
                         ('royalblue', 'royalblue'),
                         ('cyan', 'cyan'),
                         ('limegreen', 'limegreen'),
                         ('green', 'green'),
                         ('yellow', 'yellow'),
                         ('gold', 'gold'),
                         ('lightsalmon', 'lightsalmon'),
                         ('coral', 'coral'),
                         ('red', 'red'),
                         ('firebrick', 'firebrick'),
                         ('maroon', 'black')]

    #ticks = [xx[0] for xx in transition_vals]

    #special selection of label

    ticks = [0, 0.5, 1, 2, 3, 5, 10, 15, 20, 30, 40, 50]
    #ticks = [0, 1, 2, 3, 5, 10, 15, 20, 30, 40, 50]
  
    # selection of min and max values for colormap if needed
    min_tb = transition_vals[0][0]
    max_tb = transition_vals[-1][1]

    LOG.info('Setting cmap')
    mpl_cmap = create_linear_segmented_colormap('rain_cmap',
                                                min_tb,
                                                max_tb,
                                                transition_vals,
                                                transition_colors)
    '''
    if min_tb >= 0.1 or max_tb <= 40:
        raise('Rain rate range must include 0.1 and 40')
    ticks = [min_tb, 0.1, 0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 15, 20, 30, 40, max_tb]
    colorlist=['silver','slategray','navy','blue','royalblue','cyan','limegreen','green',
               'yellow','gold','lightsalmon','coral','red','maroon','black']
    mpl_cmap = matplotlib.colors.ListedColormap(colorlist,N=len(colorlist))

    LOG.info('Setting norm')
    from matplotlib.colors import BoundaryNorm
    bounds = (ticks + [max_tb + 1])
    mpl_norm =  BoundaryNorm(bounds,mpl_cmap.N)

    cbar_label = r'Rainrate $(mm hr^{-1})$'

    # Must be uniform or proportional, None not valid for Python 3
    cbar_spacing = 'uniform'           # for discrete bounds of a  color bar
    mpl_tick_labels = None
    mpl_boundaries = None

    # from geoips2.image_utils.mpl_utils import create_colorbar
    # only create colorbar for final imagery
    # cbar = create_colorbar(fig, mpl_cmap, mpl_norm, ticks, cbar_label=cbar_label)
    mpl_colors_info = {'cmap': mpl_cmap,
                       'norm': mpl_norm,
                       'cbar_ticks': ticks,
                       'cbar_tick_labels': mpl_tick_labels,
                       'cbar_label': cbar_label,
                       'boundaries': mpl_boundaries,
                       'cbar_spacing': cbar_spacing,
                       'colorbar': True,
                       'cbar_full_width': True}

    # return cbar, min_tb, max_tb
    return mpl_colors_info

def set_matplotlib_colors_winds(min_wind_speed=0, max_wind_speed=200):
    ''' Generate appropriate matplotlib colors for plotting standard wind speeds.  set_matplotlib_colors_winds
        contains hard coded transition values for different colors, in order to have consistent imagery across all
        sensors / products

    Args:
        min_wind_speed (float) : Default 0
        max_wind_speed (float) : Default 200

    Returns:
        mpl_colors_info (dict) Specifies matplotlib Colors parameters for use in both plotting and colorbar generation
                                See geoips2.image_utils.mpl_utils.create_colorbar for field descriptions.
                                For Wind Speed colors, the following general fields are used:
            mpl_colors_info = {'cmap': (LinearSegmentedColormap)
                               'norm': (Normalize)
                               'cbar_ticks':  (list of transition values for wind speeds)
                               'cbar_tick_labels': (None)
                               'cbar_label': ('Surface Wind (knots)')
                               'boundaries': (None)
                               'cbar_spacing': ('proportional')
                               'colorbar': (True)}
    '''

    from geoips2.image_utils.colormaps import create_linear_segmented_colormap
    transition_vals = [(min_wind_speed, 34),
                       (34, 50),
                       (50, 64),
                       (64, 80),
                       # (64, 72),
                       # (72, 80),
                       (80, 100),
                       (100, 120),
                       (120, 150),
                       (150, max_wind_speed)]
    transition_colors = [('lightblue', 'blue'),
                         ('yellow', 'orange'),
                         ('red', 'red'),

                         # ('thistle', 'thistle'),
                         # ('firebrick', 'firebrick'),
                         # ('fuchsia', 'fuchsia'),
                         # ('mediumvioletred', 'mediumvioletred'),
                         ('rebeccapurple', 'rebeccapurple'),

                         # ('purple', 'rebeccapurple'),
                         # ('rebeccapurple', 'rebeccapurple'),
                         # ('mediumvioletred', 'mediumvioletred'),
                         ('palevioletred', 'palevioletred'),

                         ('silver', 'silver'),
                         ('gray', 'gray'),
                         ('dimgray', 'dimgray')]

    ticks = [xx[0] for xx in transition_vals]

    min_wind_speed = transition_vals[0][0]
    max_wind_speed = transition_vals[-1][1]

    LOG.info('Setting cmap')
    mpl_cmap = create_linear_segmented_colormap('windspeed_cmap',
                                                min_wind_speed,
                                                max_wind_speed,
                                                transition_vals,
                                                transition_colors)

    LOG.info('Setting norm')
    from matplotlib.colors import Normalize
    mpl_norm = Normalize(vmin=min_wind_speed, vmax=max_wind_speed)

    cbar_label = 'Surface Wind (knots)'

    # Must be uniform or proportional, None not valid for Python 3
    cbar_spacing = 'proportional'
    mpl_tick_labels = None
    mpl_boundaries = None

    # from geoips2.image_utils.mpl_utils import create_colorbar
    # only create colorbar for final imagery
    # cbar = create_colorbar(fig, mpl_cmap, mpl_norm, ticks, cbar_label=cbar_label)
    mpl_colors_info = {'cmap': mpl_cmap,
                       'norm': mpl_norm,
                       'cbar_ticks': ticks,
                       'cbar_tick_labels': mpl_tick_labels,
                       'cbar_label': cbar_label,
                       'boundaries': mpl_boundaries,
                       'cbar_spacing': cbar_spacing,
                       'colorbar': True}

    # return cbar, min_wind_speed, max_wind_speed
    return mpl_colors_info


def get_title_string_from_objects(area_def, xarray_obj, product_name_title, product_datatype_title=None,
                                  bg_xarray=None, bg_product_name_title=None, bg_datatype_title=None):
    from geoips2.filenames.base_paths import PATHS as gpaths
    from geoips2.sector_utils.utils import is_sector_type
    if product_datatype_title is None:
        product_datatype_title = '{0} {1}'.format(xarray_obj.platform_name.upper(), xarray_obj.source_name.upper())
    if bg_xarray is not None and bg_datatype_title is None:
        bg_datatype_title = '{0} {1}'.format(bg_xarray.platform_name.upper(), bg_xarray.source_name.upper())
    if is_sector_type(area_def, 'atcf'):
        LOG.info('Setting dynamic title')

        # Make sure we reflect the actual start_datetime in the filename
        # geoimg_obj.set_geoimg_attrs(start_dt=xarray_obj.start_datetime)

        title_line1 = '{0}{1:02d} {2} at {3}, {4}'.format(area_def.sector_info['storm_basin'],
                                                     int(area_def.sector_info['storm_num']),
                                                     area_def.sector_info['storm_name'],
                                                     area_def.sector_info['synoptic_time'],
                                                     gpaths['GEOIPS_COPYRIGHT'])

        # pandas dataframes seem to handle time objects much better than xarray.
        title_line2 = '{0} {1} at {2}'.format(product_datatype_title,
                                              product_name_title,
                                              xarray_obj.start_datetime)
        if bg_xarray is not None:
            title_line3 = '{0} {1} at {2}'.format(bg_datatype_title,
                                                  bg_product_name_title,
                                                  bg_xarray.start_datetime)
            title_string = '{0}\n{1}\n{2}'.format(title_line1, title_line2, title_line3)
        else:
            title_string = '{0}\n{1}'.format(title_line1, title_line2)
        LOG.info('title_string: %s', title_string)
    else:
        title_line1 = '{0} {1}'.format(product_datatype_title,
                                       product_name_title)
        title_line2 = '{0} {1}'.format(xarray_obj.start_datetime.strftime('%Y/%m/%d %H:%M:%SZ'),
                                       gpaths['GEOIPS_COPYRIGHT'])
        if bg_xarray is not None:
            title_line3 = '{0} {1} at {2}'.format(bg_datatype_title,
                                                  bg_product_name_title,
                                                  bg_xarray.start_datetime)
            title_string = '{0}\n{1}\n{2}'.format(title_line1, title_line2, title_line3)
        else:
            title_string = '{0}\n{1}'.format(title_line1, title_line2)
        LOG.info('Not dynamic, using standard title_string: %s', title_string)
    return title_string


def plot_image(main_ax, data, mapobj, mpl_colors_info):
    ''' Plot the "data" array and map in the matplotlib "main_ax"

        Args:
            main_ax (Axes) : matplotlib Axes object for plotting data and overlays 
            data (numpy.ndarray) : Numpy array of data to plot
            mapobj (Map Object) : Basemap or Cartopy CRS instance 
            mpl_colors_info (dict) Specifies matplotlib Colors parameters for use in both plotting and colorbar
                                   See geoips2.image_utils.mpl_utils.create_colorbar for field descriptions.
       Returns:
            No return values
    '''
    # main_ax.set_aspect('auto')

    LOG.info('imshow')
    import numpy
    from geoips2.image_utils.maps import is_crs
    if is_crs(mapobj):
        import matplotlib.pyplot as plt
        # Apparently cartopy handles the flipud
        plt.imshow(data,
                   transform=mapobj,
                   extent=mapobj.bounds,
                   cmap=mpl_colors_info['cmap'],
                   norm=mpl_colors_info['norm'])
    else:
        mapobj.imshow(numpy.flipud(data),
                      ax=main_ax,
                      cmap=mpl_colors_info['cmap'],
                      norm=mpl_colors_info['norm'],
                      aspect='auto')

    return mapobj


def create_figure_and_main_ax_and_mapobj(x_size, y_size, area_def,
                                         font_size=None, existing_mapobj=None, noborder=False):
    ''' Create a figure of x pixels horizontally and y pixels vertically. Use information from matplotlib.rcParams
        xsize = (float(x_size)/dpi)/(right_margin - left_margin)
        ysize = (float(y_size)/dpi)/(top_margin - bottom_margin)
        fig = plt.figure(figsize=[xsize, ysize])
        Parameters:
            x_size (int): number pixels horizontally
            y_size (int): number pixels vertically
            area_def (AreaDefinition) : pyresample AreaDefinition object - used for
                                        initializing map object (basemap or cartopy)
            existing_mapobj (CRS or basemap) : Default None: If specified, do not regenerate mapobj. If None, create
                                                             CRS or basemap object from specified area_def.
            noborder (bool) : Default False: If true, use [0, 0, 1, 1] for axes (allowing for image exact shape of
                                             sector).
        Return:
            (matplotlib.figure.Figure, matplotlib.axes._axes.Axes, mapobject)
                matplotlib Figure object to subsequently use for plotting imagery / colorbars / etc
                matplotlib Axes object corresponding to the single main plotting area.
                cartopy crs or Basemap object for plotting
    '''

    import matplotlib
    matplotlib.use('agg')
    rc_params = matplotlib.rcParams
    import matplotlib.pyplot as plt

    set_fonts(y_size, font_size=font_size)

    # Gather needed rcParam constants
    dpi = rc_params['figure.dpi']

    # I can't seem to get a clean image with no border unless the ax fills the whole figure.
    # Titles / labels don't show up unless we use figure.subplot rc_params
    # It does not appear to be possible to plot the image only once for both the clean and annotated image.
    if noborder:
        left_margin = 0.0
        right_margin = 1.0
        bottom_margin = 0.0
        top_margin = 1.0
    else:
        left_margin = rc_params['figure.subplot.left']   # Fractional distance from left edge of figure for subplot
        right_margin = rc_params['figure.subplot.right']  # Fractional distance from right edge of figure for subplot
        bottom_margin = rc_params['figure.subplot.bottom']  # Fractional distance from bottom edge of figure for subplot
        top_margin = rc_params['figure.subplot.top']     # Fractional distance from top edge of figure for subplot

    xsize = (float(x_size)/dpi)/(right_margin - left_margin)
    ysize = (float(y_size)/dpi)/(top_margin - bottom_margin)
    LOG.info('Creating figure: left, right, bottom, top, xsize, ysize %s %s %s %s %s %s',
             left_margin, right_margin, bottom_margin, top_margin, xsize, ysize)

    fig = plt.figure(frameon=False)
    fig.set_size_inches(xsize, ysize)
    set_fonts(y_size, font_size=font_size)

    if existing_mapobj is None:
        LOG.info('creating mapobj instance')
        from geoips2.image_utils.maps import area_def2mapobj
        mapobj = area_def2mapobj(area_def)
    else:
        LOG.info('mapobj already exists, not recreating')
        mapobj = existing_mapobj

    from geoips2.image_utils.maps import is_crs
    LOG.info('Creating main ax: left, bottom, width, height %s %s %s %s',
             left_margin, bottom_margin, right_margin - left_margin, top_margin - bottom_margin)
    if is_crs(mapobj):
        main_ax = fig.add_axes([left_margin,
                                bottom_margin,
                                right_margin - left_margin,
                                top_margin - bottom_margin],
	    						projection=mapobj
                               )
    else:
        # main_ax = fig.add_axes([left_margin,
        #                         bottom_margin,
        #                         right_margin - left_margin,
        #                         top_margin - bottom_margin],
        #                        )
        main_ax = plt.Axes(fig, [left_margin, bottom_margin, right_margin-left_margin, top_margin-bottom_margin])
    main_ax.set_axis_off()
    fig.add_axes(main_ax)

    return fig, main_ax, mapobj


def set_fonts(figure_y_size, font_size=None):
    ''' Set the fonts in the matplotlib.rcParams dictionary, using matplotlib.rc
        Parameters:
            figure_y_size (int): Font size set relative to number of pixels in the y direction
        No return values
    '''
    import matplotlib
    matplotlib.use('agg')
    mplrc = matplotlib.rc

    # Update font size based on number of lines
    if font_size is not None:
        title_fsize = font_size
    elif int(figure_y_size)/1000 != 0:
        title_fsize = 20*int(figure_y_size)/1000
    else:
        title_fsize = 20

    font = {'family': 'sans-serif',
            'weight': 'bold',
            'size': title_fsize}

    LOG.info('Setting font size to %s for figure_y_size %s', title_fsize, figure_y_size)
    mplrc('font', **font)


def set_title(ax, title_string, figure_y_size, xpos=None, ypos=None, fontsize=None):
    ''' Set the title on figure axis "ax" to string "title_string" 
        Parameters:
            ax (Axes): matplotlib.axes._axes.Axes object to add the title
            title_string (str): string specifying title to attach to axis "ax"
            figure_y_size (int): vertical size of the image, used to proportionally set the title size
        No returns
    '''
    import matplotlib
    matplotlib.use('agg')
    rc_params = matplotlib.rcParams

    # Provide pad room between characters
    fontspace = rc_params['font.size']
    title_line_space = float(fontspace) / figure_y_size
    # num_title_lines = len(title_string.split('\n'))

    if xpos is None:
        xpos = 0.5          # This centers the title
    if ypos is None:
        # ypos = 1 + title_line_space*2
        ypos = 1 + title_line_space*2 # This is relative to main_ax, so greater than 1.
    LOG.info('Setting title: font size %s, xpos %s ypos %s, title_line_space %s',
             fontspace, xpos, ypos, title_line_space)
    LOG.info('    Title string: %s', title_string)
    ax.set_title(title_string, position=[xpos, ypos], fontsize=fontsize)


def create_colorbar(fig, mpl_colors_info):
    '''Routine to create a single colorbar with specified matplotlib ColorbarBase parameters
       cbar_ax = fig.add_axes([<cbar_start_pos>, <cbar_bottom_pos>, <cbar_width>, <cbar_height>])
       cbar = matplotlib.colorbar.ColorbarBase(cbar_ax, cmap=mpl_cmap, extend='both', orientation='horizontal',
                                               norm=cmap_norm, ticks=cmap_ticks, boundaries=cmap_boundaries,
                                               spacing=cmap_spacing)
       cbar.set_label(cbar_label, size=fontsize)

        Parameters:
            fig (Figure): matplotlib.figure.Figure object to attach the colorbar - the colorbar will create its own ax
            mpl_colors_info (dict) : Dictionary of matplotlib Color information, required fields below
                mpl_colors_info['cmap'] (Colormap): matplotlib.colors.Colormap object (LinearSegmentedColormap, etc)
                                                    - this is used to plot the image and to generated the colorbar
                mpl_colors_info['norm'] (Normalize): matplotlib.colors.Normalize object (BoundaryNorm, Normalize, etc)
                                                    - again, this should be used to plot the data also
                mpl_colors_info['cbar_ticks'] (list): list of floats - values requiring tick marks on the colorbar
                mpl_colors_info['cbar_tick_labels'] (list): list of values to use to label tick marks, if other than
                                                            found in cmap_ticks
                mpl_colors_info['boundaries'] (list): if cmap_norm is BoundaryNorm, list of boundaries for discrete
                                                      colors
                mpl_colors_info['cbar_spacing (string): DEFAULT 'proportional', 'uniform' or 'proportional'
                mpl_colors_info['cbar_label (string): string label for colorbar
                mpl_colors_info['colorbar']: (bool) True if a colorbar should be included in the image, False if no cbar
        Returns:
            (matplotlib.colorbar.ColorbarBase): This will have all the pertinent information for ensuring plot and
                                                colorbar use the same parameters
    '''
    cmap_ticklabels = mpl_colors_info['cbar_tick_labels']
    cmap_ticks = mpl_colors_info['cbar_ticks']
    cmap_norm = mpl_colors_info['norm']
    mpl_cmap = mpl_colors_info['cmap']
    cmap_boundaries = mpl_colors_info['boundaries']
    cmap_spacing = mpl_colors_info['cbar_spacing']
    cbar_label = mpl_colors_info['cbar_label']
    if not cmap_ticklabels:
        cmap_ticklabels = cmap_ticks
    import matplotlib
    rc_params = matplotlib.rcParams
    left_margin = rc_params['figure.subplot.left']    # Fractional distance from left edge of figure for subplot
    right_margin = rc_params['figure.subplot.right']    # Fractional distance from left edge of figure for subplot
    fontsize = rc_params['font.size']

    cbar_start_pos = 2*left_margin
    if 'cbar_full_width' in mpl_colors_info and mpl_colors_info['cbar_full_width'] is True:
        cbar_start_pos = left_margin  # Full width colorbar

    cbar_bottom_pos = 0.05
    cbar_height = 0.020

    cbar_width = 1 - 4*left_margin
    if 'cbar_full_width' in mpl_colors_info and mpl_colors_info['cbar_full_width'] is True:
        cbar_width = right_margin - left_margin  # Full width colorbar

    cbar_labelsize = 'small'
    # [left, bottom, width, height]
    cbar_ax = fig.add_axes([cbar_start_pos, cbar_bottom_pos, cbar_width, cbar_height])
    cbar = matplotlib.colorbar.ColorbarBase(cbar_ax, cmap=mpl_cmap, extend='both', orientation='horizontal',
                                            norm=cmap_norm, ticks=cmap_ticks, boundaries=cmap_boundaries,
                                            spacing=cmap_spacing)
    cbar.set_ticklabels(cmap_ticklabels)
    cbar.ax.tick_params(labelsize=cbar_labelsize)
    if cbar_label:
        cbar.set_label(cbar_label, size=fontsize)
    return cbar
