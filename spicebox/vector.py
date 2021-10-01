from osgeo import ogr
import json
from pandas import DataFrame
import numpy as np
import geojson

from scipy.spatial import ConvexHull

def load_vector(in_vec_file):
    """Open a vector file readable by ogr

    returns
    -------
    ogr vector data source
    """
    ds = ogr.Open(in_vec_file)

    return ds

def get_features(vector_ds):
    """Get features from vector data source

    parameters
    ----------
    vector_ds:
        dict of feature keyed by feature names
    """

    vec_data = {}
    
    count = vector_ds.GetLayerCount()
    # print (count)
    for l_n in range (count):
        layer = vector_ds.GetLayer(l_n)
        # print(layer)
        vec_data[layer.GetName()] = {}
        for f_n in range(1, layer.GetFeatureCount() + 1):
            feature = layer.GetFeature(f_n)
            ## Loop through fields?
            f_name = feature.GetField(1)
            vec_data[layer.GetName()][f_name] = feature

    return vec_data

def calc_centroids(vec_data, format_as_table=False):
    """Calc centroids of vector features

    parameters
    ----------
    vec_data: dict
        dict of vector features
    format_as_table: bool
        if True centroids are returned as pandas dataframe, otherwise dict
        is returned
    
    returns
    -------
    dict or DataFrame
    """
    
    centroids = {}
    for l_name in vec_data:
        fields = {}
        for f_name in vec_data[l_name]:
            geom = vec_data[l_name][f_name].geometry()
            # print(geom)

            fields[f_name] = geom.Centroid().GetPoint()
        centroids[l_name] = fields
    if format_as_table:
        centroids = DataFrame(
            [[l, f, centroids[l][f][1], centroids[l][f][0]] \
                for l in centroids \
                for f in centroids[l]
            ],
            columns = ['site', 'location', 'lat', 'long'] )
    return centroids


def merge_polygons (feature_list):
    """Create one polygon from the convex hull of many polygons

    Parametes
    ---------
    feature_list: list
        list of ogr.Feature objects
    
    Returns
    -------
    ogr.Geometry
        convex hull geometry
    """
    final_points_list = []
    for feat in feature_list:
        js = json.loads(feat.ExportToJson())
        points_list = np.array(js['geometry']['coordinates'])
        len_points = int(np.array(points_list.shape[:-1] ).prod())
        n_coords = int(points_list.shape[-1])

        points_list = points_list.reshape([len_points, n_coords])

        final_points_list += list(points_list)

    # final_points_list = np.flip(final_points_list, axis=1)

    ch = ConvexHull(final_points_list)

    chl = ch.points[ch.vertices].tolist()
    chl.append(ch.points[ch.vertices][0].tolist())

    geojs = geojson.Polygon(coordinates=[chl])
    return ogr.CreateGeometryFromJson(json.dumps(geojs))
 

def create_new_feature(feat_def, geom):
    """Create a new feature

    Parameters
    ----------
    feat_def: ogr.FeatureDefn
        definition for feature from a layer 
    geom: ogr.Geometry
        geometry of feature

    Returns
    --------
    ogr.Feature
    """
    feat = ogr.Feature(feat_def)
    rv = feat.SetGeometry(geom)
    
    if rv != 0:
        return None

    # feat.SetField('name', name)
    return feat

def create_new_data_source(file_name, driver_name = 'ESRI Shapefile'):
    """Creates a new vector DataSource. Use `save_vector` to save contents
    to disk.

    Parameters
    ----------
    file_name: str
        a path to the new file to create
    driver_name: Str
        vector driver recognized by ogr.GetDriverByName
    
    Returns
    -------
    ogr.DataSource
    """
    driver = ogr.GetDriverByName(driver_name)
    return driver.CreateDataSource(file_name)


def save_vector(data_source):
    """Save a modified vector data set to disk

    Parameters
    ----------
    data_source: ogr.DataSource
    """
    data_source.FlushCache()


def get(dataset, layer, feature=None):
    """
    get the targer layer, or feature from a data set

    Parameters
    ----------
    dataset: ogr.DataSource
        vector dataset
    layer: int
        layer number
    feature: int or None (optional)
        feature number in layer 
    """

    layer = dataset.GetLayer(layer)
    if feature is None or layer is None:
        return layer
    return layer.GetFeature(feature)
    
def geometry_to_array(geometry):
    """
    Get geometry type and list of points defining geometry form ogr.Geometry

    Parameters
    ----------
    geometry: ogr.Geometry

    """
    gt = geometry.GetGeometryName()
   
    if gt == 'POLYGON':
        bound = geometry.Boundary()
        pts = bound.GetPoints()
        array = np.array(pts)
    elif  gt == 'MULTIPOLYGON':
        geo_list = []
        # bound = geometry.GetGeometryCount()
        for i in range(geometry.GetGeometryCount()):
            bound = geometry.GetGeometryRef(i).GetBoundary()
            geo_list.append(np.array(bound.GetPoints()))
        array = np.array(geo_list)
        
    else:
        raise NotImplementedError('%s Not implented' % gt)
    

    return gt, array


def plot_geometry(geometry, ax, gt=None):
    """
    plot geometry on plt axis object

    Parameters
    ----------
    geometry: ogr.Geometry

    Returns
    -------
    matplotlib compatible axis

    """

    if type(geometry) is ogr.Geometry:
        gt, pts = geometry_to_array(geometry)
    else:
        pts = geometry

    if gt == 'POLYGON':
        ax.plot(pts.T[0], pts.T[1])

    else:
        raise NotImplementedError('plotting of %s is not implemented' % gt)

    return ax 


