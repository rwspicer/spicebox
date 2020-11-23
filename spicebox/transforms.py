"""
Transforms
----------

Functions for performing coordinate transforms

"""
import numpy as np
import gdal
from osgeo.osr import SpatialReference, CoordinateTransformation


def to_pixel (coords, gt):
    """Convert from geographic coordinates (ie. Alaska Albers [east,north]) 
    to pixel coordinates (row, cols) 

    Parameters
    ----------
    coords: list like
        coordinates in system defined by gt
        i.e (east, north) or list of (east, north) coordinates 
    gt: tuple 
        raster geotransform format (origin_x, pixel_width, x_rotation, 
        origin_y, y_rotation, pixel_height)
        see: https://gdal.org/user/raster_data_model.html

    Returns
    -------
    coordinates (row, col) or list of coordinates in row col format
    """
    coords = np.array(coords)
    gt = gdal.InvGeoTransform(gt)
    transform_mat = np.array([
        [gt[1], gt[2], gt[0]],
        [gt[4], gt[5], gt[3]],
        [   0,     0,   1],
    ]).T
    try:# multiple points
        if coords.shape[1] == 2:
            new = np.ones([coords.shape[0], 3])
            new[:,:-1] = coords[:]
            coords = new
        # flip to change coord order 
        return np.flip(np.matmul(coords, transform_mat)[:,:-1],1)
    except IndexError:
        coords = np.array([coords[0], coords[1], 1])
        return np.flip(np.matmul(coords, transform_mat)[:-1],0)
    
def to_geo (coords, gt):
    """Convert from pixel coordinates (row, cols) 
    to geographic coordinates (ie. Alaska Albers [east,north]) 

    Parameters
    ----------
    coords: list like
        coordinates in row col format
        i.e (row, col) or list of (row, col) coordinates 
    gt: tuple 
        raster geotransform format (origin_x, pixel_width, x_rotation, 
        origin_y, y_rotation, pixel_height)
        see: https://gdal.org/user/raster_data_model.html

    Returns
    -------
    coordinates raster (ie [east, north]) or list of coordinates in that format
    """
    coords = np.array(coords)
    # flip to change coord order from row major to col major
    coords = np.flip(coords,0)
    transform_mat = np.array([
        [gt[1], gt[2], gt[0]],
        [gt[4], gt[5], gt[3]],
        [   0,     0,   1],
    ]).T
    try:# multiple points
        if coords.shape[1] == 2:
            new = np.ones([coords.shape[0], 3])
            new[:,:-1] = coords[:]
            coords = new

        return np.matmul(coords, transform_mat)[:,:-1]
    except IndexError:
        coords = np.array([coords[0], coords[1], 1])
        return np.matmul(coords, transform_mat)[:-1]


def format_crs(unformatted_crs):
    """Format a Coordinate Reference Systems (CRS) (WTK or EPSG #) as a 
    SpatialReference Object

    Parameters
    ----------
    unformatted_crs: str, int, or SpatialReference
        for int: SpatialReference object created from EPSG code
        for str: SpatialReference object created from WKT (string must be in WKT
        format)
        for SpatialReference object, object is returned

    Raises
    ------
    TypeError: if SpatialReference cannot be created from input

    
    Returns
    -------
    SpatialReference
    """
    if type(unformatted_crs) is SpatialReference:
        return unformatted_crs
    elif type(unformatted_crs) is int:
        crs = SpatialReference()
        crs.ImportFromEPSG(unformatted_crs)
        return crs
    elif  type(unformatted_crs) is str:
        crs = SpatialReference()
        try:
            crs.ImportFromWkt(unformatted_crs)
        except:
            raise TypeError ('CRS could not be created from provided reference')
        return crs
    else:
        raise TypeError ('CRS could not be created from provided reference')
        


def convert_projections(points, in_crs, out_crs):
    """Converts a point or list of points from in_crs to out_crs

    Parameters
    ----------
    points: list 
        (x,y) or [(x1,y1), (x2,y2), ... , (xN,yN)]
    in_crs: str, int, or SpatialReference
        CRS for input points
        This argument is passed through format_crs function
    out_crs: str, int, or SpatialReference
        CRS for output points
        This argument is passed through format_crs function

    Returns
    -------
    points in out_crs system
    """
    points = np.array(points)
    
    shape = points.shape
    
    if shape == (2,):
        points = np.array(points).reshape(1,2)
    
    in_crs = format_crs(in_crs)
    out_crs = format_crs(out_crs)

    transform = CoordinateTransformation(in_crs,out_crs)

    
    return np.array(transform.TransformPoints(points))[:,:-1].reshape(shape)

def to_wgs84(points, in_crs):
    """Converts point or list of points to WGS84 (EPSG:4236) (lat, long) format

    Parameters
    ----------
    points: list 
        (x,y) or [(x1,y1), (x2,y2), ... , (xN,yN)] in in_crs system
    in_crs: str, int, or SpatialReference
        CRS for input points
        This argument is passed through format_crs function

    Returns
    -------
    points in WGS84 system
    """
    return convert_projections(points, in_crs, 4236)
    
def from_wgs84(points, out_crs):
    """
    Parameters
    ----------
    points: list 
        (x,y) or [(x1,y1), (x2,y2), ... , (xN,yN)] in WGS84 system
    out_crs: str, int, or SpatialReference
        CRS for output points
        This argument is passed through format_crs function

    Returns
    -------
    points in out_crs system
    """
    return convert_projections(points, 4236, out_crs)
    