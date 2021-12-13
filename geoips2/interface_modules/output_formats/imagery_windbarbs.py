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

import os
import logging

LOG = logging.getLogger(__name__)

output_type = 'image_overlay'


def imagery_windbarbs(area_def,
                      xarray_obj,
                      product_name,
                      output_fnames,
                      clean_fname=None,
                      product_name_title=None,
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

    if product_name_title is None:
        product_name_title = product_name
 
    if len(xarray_obj[product_name].shape) == 3:
       speed = xarray_obj[product_name].to_masked_array()[:,:,0]
       direction = xarray_obj[product_name].to_masked_array()[:,:,1]
       rain_flag = xarray_obj[product_name].to_masked_array()[:,:,2]
    else:
       speed = xarray_obj[product_name].to_masked_array()[:,0]
       direction = xarray_obj[product_name].to_masked_array()[:,1]
       rain_flag = xarray_obj[product_name].to_masked_array()[:,2]

    success_outputs = []
    import matplotlib.pyplot as plt         #for windbarbs plot:  plt.barbs()
    from geoips2.image_utils.mpl_utils import create_figure_and_main_ax_and_mapobj
    from geoips2.image_utils.colormap_utils import set_matplotlib_colors_standard
    from geoips2.image_utils.mpl_utils import plot_image, save_image, plot_overlays, create_colorbar
    from geoips2.image_utils.mpl_utils import get_title_string_from_objects, set_title

    if not mpl_colors_info:
        # Create the matplotlib color info dict - the fields in this dictionary (cmap, norm, boundaries,
        # etc) will be used in plot_image to ensure the image matches the colorbar.
        mpl_colors_info = set_matplotlib_colors_standard(data_range=[plot_data.min(), plot_data.max()],
                                                         cmap_name=None,
                                                         cbar_label=None)

    mapobj = None

    # Plot windbarbs
    import numpy
    from matplotlib import colors
    from pyresample import utils
    '''
    lat=xarray_obj['latitude'].to_masked_array()
    lon2=xarray_obj['longitude'].to_masked_array()
    direction=xarray_obj['wind_dir_deg_met'].to_masked_array()
    speed=xarray_obj['wind_speed_kts'].to_masked_array()

    u=speed * numpy.sin((direction+180)*3.1415926/180.0)
    v=speed * numpy.cos((direction+180)*3.1415926/180.0)

    #u=speed * numpy.sin(direction*3.1415926/180.0)
    #v=speed * numpy.cos(direction*3.1415926/180.0)

    '''

    # These should probably be specified in the product dictionary.
    # It will vary per-sensor / data type, these basically only currently work with
    # ASCAT 25 km data.
    # This would also avoid having the product names hard coded in the output module code.
    if product_name == 'windbarbs':
        # Thinning the data points to better display the windbards
        thinning=1                                                    # skip data points
        barblength=5.
        linewidth=1.5
        sizes_dict = dict(height=0.7,
                          spacing=0.3)
        rain_size = 10
    elif product_name == 'wind-ambiguities':
        # Thinning the data points to better display the windbards
        thinning=1                                                   # skip data points
        barblength=5    # Length of individual barbs
        linewidth=2     # Width of individual barbs
        rain_size = 10  # Marker size for rain_flag
        sizes_dict = dict(height=0,
                          spacing=0,
                          width=0,  # flag width, relative to barblength
                          emptybarb=0.5)

    lat=xarray_obj['latitude'].to_masked_array()
    lon2=xarray_obj['longitude'].to_masked_array()
    u=speed * numpy.sin((direction+180)*3.1415926/180.0)
    v=speed * numpy.cos((direction+180)*3.1415926/180.0)

    #convert longitudes to (-180,180)
    # lon=utils.wrap_longitudes(lon2)
    # Must be 0-360 for barbs
    lon = numpy.ma.where(lon2 < 0, lon2 + 360, lon2)

    if len(lat.shape) == 2:
        lat2  =lat[::thinning,::thinning]
        lon2  =lon[::thinning,::thinning]
        u2    =u[::thinning,::thinning]
        v2    =v[::thinning,::thinning]
        speed2=speed[::thinning,::thinning]
        rain_flag2=rain_flag[::thinning, ::thinning]
    elif len(lat.shape) == 1:
        lat2  =lat[::thinning]
        lon2  =lon[::thinning]
        u2    =u[::thinning]
        v2    =v[::thinning]
        speed2=speed[::thinning]
        rain_flag2=rain_flag[::thinning]
    if lat2.min() > 0:
        flip_barb = False
    elif lat2.max() < 0:
        flip_barb = True
    else:
        flip_barb = numpy.ma.where(lat2 > 0, False, True).data
    good_inds = numpy.ma.where(speed2)
    lon2 = lon2[good_inds]
    lat2 = lat2[good_inds]
    u2 = u2[good_inds]
    v2 = v2[good_inds]
    speed2 = speed2[good_inds]
    rain_flag2 = rain_flag2[good_inds]
    rain_inds = numpy.ma.where(rain_flag2)


    from geoips2.image_utils.maps import is_crs
    if clean_fname is not None:
        # Create matplotlib figure and main axis, where the main image will be plotted
        fig, main_ax, mapobj = create_figure_and_main_ax_and_mapobj(area_def.x_size,
                                                                    area_def.y_size,
                                                                    area_def,
                                                                    noborder=True)
        if is_crs(mapobj):
            import cartopy.crs as crs
            # main_ax.extent = area_def.area_extent_ll
            main_ax.set_extent(mapobj.bounds, crs=mapobj)
            # main_ax.extent = mapobj.bounds
            import numpy
            # NOTE this does not work if transform=mapobj.
            # Something about transforming to PlateCarree projection, then
            # reprojecting to mapobj.  I don't fully understand it, but this
            # works beautifully, and transform=mapobj puts all the vectors 
            # in the center of the image.
            main_ax.scatter(x=lon2.data[rain_inds], y=lat2.data[rain_inds],
                            transform=crs.PlateCarree(),
                            marker='D', color='k', s=rain_size, zorder=2)
            main_ax.barbs(lon2.data, lat2.data, u2.data, v2.data, speed2.data,
                          transform=crs.PlateCarree(),
                          pivot='tip',
                          rounding=False,
                          cmap=mpl_colors_info['cmap'], flip_barb=flip_barb,
                          #barb_increments=dict(half=10, full=20, flag=50), 
                          sizes=sizes_dict,
                          length=barblength,
                          linewidth=linewidth,
                          norm=mpl_colors_info['norm'],
                          zorder=1)
        else:
            mapobj.scatter(lon2.data[rain_inds], lat2.data[rain_inds], latlon=True, marker='D', color='k', s=2)
            mapobj.barbs(lon2.data, lat2.data, u2.data, v2.data, speed2.data,
                         pivot='tip',
                         rounding=False,
                         cmap=mpl_colors_info['cmap'], flip_barb=flip_barb,
                         #barb_increments=dict(half=10, full=20, flag=50), 
                         sizes=sizes_dict,
                         length=barblength,
                         norm=colors.Normalize(vmin=0,vmax=200))
        success_outputs += save_image(fig, clean_fname, is_final=False, image_datetime=xarray_obj.start_datetime)

    # Create matplotlib figure and main axis, where the main image will be plotted
    fig, main_ax, mapobj = create_figure_and_main_ax_and_mapobj(area_def.x_size,
                                                                area_def.y_size,
                                                                area_def,
                                                                existing_mapobj=mapobj,
                                                                noborder=False)

    if bg_data is not None:
        if not bg_mpl_colors_info:
            bg_mpl_colors_info = set_matplotlib_colors_standard(data_range=[bg_data.min(), bg_data.max()],
                                                                cmap_name='Greys',
                                                                cbar_label=None,
                                                                create_colorbar=False)
        # Plot the background data on a map
        plot_image(main_ax,
                   bg_data,
                   mapobj,
                   mpl_colors_info=bg_mpl_colors_info)

    # plt.barbs(lon2.data, lat2.data, u2.data, v2.data, speed2.data,
    if is_crs(mapobj):
        import cartopy.crs as crs
        main_ax.set_extent(mapobj.bounds, crs=mapobj)
        # main_ax.extent = area_def.area_extent_ll
        # main_ax.extent = mapobj.bounds
        import numpy
        # NOTE this does not work if transform=mapobj.
        # Something about transforming to PlateCarree projection, then
        # reprojecting to mapobj.  I don't fully understand it, but this
        # works beautifully, and transform=mapobj puts all the vectors 
        # in the center of the image.
        main_ax.scatter(x=lon2.data[rain_inds], y=lat2.data[rain_inds],
                        # transform=mapobj,
                        transform=crs.PlateCarree(),
                        marker='D', color='k', s=rain_size, zorder=2)
        main_ax.barbs(lon2.data, lat2.data, u2.data, v2.data, speed2.data,
                      # transform=mapobj,
                      transform=crs.PlateCarree(),
                      pivot='tip',
                      rounding=False,
                      cmap=mpl_colors_info['cmap'], flip_barb=flip_barb,
                      #barb_increments=dict(half=10, full=20, flag=50), 
                      sizes=sizes_dict,
                      length=barblength,
                      linewidth=linewidth,
                      norm=mpl_colors_info['norm'],
                      zorder=1)
    else:
        mapobj.scatter(lon2.data[rain_inds], lat2.data[rain_inds], latlon=True, marker='D', color='k', s=2)
        mapobj.barbs(lon2.data, lat2.data, u2.data, v2.data, speed2.data,
                     pivot='tip', rounding=False, cmap=mpl_colors_info['cmap'], flip_barb=flip_barb,
                     #barb_increments=dict(half=10, full=20, flag=50), 
                     sizes=sizes_dict,
                     length=barblength, norm=colors.Normalize(vmin=0,vmax=200))
    
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

    if output_fnames is not None:
        for annotated_fname in output_fnames:
            # Save the final image
            success_outputs += save_image(fig, annotated_fname, is_final=True, image_datetime=xarray_obj.start_datetime)

    return success_outputs
