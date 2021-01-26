from osgeo import ogr

from pandas import DataFrame

def load_vector(in_vec_file):
    """Open a vector file readable by ogr

    returns
    -------
    gdal vector dataset
    """
    ds = ogr.Open(in_vec_file)

    return ds

def get_features(vector_ds):
    """Get features from vector dataset

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





