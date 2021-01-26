# CHANGLOG

## [0.3.0] - 2021-01-26
### added
- raster.zoom_box and raster.get_zoom_box_geotransform functions
- vector.py 

### changed
- improved raster documentation

## [0.2.2] - 2021-01-05
### updated
- gdal imports to be "from osgeo import gdal"

## [0.2.1] - 2020-12-10
### updated
- raster.zoom_to radius of 0 now can return the vaule at the pixel requested

## [0.2.0] - 2020-12-02
### added
- raster.get_zoom_geotransform to build transform for data returned by zoom_to
function

## [0.1.1] - 2020-11-24
### added
- OLD_STYLE_RASTER_METADATA for compatbility of reading raster metadata 
from old (as in previously written) yaml file

## [0.1.0] - 2020-11-23
### Initial Version
