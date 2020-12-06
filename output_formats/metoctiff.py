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

#!/usr/bin/env python
''' Create valid metoctiff file from existing image or data '''
#
#  This is the driver routine for creation of a metoctif file for ATCF.

# Standard Python Libraries
import logging
import os

# Installed Libraries
import numpy


try:
    # use these packages to create/modify metoctiffs
    from skimage.external import tifffile as tf
except Exception as err:
    import tifffile as tf

try:
    from PIL import Image
    import gzip
    import shutil
except Exception as err:
    print('error importing image related packages: ', str(err.__doc__))


# This is a display of info from the ATCF app
# *** pSatStuff->                                 ***
# ***       Satellite name =                      ***
# ***       nChannelNumber = 0                    ***
# ***       nWidth = 1024                         ***
# ***       nHeight = 1024                        ***
# ***       nBitsPerPixel = 8                     ***
# ***       nProjection = 4                       ***
# ***       rsStandard1 = 0.000000                ***
# ***       rsStandard2 = 0.000000                ***
# ***       nHemisphere = 1                       ***
# ***       rsBCLat = -0.898740                   ***
# ***       rsBCLon = -172.800003                 ***
# ***       rsUCLat = 17.498739                   ***
# ***       rsUCLon = -172.800003                 ***
# ***       rsULLat = 17.498739                   ***
# ***       rsULLon = 177.903870                  ***
# ***       rsLLLat = -0.898740                   ***
# ***       rsLLLon = 177.903870                  ***
# ***       rsURLat = 17.498739                   ***
# ***       rsURLon = -163.503876                 ***
# ***       rsLRLat = -0.898740                   ***
# ***       rsLRLon = -163.503876                 ***
# ***       szDescription =
# DATA_PLATFORM="himawari-8";DATA_NAME="svissr_ir1";DATA_START_TIME="Mon, 11
# Jan 2016 15:55:24 GMT";DATA_END_TIME="Mon, 11 Jan 2016 15:57:57
# GMT";DATA_UNITS="celcius";DATA_RANGE="0,249,-80,0.441767,None";

LOG = logging.getLogger(__name__)

class METOCTIFFInfo(object):
    '''Object to store dynamically generated header and tag info for METOCTIFF files
              ullat_radians,
              urlat_radians,
              lllat_radians,
              lrlat_radians,
              ullon_radians,
              urlon_radians,
              lllon_radians,
              lrlon_radians,
              data_start_datetime,
              data_end_datetime,
              product_name,
              platform_name,
              data_units,
              output_filename,
              requested_data_min,
              requested_data_max,
              scale_data_min=1,
              scale_data_max=255,
              missing_value=0,
    '''

    def __init__(self):
        self.ullat_radians = None
        self.urlat_radians = None

    @property
    def ullat_radians(self):
        '''Getter method for ullat.'''
        if not hasattr(self, '_ullat_radians'):
            self._ullat_radians = None
        return self._ullat_radians

    @ullat_radians.setter
    def ullat_radians(self, val):
        '''Setter method for ullat.'''
        self._ullat_radians = val

    @property
    def ullon_radians(self):
        '''Getter method for ullon.'''
        if not hasattr(self, '_ullon_radians'):
            self._ullon_radians = None
        return self._ullon_radians

    @ullon_radians.setter
    def ullon_radians(self, val):
        '''Setter method for ullon.'''
        self._ullon_radians = val

    @property
    def urlat_radians(self):
        '''Getter method for urlat.'''
        if not hasattr(self, '_urlat_radians'):
            self._urlat_radians = None
        return self._urlat_radians

    @urlat_radians.setter
    def urlat_radians(self, val):
        '''Setter method for urlat.'''
        self._urlat_radians = val

    @property
    def urlon_radians(self):
        '''Getter method for urlon.'''
        if not hasattr(self, '_urlon_radians'):
            self._urlon_radians = None
        return self._urlon_radians

    @urlon_radians.setter
    def urlon_radians(self, val):
        '''Setter method for urlon.'''
        self._urlon_radians = val


