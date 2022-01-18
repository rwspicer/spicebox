"""
raster
------
Input Output operations for rasters
"""
from osgeo import gdal, gdal_array
import numpy as np

ROW, COL = 0,1
import math

import matplotlib.pyplot as plt

from . import transforms

from collections import namedtuple
OLD_STYLE_RASTER_METADATA = namedtuple('RASTER_METADATA', 
    ['transform', 'projection', 
        'nX', 'nY', 'deltaX', 'deltaY', 'originX', 'originY'
    ]
)

def numpy_type_lookup (item):
    try:
        dtype = item.dtype
    except:
        return gdal.GDT_Unknown

    return gdal_array.GDALTypeCodeToNumericTypeCode(dtype.type)

def load_raster (filename,  return_dataset = False, band = 1):
    """Load a raster file and it's metadata
    
    Parameters
    ----------
    filename: str
        path to raster file to read
    return_dataset: bool
        if true return gdal.dataset
        
    Returns 
    -------
    gdal.dataset
        or 
    np.array
        2d raster data
    RASTER_METADATA
        metadata on raster file read
    """
    dataset = gdal.Open(filename, gdal.GA_ReadOnly)
    # (X, deltaX, rotation, Y, rotation, deltaY) = dataset.GetGeoTransform()
    if return_dataset:
        return dataset

    metadata = {
        'transform': dataset.GetGeoTransform(),
        'projection': dataset.GetProjection(),
        'x_size': dataset.RasterXSize,
        'y_size': dataset.RasterYSize,
    }

    data = dataset.GetRasterBand(band).ReadAsArray()
    return data, metadata

def save_raster(filename, data, transform, projection, 
    datatype = gdal.GDT_Float32):
    """Function Docs 
    Parameters
    ----------
    filename: path
        path to file to save
    data: np.array like
        2D array to save
    transform: tuple
        (origin X, X resolution, 0, origin Y, 0, Y resolution) 
    projection: string
        SRS projection in WTK format
    datatype:
        Gdal data type
    
    """
    write_driver = gdal.GetDriverByName('GTiff') 
    raster = write_driver.Create(
        filename, data.shape[1], data.shape[0], 1, datatype
    )
    raster.SetGeoTransform(transform)  
    outband = raster.GetRasterBand(1)  
    outband.WriteArray(data) 
    raster.SetProjection(projection) 
    outband.FlushCache()  
    raster.FlushCache()     

def zoom_box(data, top_left, bottom_right, no_data_val=np.nan):
    """Zoom to a box defined by the top left and bottom right pixel coordinates

    Parameters
    ----------
    data: np.array
        2d raster data
    top_left: tuple
        (row, col) coordinates of top left pixel
    bottom_right: tuple
        (row, col) coordinates of bottom right pixel

    Returns
    -------
    np.array
    """
    row_shift = 0
    if top_left[0] < 0:
        row_shift = abs(top_left[0])
        top_left[0]= 0
        
    col_shift = 0
    if top_left[1] < 0:
        col_shift = abs(top_left[1]) 
        top_left[1] = 0

    new = data[top_left[0]:bottom_right[0], top_left[1]:bottom_right[1]]
    rows, cols = new.shape
    if row_shift != 0 or col_shift !=0:
        resized = np.zeros([rows+row_shift, cols+col_shift]) + no_data_val
        resized[row_shift:, col_shift: ] = new[:,:]
        new = resized
    return new


def zoom_to(data, pixel, radius=50):
    """zooms in on a pixel location

    data: np.array
        2d raster data
    pixel: tuple
        (row, col) coordinates of center point to zoom to
    radius: Int, default 50
        number of pixels around center to include in zoom
    """
    idxs = np.array(pixel) - radius, np.array(pixel)+radius

    if radius == 0:
        zoom = data[pixel[0]:pixel[0]+1,pixel[1]:pixel[1]+1]
        # print(zoom)
        return zoom 
        
    return zoom_box(data, idxs[0], idxs[1])

def get_zoom_box_geotransform(md, top_left, bottom_right):
    """get geotransform for zoom box

    Parameters
    ----------
    md: dict
        raster metadata
    top_left: tuple
        (row, col) coordinates of top left pixel
    bottom_right: tuple
        (row, col) coordinates of bottom right pixel

    Returns
    -------
    tuple of new transform
    """

    origin = top_left[0],  bottom_right[0]

    # if origin[0] < 0:
    #     origin[0] = 0

    # if origin[1] < 0:
    #     origin[1] = 0

    n_oX, n_oY = transforms.to_geo((origin),md['transform'])
    old_t = md['transform']
    new_t = (n_oX, old_t[1], old_t[2], n_oY, old_t[4], old_t[5] )

    return new_t


def get_zoom_geotransform(md, pixel, radius=50):
    """Creates the geotransform for raster created by zoom_to

    parameters
    ----------
    md: dict
        raster metadata
    pixel: tuple
        (row index, col index)
    radius: int

    returns
    -------
    tuple of new transform
    
    """

    origin = np.array(pixel) - radius

    # bounds checking
    if origin[0] < 0:
        origin[0] = 0

    if origin[1] < 0:
        origin[1] = 0
    
    n_oX, n_oY = transforms.to_geo((origin),md['transform'])
    old_t = md['transform']
    new_t = (n_oX, old_t[1], old_t[2], n_oY, old_t[4], old_t[5] )

    return new_t
    


def mask_layer(layer, mask, mask_value = np.nan):
    """apply a mask to a layer 
    layer[mask == True] = mask_value
    """
    layer[mask] = mask_value
    return layer

