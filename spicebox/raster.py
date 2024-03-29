"""
raster
------
Input Output operations for rasters
"""
from osgeo import gdal, gdal_array
import numpy as np
import subprocess

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

def gdal_type_lookup (item):
    """Find the gdal type code of a Numpy object

    Parameters
    ----------
    item: any
        a numpy objet

    Returns
    -------
    int
        Gdal type code
    """
    try:
        dtype = item.dtype
    except:
        return gdal.GDT_Unknown

    return gdal_array.GDALTypeCodeToNumericTypeCode(dtype.type)

def load_raster (filename,  return_dataset = False, band = 1, mode=gdal.GA_ReadOnly):
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
    dataset = gdal.Open(filename, mode)
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

def create_raster(filename, data, transform, projection, 
        datatype = gdal.GDT_Float32,
        no_data = None,
        color_dict = None,
        metadata = {},
        verbose = False
    ):
    """Create a raster data set from an array and metadata

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
    no_data:
        no data value
    color_dicts: dict, default None
        dict of colors as described by set_band_color_descriptions.
        If left None color descriptions are not written
    metadata: dict
        dict of metadata key value pairs to write to raster metadata
    verbose: bool
        messages may be written to console if true

    Returns
    -------
    gdal raster dateset
    """
    write_driver = gdal.GetDriverByName('GTiff') 

    if len(data.shape) == 3
        cols, rows, bands = data.shape[2], data.shape[1], data.shape[0]
    else:
        cols, rows, bands = data.shape[1], data.shape[0], 1

    raster = write_driver.Create(
        filename, cols, rows, bands, datatype
    )

    raster.SetGeoTransform(transform) 
    raster.SetProjection(projection) 

    for band in range(bands): 
        outband = raster.GetRasterBand(band + 1) # +1 for gdal 1 base index  
        outband.WriteArray(data['band']) 
        if band == 0 and no_data:
            outband.SetNoDataValue(no_data)
        outband.FlushCache()  
        del(outband)

    for key in metadata:
        set_metadata_item(raster, key, metadata['key'], verbose)

    if color_dict: 
        set_band_color_descriptions(raster, color_dict, verbose)
    
    
    raster.FlushCache()   
    return raster

def set_band_color_descriptions(ds, color_dict, verbose=False):
    """Set band descriptions to color names. If band name is red, green, or 
    blue color interpretation is also set 

    Parameters
    ----------
    ds: gdal.dataset
        raster dataset
    color_dict: dict
        dict of band numbers to color names. i.e 
        {1: 'blue', 2:'green', 3:'red', 4:'nir 1' }
    verbose: bool
        if true prints updated band metadata values

    Returns
    -------
    returns True if function is successful
    """

    ci_table = {
        'red': gdal.GCI_RedBand,
        'green': gdal.GCI_GreenBand,
        'blue': gdal.GCI_BlueBand,
        'panchromatic': gdal.GCI_GrayIndex,
    }

    for band in range(1, ds.RasterCount+1):
        rb = ds.GetRasterBand(band)
        
        if color_dict[band] in ['red', 'green', 'blue']:
            rb.SetColorInterpretation(ci_table[color_dict[band]])
        else:
            rb.SetColorInterpretation(0)

        rb.SetDescription(color_dict[band])
        if verbose:
            print(rb.GetDescription(), rb.GetColorInterpretation())
    return True

def set_metadata_item(ds, key, value, verbose=False):
    """sets a raster metadata item

    Parameters
    ----------
    ds: gdal.dataset
        raster dataset
    key: str
    value: str
    verbose: bool
        if true prints updated band metadata values

    Returns
    -------
    returns True if function is successful
    """
    
    ds.SetMetadataItem(key, value)
    if verbose:
        print(ds.GetMetadata())
    
    return True



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

def rescale_raster(
        in_raster, out_raster, resolution, datatype=gdal.GDT_Float32
    ):
    """Rescales a rasters pixels to resolution
                                            
    Parameters
    ----------                                 
    in_raster: path                           
        input raster file
    out_raster: path
        output raster file
    resolution: tuple
        (x Resolution, y Resolution)
    datatype: gdal.Type
    """
    tiff = gdal.Warp(
        out_raster, in_raster, xRes=resolution[0], yRes=resolution[1], 
        format='GTiff', outputType=datatype
    )    
    tiff.GetRasterBand(1).FlushCache()
    tiff.FlushCache()
    return True


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
    
    Parameters
    ----------
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
    """clips raster from shape(a vector file) using gdal warp

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

def clamp_band(data, min, max ):
    """clamp data in band between min an max

    Parameters
    ----------
    data: np.array
        band data
    min: Number
    max: Number
        Min and max values to clam to

    Returns
    -------
    np.array
        band_data
    """
    data[data < min] = min
    data[data > max] = max
    return data


def calc_norm_index(dataset, band_a_name, band_b_name):
    """Calculate a normalized index such as NDVI acording to the 
    equation: 

        INDEX = (band_a - band b)/(band_a + band_b)

    Parameters
    ----------
    dataset: GDAL.dataset
        multispectral raster dataset
    band_a_num: str
    band_b_num: str
        band numbers to use in calculating index

    Returns
    -------
    Index values
    """
    ## adding clamp function here because reflectance should be [0,1]
    band_a = clamp_band(dataset.GetRasterBand(band_a_name).ReadAsArray(), 0, 1)
    band_b = clamp_band(dataset.GetRasterBand(band_b_name).ReadAsArray(), 0, 1)

    return (band_a - band_b) /  (band_b + band_a)


def reproject(in_img, out_img, new_projection, dest_nodata):

    options = gdal.WarpOptions(
        dstSRS=new_projection, 
        dstNodata=dest_nodata, 
        creationOptions=['COMPRESS=LZW',]
    )
    gdal.Warp(out_img, in_img, options=options)


def merge(to_merge, outfile, warp_options=[]): 
    """Merge many rasters into a single raster using gdal warp

    Parameters
    ----------
    to_merge: list
        list of raster files
    outfile: path
        path to save merged data at
    warp_options: gdal.warpOptions
        options to pass to gdal warp

    Returns
    -------
    raster.Dataset
    """
    merged = gdal.Warp(
        outfile, to_merge, format="GTiff",
        options=warp_options
    ) # if you want
    
    merged.FlushCache() 
    return merged 

def set_no_data(ds, no_data_val, no_data_mask, bands=None):
    """sets 
    """
    if bands is None:
        bands = range(1, ds.RasterCount+1)
    for band in bands:
        rb = ds.GetRasterBand(band)
        data = rb.ReadAsArray()
        data[no_data_mask] = no_data_val
        ds.GetRasterBand(band).WriteArray(data)
        ds.GetRasterBand(band).SetNoDataValue(no_data_val)

    return True

def change_no_data(ds, new_no_data, bands=None):
    if bands is None:
        bands = range(1, ds.RasterCount+1)
    for band in bands:
        rb = ds.GetRasterBand(band)
        old_no_data = rb.GetNoDataValue()
        data = rb.ReadAsArray()
        if np.isnan(old_no_data):
            mask = np.isnan(data)
        else:
            mask = data == old_no_data
        set_no_data(ds, new_no_data, mask, [band])

    return True



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