def get_data_from_image(existing_image):
    '''
        If we have a pre-existing image and not actual data, just read the image in, pull the palette from the image,
        and write it back out.  NO VALID QUANTITATIVE INFORMATION, just imagery with proper colors.
        +------------------+-----------+-------------------------------------------------------+
        | Parameters:      | Type:     | Description:                                          |
        +==================+===========+=======================================================+
        |existing_image| *str*        | path to existing image                                |
        |              | *ndarray*    | RGB or RGBA array of 0 to 1                           |
        +------------------+-----------+-------------------------------------------------------+
    '''
    if isinstance(existing_image, str):
        imopen = Image.open
        curr_image = existing_image
    else:
        imopen = Image.fromarray
        curr_image = (existing_image*256).astype(numpy.uint8)
    # convert the full composite png image to a tif palette image and save it out
    try:
        with imopen(curr_image) as img:
            # convert to palette image using the ADAPTIVE palette
            img = img.convert("P", palette=Image.ADAPTIVE, colors=256)

            # get the data from the img
            data = numpy.asarray(img)

            #
            #
            # The item discription string is written to tiff tag 270 and is needed by ATCF
            #

            # data range information is used by atcf to translate pixel intensities to real world data values.
            # formula seems to be sourceDataMin + (PixelIntensity - colorSpaceMin)*(sourceDataMax/colorSpaceMax)
            colorSpaceMax = data.max()
            colorSpaceMin = data.min()

            # get the color map from the img
            # it returns list of color values [r, g, b, ...] but as 8 bit
            palette = img.getpalette()
            # if passing in tag 320 as an extratag, TiffWriter expects a 1d array with all red values,
            # then green values, then blue values of length 2**(data.itemsize*8)
            # if using TiffWriter.save colormap parameter, the object passed must be shape
            # (3, 2**(data.itemsize*8)) and dtype uint16
            r = palette[0::3]
            g = palette[1::3]
            b = palette[2::3]

            # create the object to pass into the colormap parameter of TiffWriter.save
            clrmap256 = numpy.array([r, g, b], dtype=numpy.uint16)
            # move to 16 bit colors
            clrmap = clrmap256 * (65535/255)

            # add the MetocTiff tags and save in the place where GeoIPS MetocTiffs go to live in the wild
            return data, clrmap, [colorSpaceMin, colorSpaceMax], [colorSpaceMin, colorSpaceMax]

    except Exception as err:
        LOG.info('{0}: {1} >> {2}'.format(type(err).__name__, str(err.__doc__), str(err.args)))
        raise

def get_data_from_equations(data_array, mpl_cmap,
                            requested_data_min, requested_data_max,
                            scale_data_min=1, scale_data_max=255, missing_value=0):
    '''
    Get the appropriate 249 colormap for the tiff, apply appropriate data ranges, and normalize data from 0 to 249
        +------------------+-----------+-------------------------------------------------------+
        | Parameters:      | Type:     | Description:                                          |
        +==================+===========+=======================================================+
        | data_array:      | *ndarray* | Array of data to scale properly for metoctiff         |
        +------------------+-----------+-------------------------------------------------------+
        | mpl_cmap:        |*ColorMap* | matplotlib ColorMap object to create 255 color palette|
        |                  |           |     to map the scaled 1-255 data values in the jif    |
        +------------------+-----------+-------------------------------------------------------+
        |requested_data_min| *float*   | Minimum allowed value for the actual data, for norm   |
        |                  |           |                                                       |
        +------------------+-----------+-------------------------------------------------------+
        |requested_data_max| *float*   | Maximum allowed value for the actual data, for norm   |
        |                  |           |                                                       |
        +------------------+-----------+-------------------------------------------------------+
    '''

    # Create a 249 color palette from the passed matplotlib colormap

    # This works for LinearSegmentedColormaps and ListedColormaps. Maybe all???
    # You are basically getting the RGB values for 249 colors within
    # the specified colormap. colormap returns values between 0 and 1, we need uint16, so multiply by 65535

    rgb = mpl_cmap(range(scale_data_min, scale_data_max+1)) * 65535

    red = []
    grn = []
    blu = []

    # Pad with zeros at the beginning
    while len(red) < scale_data_min:
        red += [0]
        grn += [0]
        blu += [0]

    # reassemble the rgb array into r array, g array, b array
    # I'm sure there is a better slicing method for this.
    for currrgb in rgb:
        red += [currrgb[0]]
        grn += [currrgb[1]]
        blu += [currrgb[2]]

    # Pad with zeros at the end
    while len(red) < 256:
        red += [0]
        grn += [0]
        blu += [0]

    if len(red) != 256:
        LOG.info('cmap is not length 256, qualitative imagery only!')
        raise

    # Now create the cmap array format expected by TiffWriter
    # Needs to be uint16, 0-65535, and needs to be
    # [red array, green array, blue array]
    jif_cmap = numpy.array([red, grn, blu], dtype=numpy.uint16)

    # This will normalize between scale_data_min and scale_data_max
    # For the DATA_RANGE tag in the mtif, 1/m is the scaling factor,
    # plus scale_data_min, scale_data_max, and requested_data_min
    m = (float(scale_data_max) - scale_data_min) / (float(requested_data_max) - requested_data_min)
    b = scale_data_min - m * float(requested_data_min)
    scaledata = m * data_array + b
    scaledata = numpy.ma.masked_less(scaledata, scale_data_min)
    scaledata = numpy.ma.masked_greater(scaledata, scale_data_max)

    # Fill with missing value
    scaledata.fill_value = missing_value
    scaledata = scaledata.filled()

    return scaledata, jif_cmap