def clip_raster (in_raster, out_raster, extent, datatpye=gdal.GDT_Float32):
    """Clip a raster to extent
    
    Parameters:
    in_raster: path
        input raster file
    out_raster: path
        output raster file
    extent: tuple
        (minX, maxY, maxX, minY)
    """

    tiff = gdal.Translate(
        out_raster, in_raster, projWin = extent, 
        format='GTiff', outputType=datatpye, noData=np.nan
    ) 
    # printtiff
    tiff.GetRasterBand(1).FlushCache()
    tiff.FlushCache()
    return True


def convert_to_figure(raster_name, figure_name, title = "", cmap = 'viridis', 
        ticks = None, tick_labels=None, vmin=None,vmax=None, save=True
    ):
    """Converts a raster file to a figure with colorbar and title

    Parameters
    ----------
    raster_name: path
        raster file
    figure_name: path
        output figure file
    title: str, default ""
    cmap: str or matplotlib colormap, default 'viridis'
    ticks: list, defaults None
        where the colorbat ticks are placed
    tick_labes: list, defaults None
        optional labels for the colorbar ticks
    vmin: Float or Int
    vmax: Float or Int
        min and max values to plot
    """
    if type(raster_name) is str:
        data, md = load_raster(raster_name)
    else:
        data = raster_name
    imgplot = plt.matshow(data, cmap = cmap, vmin=vmin, vmax=vmax) 
    # imgplot.axes.get_xaxis().set_visible(False)
    # imgplot.axes.get_yaxis().set_visible(False)
    imgplot.axes.axis('off')
    cbar = plt.colorbar(shrink = .9, drawedges=False,  ticks=ticks) #[-1, 0, 1]
    # fig.colorbar(cax)
    if tick_labels:
        cbar.set_ticklabels(tick_labels)
        plt.clim(-0.5, len(tick_labels) - .5)
    plt.title(title, y=1.2)
    if save:
        plt.savefig(figure_name, bbox_inches='tight')
    else:
        plt.show()
    plt.close()

def clip_polygon_raster (
    in_raster, out_raster, vector, **warp_options
    ):
    """clips raster from shape using gdal warp

    Parameters
    ----------
    in_raster: path or gdal.Dataset
        input rater 
    out_raster: path
        file to save clipped data to
    vector: path
        path to vector file with shape to clip to
    warp_options:
        keyword options for gdal warp as formated for gdal.WarpOptions
        see https://gdal.org/python/osgeo.gdal-module.html#WarpOptions
        Default options use 'cropToCutline' = True, 'targetAlignedPixels' = True
        and xRes and yRes from input raster.

    Returns
    -------
    gdal.Dataset
    """
    if type(in_raster) is str:
        in_raster = load_raster(in_raster, True)
    gt = in_raster.GetGeoTransform()
     
    
    options = {
        'xRes': gt[1],'yRes': gt[5],
        'targetAlignedPixels':True,
        'cutlineDSName': vector,
        'cropToCutline':True
    }
    options.update(warp_options)
    
    options = gdal.WarpOptions(**options)
    
    rv = gdal.Warp(out_raster, in_raster, options=options )
    if not rv is None:
        rv.FlushCache()
    return rv

def calc_norm_index(dataset, band_num, ir_band_num):
    """
    """
    ir_band = dataset.GetRasterBand(ir_band_num).ReadAsArray()
    band = dataset.GetRasterBand(band_num).ReadAsArray()

    return (ir_band - band) /  (ir_band + band)


def calc_julian_days_dg(tlc_time):
    a = tlctime.year//100 
    b = 2 - a + a // 4
    UT = tlctime.hour + tlctime.minute/60 + (tlctime.second+tlctime.microsecond)/3600
    jd = int(365.25*tlctime.year+4716) + \
        int(30.6001*(tlctime.month+1)) + \
        tlctime.day + UT/24+b-1524.5
    return jd

def calc_dist_sun_earth_au(jd):
    d = jd - 2451545.0
    g = 357.529 + 0.98560028 * d
    d_es = 1.00014 - 0.01671 * np.cos(g) - 0.00014*np.cos(2*g)
    return d_es

def calc_absolute_radometric_calibration(
        data, gain,offset, abs_cal_factor, effective_bandwidth, 
    ):
    """"""
    return gain*data*(abs_cal_factor/effective_bandwidth) + offset

def calc_toa_reflectance(radiance, dist_earth_sun, irradiance, theta):
    """
    """
    ref = (radiance * (dist_earth_sun**2) * np.pi)/ (irradiance * np.cos(theta))
    return ref



# def orthorectify(out_raster, in_raster, ): 
#     gdal.Warp(out_raster, in_raster, 

## examples
# --- ## numerical 
# raster.convert_to_figure( 
#     'atm_ns_potential_initialization_areas_full_winter_precipitation/1901-1950/2003_precip_gtavg.tif', 
#     'winter-2003-2004-full-winter-precip.jpg', 
#     'Winter (Oct-Mar) 2003-2004 Departure From Average Precipitation', 
#     cmap="Greens",  
# ) 

# --- ## categorical         
# raster.convert_to_figure( 
#     'atm_ns_potential_initialization_areas_full_winter_precipitation/1901-1950/2003_precip_gtavg.tif', 
#     'winter-2003-2004-full-winter-precip.jpg', 
#     'Winter (Oct-Mar) 2003-2004 Departure From Average Precipitation', 
#     cmap=plt.cm.get_cmap("Greens", 4),  
#     ticks=[0,1,2,3],  
#     vmin=0, 
#     vmax=3,  
#     tick_labels=['<= Average', '> Average', '> 1 Std. Dev.', '> 2 Std. Dev.'] 
# )                
