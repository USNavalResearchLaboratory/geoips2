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

''' Module for generating specific colormaps on the fly '''
# Installed Libraries
import logging

LOG = logging.getLogger(__name__)


def create_linear_segmented_colormap(cmapname, min_val, max_val, transition_vals, transition_colors):
    ''' Use argument values to fill in the dict used in LinearSegmentedColormap
        +------------------+-----------+-------------------------------------------------------+
        | Parameters:      | Type:     | Description:                                          |
        +==================+===========+=======================================================+
        | cmapname:        | *str*     | Name to attach to the matplotlib.color ColorMap object|
        +------------------+-----------+-------------------------------------------------------+
        | min_val:         | *float*   | Overall minimum value for the colormap                |
        |                  |           |     Range must be normalized between 0 and 1          |
        +------------------+-----------+-------------------------------------------------------+
        | max_val:         | *float*   | Overall maximum value for the colormap                |
        |                  |           |     Range must be normalized between 0 and 1          |
        |                  |           |                                                       |
        +------------------+-----------+-------------------------------------------------------+
        | transition_vals: | *list*    | A list of value ranges specified as tuples for        |
        |                  |   of      |     generating a specific range of colors             |
        |                  |*tuples*   |     ie [(0, 10), (10, 30), (30, 60)]                  |
        +------------------+-----------+-------------------------------------------------------+
        |transition_colors:| *list*    | A list of color ranges specified as tuples for        |
        |                  |   of      |     generating a specific range of colors             |
        |                  |*tuples*   |     corresponding to the transition_vals specified    |
        |                  |   of      |     above                                             |
        |                  |*colors*   |     ie [('yellow', 'orange'),                         |
        |                  |           |         ('pink', 'red'),                              |
        |                  |           |         ('violet', 'purple')]                         |
        +------------------+-----------+-------------------------------------------------------+

        TRANSITIONPOINT1 = 0.0
        TRANSITIONPOINT4 = 1.0
        cmdict = { 'red' :  ((TRANSITIONPOINT1, IGNORED, 1to2STARTCOLOR),
                         (TRANSITIONPOINT2, 1to2ENDCOLOR, 2to3STARTCOLOR),
                         (TRANSITIONPOINT3, 2to3ENDCOLOR, 3to4STARTCOLOR),
                         (TRANSITIONPOINT4, 3to4ENDCOLOR, IGNORED)),
               'green' :  ((TRANSITIONPOINT1, IGNORED, 1to2STARTCOLOR),
                         (TRANSITIONPOINT2, 1to2ENDCOLOR, 2to3STARTCOLOR),
                         (TRANSITIONPOINT3, 2to3ENDCOLOR, 3to4STARTCOLOR),
                         (TRANSITIONPOINT4, 3to4ENDCOLOR, IGNORED)),

               'blue' :  ((TRANSITIONPOINT1, IGNORED, 1to2STARTCOLOR),
                         (TRANSITIONPOINT2, 1to2ENDCOLOR, 2to3STARTCOLOR),
                         (TRANSITIONPOINT3, 2to3ENDCOLOR, 3to4STARTCOLOR),
                         (TRANSITIONPOINT4, 3to4ENDCOLOR, IGNORED)),
            }
    '''
    from matplotlib.colors import ColorConverter, LinearSegmentedColormap
    # Sort transitions on start_val
    bluetuple = ()
    greentuple = ()
    redtuple = ()
    start_color = None
    end_color = None
    old_end_color = [0, 0, 0]
    for transition_val, transition_color in zip(transition_vals, transition_colors):
        start_val = transition_val[0]
        end_val = transition_val[1]
        tstart_color = transition_color[0]
        tend_color = transition_color[1]
        # Must start with 0.0 !
        transition_point = (start_val - min_val) / float((max_val - min_val))
        cc = ColorConverter()
        # Convert start/end color to string, tuple, whatever matplotlib can use.
        try:
            start_color = cc.to_rgb(str(tstart_color))
        except ValueError:
            # Allow for tuples as well as string representations
            start_color = cc.to_rgb(eval(str(tstart_color)))
        try:
            end_color = cc.to_rgb(str(tend_color))
        except ValueError:
            end_color = cc.to_rgb(eval(str(tend_color)))
        bluetuple += ((transition_point, old_end_color[2], start_color[2]),)
        redtuple += ((transition_point, old_end_color[0], start_color[0]),)
        greentuple += ((transition_point, old_end_color[1], start_color[1]),)
        LOG.info('    Transition point: '+str(transition_point)+': '+str(start_val)+' to '+str(end_val))
        LOG.info('        Start color: %-10s %-40s', str(tstart_color), str(start_color))
        LOG.info('        End color:   %-10s %-40s', str(tend_color), str(end_color))
        old_end_color = end_color
    # Must finish with 1.0 !
    transition_point = (end_val - min_val) / float((max_val - min_val))
    bluetuple += ((transition_point, old_end_color[2], start_color[2]),)
    redtuple += ((transition_point, old_end_color[0], start_color[0]),)
    greentuple += ((transition_point, old_end_color[1], start_color[1]),)

    cmdict = {'red': redtuple,
              'green': greentuple,
              'blue': bluetuple}

    cm = LinearSegmentedColormap(cmapname, cmdict)

    return cm