def metoctiff(data_array,
              ullat_radians,
              urlat_radians,
              lllat_radians,
              lrlat_radians,
              uclat_radians,
              lclat_radians,
              ullon_radians,
              urlon_radians,
              lllon_radians,
              lrlon_radians,
              uclon_radians,
              lclon_radians,
              data_start_datetime,
              data_end_datetime,
              product_name,
              platform_name,
              data_units,
              output_filename,
              requested_data_min,
              requested_data_max,
              scale_data_min=1,
              scale_data_max=255,
              missing_value=0,
              product_description='None',
              mpl_cmap=None,
              existing_image=None,
              gzip_output=False):
    '''
        Generate a metoctiff with valid headers from existing image OR data found in data_array,
        with appropriate colormap, data ranges, tags
        NOTE: If you include the "existing_image" option, it will just read in an arbitrary existing image and plot it
        QUALITATIVELY with the appropriate colormap / lat / lons, but no quantitative information.
        +------------------+-----------+-------------------------------------------------------+
        | Parameters:      | Type:     | Description:                                          |
        +==================+===========+=======================================================+
        | data_array:      | *ndarray* | Array of data to scale properly for metoctiff         |
        +------------------+-----------+-------------------------------------------------------+
        | ullat_radians:   | *float*   | upper left lat of the data_array in radians           |
        |                  |           |            used for metoctiff "extratags" header      |
        +------------------+-----------+-------------------------------------------------------+
        | urlat_radians:   | *float*   | upper right lat of the data_array in radians          |
        |                  |           |            used for metoctiff "extratags" header      |
        +------------------+-----------+-------------------------------------------------------+
        | lllat_radians:   | *float*   | lower left lat of the data_array in radians           |
        |                  |           |            used for metoctiff "extratags" header      |
        +------------------+-----------+-------------------------------------------------------+
        | lrlat_radians:   | *float*   | lower right lat of the data_array in radians          |
        |                  |           |            used for metoctiff "extratags" header      |
        +------------------+-----------+-------------------------------------------------------+
        | ullon_radians:   | *float*   | upper left lon of the data_array in radians           |
        |                  |           |            used for metoctiff "extratags" header      |
        +------------------+-----------+-------------------------------------------------------+
        | urlon_radians:   | *float*   | upper right lon of the data_array in radians          |
        |                  |           |            used for metoctiff "extratags" header      |
        +------------------+-----------+-------------------------------------------------------+
        | lllon_radians:   | *float*   | lower left lon of the data_array in radians           |
        |                  |           |            used for metoctiff "extratags" header      |
        +------------------+-----------+-------------------------------------------------------+
        | lrlon_radians:   | *float*   | lower right lon of the data_array in radians          |
        |                  |           |            used for metoctiff "extratags" header      |
        +------------------+-----------+-------------------------------------------------------+
        |data_start_datetime:|*datetime*| datetime object indicating the data start datetime |
        |                  |           | used for metoctiff "description" header DATA_START_TIME |
        +------------------+-----------+-------------------------------------------------------+
        |data_end_datetime:| *datetime*| datetime object indicating the data end datetime   |
        |                  |           | used for metoctiff "description" header DATA_END_TIME |
        +------------------+-----------+-------------------------------------------------------+
        | product_name:    | *str*     | string of current product name of the data_array      |
        |                  |           | used for metoctiff "description" header DATA_NAME     |
        +------------------+-----------+-------------------------------------------------------+
        | platform_name:   | *str*     | string of current platform name of the data_array     |
        |                  |           | used for metoctiff "description" header PLATFORM_NAME |
        +------------------+-----------+-------------------------------------------------------+
        | data_units:      | *str*     | string of current units of the data_array             |
        |                  |           | used for metoctiff "description" header DATA_UNITS    |
        +------------------+-----------+-------------------------------------------------------+
        | output_filename: | *str*     | string of output filename to write the metoctiff      |
        +------------------+-----------+-------------------------------------------------------+
        |requested_data_min| *float*   | Minimum allowed value for the actual data,            |
        |                  |           |    for scaling from scale_data_min to scale_data_max  |
        |                  |           | metoctiff description tag:                            |
        |                  |           | DATA_RANGE=scale_data_min,                            |
        |                  |           |            scale_data_max,                            |
        |                  |           |            requested_data_min,                        |
        |                  |           |            requested_data_max/scale_data_max          |
        |                  |           |                                                       |
        +------------------+-----------+-------------------------------------------------------+
        |requested_data_max| *float*   | Maximum allowed value for the actual data,            |
        |                  |           |    for scaling from scale_data_min to scale_data_max  |
        |                  |           | metoctiff description tag:                            |
        |                  |           | DATA_RANGE=scale_data_min,                            |
        |                  |           |            scale_data_max,                            |
        |                  |           |            requested_data_min,                        |
        |                  |           |            requested_data_max/scale_data_max          |
        +------------------+-----------+-------------------------------------------------------+
        |scale_data_min    | *uint8*   | Minimum allowed value for the scaled data,            |
        |                  |           |    for scaling from scale_data_min to scale_data_max  |
        |                  | DEFAULT   | metoctiff description tag:                            |
        |                  | 1         | DATA_RANGE=scale_data_min,                            |
        |                  |           |            scale_data_max,                            |
        |                  |           |            requested_data_min,                        |
        |                  |           |            requested_data_max/scale_data_max          |
        |                  |           |                                                       |
        +------------------+-----------+-------------------------------------------------------+
        |scale_data_max    | *uint8*   | Maximum allowed value for the scaled data,            |
        |                  |           |    for scaling from scale_data_min to scale_data_max  |
        |                  | DEFAULT   | metoctiff description tag:                            |
        |                  | 255       | DATA_RANGE=scale_data_min,                            |
        |                  |           |            scale_data_max,                            |
        |                  |           |            requested_data_min,                        |
        |                  |           |            requested_data_max/scale_data_max          |
        +------------------+-----------+-------------------------------------------------------+
        |missing_value     | *uint8*   | Value that ATCF considers missing/bad data,           |
        |                  |           |    between 0 and 255                                  |
        |                  | DEFAULT   | metoctiff description tag:                            |
        |                  | 0         | DATA_RANGE=scale_data_min,                            |
        |                  |           |            scale_data_max,                            |
        |                  |           |            requested_data_min,                        |
        |                  |           |            requested_data_max/scale_data_max          |
        +------------------+-----------+-------------------------------------------------------+
        | mpl_cmap:        |*ColorMap* | matplotlib ColorMap object to create 255 color palette|
        |                  |           |     to map the scaled 1-255 data values in the jif    |
        |                  |           |     !!! ColorMap must match the range specified in    |
        |                  |           |     requested_data_min to requested_data_max          |
        |                  |           |     if you want specific colors to match specific     |
        |                  |           |     values !!!                                        |
        |                  |           |                                                       |
        +------------------+-----------+-------------------------------------------------------+
        |existing_image:   | *str*     | string of full path to an existing image              |
        |                  | *ndarray* | RGB or RGBA array of 0 to 1                           |
        |                  |           |   NOTE: Use of this option basically ignores most     |
        |                  |           |         everything else! Just reads it in and writes  |
        |                  |           |         it back out qualitatively, with the           |
        |                  |           |         appropriate colors and metoctiff headers      |
        +------------------+-----------+-------------------------------------------------------+
        | gzip_output:     |*bool*     | Flag to determine whether to gzip the output          |
        +------------------+-----------+-------------------------------------------------------+
    '''

    output_products = []
    LOG.info('Creating metoctiff image file, gzip_output=%s', gzip_output)

    #
    #  Get the image lat lon corners for the metoctiff extratags
    #  Added the image flip.
    #

    rsULLat = int(numpy.rad2deg(ullat_radians) * 100000)
    rsULLon = int(numpy.rad2deg(ullon_radians) * 100000)

    rsURLat = int(numpy.rad2deg(urlat_radians) * 100000)
    rsURLon = int(numpy.rad2deg(urlon_radians) * 100000)

    rsLLLat = int(numpy.rad2deg(lllat_radians) * 100000)
    rsLLLon = int(numpy.rad2deg(lllon_radians) * 100000)

    rsLRLat = int(numpy.rad2deg(lrlat_radians) * 100000)
    rsLRLon = int(numpy.rad2deg(lrlon_radians) * 100000)

    rsUCLat = int(numpy.rad2deg(uclat_radians) * 100000)
    rsUCLon = int(numpy.rad2deg(uclon_radians) * 100000)

    rsBCLat = int(numpy.rad2deg(lclat_radians) * 100000)
    rsBCLon = int(numpy.rad2deg(lclon_radians) * 100000)

    #
    #  NOTE: We are now passing Center Lat and Center Lon directly -
    #        these calculations fail when crossing the dateline.
    #  Get the center lat lon values of image for the metoctiff extratags
    #

    # rsUCLat = (rsULLat + rsURLat) / 2
    # rsUCLon = (rsULLon + rsURLon) / 2

    # rsBCLat = (rsLLLat + rsLRLat) / 2
    # rsBCLon = (rsLLLon + rsLRLon) / 2

    #
    #  Additional info for extratags required for metocTiff
    #

    nProjection = 4  # 1 = Polar Stereographic 2 = Lambert Conformal 4 = Mercator 8 = Normal.
                     #   It's likely that mercator is analogous to 'cyl' in pyproj'''
    rsStandard1 = 0  # only used if lambert conformal projection is specified
    rsStandard2 = 0  # only used if lambert conformal projection is specified
    if rsBCLat >= 0:
        Hemisphere = 1  # northern
    else:
        Hemisphere = 2  # southern

    # Otherwise, if we passed a existing_image, read it in and grab data from
    # temporary image
    if existing_image is not None:
        scaledata, jif_cmap, requested_bounds, scale_bounds = get_data_from_image(existing_image)
        scale_data_min = scale_bounds[0]
        scale_data_max = scale_bounds[1]
        requested_data_min = requested_bounds[0]
        requested_data_max = requested_bounds[1]
    else:
        scaledata, jif_cmap = get_data_from_equations(data_array,
                                                      mpl_cmap,
                                                      requested_data_min,
                                                      requested_data_max,
                                                      scale_data_min,
                                                      scale_data_max,
                                                      missing_value)

    #
    #  Info for "description" tag included in metoctiff file.
    #  ATCF relies heavily on this description in order to display the tiff correctly
    #

    data_name = product_name
    platform = platform_name

    data_start_dtstr = data_start_datetime.strftime('%a, %d %b %Y %H:%M:%S GMT')
    data_end_dtstr = data_end_datetime.strftime('%a, %d %b %Y %H:%M:%S GMT')

    #
    #  Write out the tiff file with all of the appropriate METOCTiff headers!
    #  Note it appears we need to use little endian order (big endian looks correct,
    #  but doesn't work for interrogating values in ATCF), and uint8
    #
    #  Note: Any data ranges are scaled to 0 to 249 in get_data_from_equations
    #

    # for byteorderstr in ['le', 'be']:
    #     for dtype in ['uint8', 'uint16', 'float64', 'float32']:
    for byteorderstr in ['le']:
        for dtype in ['uint8']:
            if byteorderstr == 'le':
                byteorder = '<'
            elif byteorderstr == 'be':
                byteorder = '>'

            # Just output filename - we've determined little endian, uint8, from data itself is the way to go.
            curr_output_filename = output_filename

            szDescription = 'DATA_PLATFORM="{0}";'.format(platform) + \
                            'DATA_NAME="{0}";'.format(data_name) + \
                            'DATA_START_TIME="{0}";'.format(data_start_dtstr) + \
                            'DATA_END_TIME="{0}";'.format(data_end_dtstr) + \
                            'DATA_UNITS="{0}";'.format(data_units)

            LOG.info('DATA_RANGE tag from %s to %s', requested_data_min, requested_data_max)

            # From def get_data_from_equations
            # m = (float(scale_data_max) - scale_data_min) / (float(requested_data_max) - requested_data_min)
            # b = scale_data_min - m * float(requested_data_min)
            # scaledata = m * data_array + b
            # So realdata = (1/m) * (scaledata - b)
            # DATA range uses the 1/m scaling factor, as well as scale_data_min, scale_data_max, and requested_data_min
            # in order to recover the real data from the scaled values.

            # To determine MAX_DATA_VAL from scaling_term in DATA_RANGE:
            #   scaling_term*(SCALE_DATA_MAX-SCALE_DATA_MIN) + MIN_DATA_VAL
            scaling_term = (float(requested_data_max) - requested_data_min) / (float(scale_data_max) - scale_data_min)

            datarange = 'DATA_RANGE="{0},{1},{2},{3:0.6f},{4}";'.format(scale_data_min,
                                                                        scale_data_max,
                                                                        requested_data_min,
                                                                        scaling_term,
                                                                        product_description)

            # print(datarange)
            szDescription = '{0}{1}'.format(szDescription, datarange)

            scaledata = scaledata.astype(dtype)

            from geoips2.filenames.base_paths import make_dirs
            make_dirs(os.path.dirname(curr_output_filename))
            with tf.TiffWriter(curr_output_filename, byteorder=byteorder) as mtif:
                LOG.info('Writing METOCTIFF jif file: %s...', curr_output_filename)
                mtif.save(scaledata,
                          colormap=jif_cmap,
                          description=szDescription,
                          metadata=None,
                          extratags=[(284, 'H', 1, 1, True),
                                     (33000, 'i', 1, nProjection, True),
                                     (33001, 'i', 1, rsStandard1, True),
                                     (33002, 'i', 1, rsStandard2, True),
                                     (33003, 'i', 1, Hemisphere, True),
                                     (33004, 'i', 1, rsULLat, True),
                                     (33005, 'i', 1, rsULLon, True),
                                     (33006, 'i', 1, rsLLLat, True),
                                     (33007, 'i', 1, rsLLLon, True),
                                     (33008, 'i', 1, rsURLat, True),
                                     (33009, 'i', 1, rsURLon, True),
                                     (33010, 'i', 1, rsLRLat, True),
                                     (33011, 'i', 1, rsLRLon, True),
                                     (33012, 'i', 1, rsBCLat, True),
                                     (33013, 'i', 1, rsBCLon, True),
                                     (33014, 'i', 1, rsUCLat, True),
                                     (33015, 'i', 1, rsUCLon, True)])
                LOG.info('MTIFSUCCESS %s', curr_output_filename)
                output_products = [curr_output_filename]

    # Sanity Check
    LOG.info('Min/Max Left Lat %s %s', rsLLLat/10**5*1.0, rsULLat/10**5*1.0)
    LOG.info('Min/Max Right Lat %s %s', rsLRLat/10**5*1.0, rsURLat/10**5*1.0)
    LOG.info('Bottom/Top Center Lat %s %s', rsBCLat/10**5*1.0, rsUCLat/10**5*1.0)
    LOG.info('Min/Center/Max Lower Lon %s %s %s', rsLLLon/10**5*1.0, rsBCLon/10**5, rsLRLon/10**5*1.0)
    LOG.info('Min/Center/Max Upper Lon %s %s %s', rsULLon/10**5*1.0, rsUCLon/10**5*1.0, rsURLon/10**5*1.0)
    
    if gzip_output is True:
        try:
            #gzip the file and remove original
            LOG.info('Gzipping output to file %s.gz', output_filename)
            with open(output_filename, 'rb') as uncompressedFile, gzip.open(output_filename + '.gz', 'wb') as compressedFile:
                shutil.copyfileobj(uncompressedFile, compressedFile)
            if os.path.isfile(output_filename):
                os.remove(output_filename)
            output_products = [output_filename+'.gz']
        except Exception as err:
            LOG.info('{0}: {1} >> {2}'.format(type(err).__name__,str(err.__doc__),str(err.args)))

    return output_products
