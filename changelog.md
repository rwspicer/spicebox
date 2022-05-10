# CHANGELOG

## [0.8.1] - 2022-05-10
### Chanaged
- Copies the input config flags dict in CLI constructor so that the 
original object is not affected.

## [0.8.0] - 2022-03-22
### Chanaged
- rewrite of contructior for CLIlib to allow better handling of default and 
optional arguments. This change breaks utilities using older versions 

## [0.7.3] - 2022-02-17
### Fixed
- bugs caused by file tools refactoring

## [0.7.2] - 2022-02-14
### Added
- filetools.tarball_all_subfiles and filetools.tarball_all functions 

### Changed
- Abstraction of code for filetools.tarball_all functions


## [0.7.1] - 2022-02-09
### Changed
- documentation cleanup

## [0.7.0] - 2022-02-03
### Added
- digitalglobe.py
- raster.merge

### change
- adds docs
- changes setup for file tools

## [0.6.0] - 2022-01-18
### Added
- filetools.py
- CLIlib.py
- raster.py normal index functions

### Changed
- updates to raster clipping

## [0.5.0] - 2021-10-01
### Added
- raster.clip_polygon_raster to clip an area from a raster
- vector.get to get a specific layer/feature from a vector dataset
- vector.geometry_to_array to convert feature geometry to an array of coordinates 
- vector.plot_geometry to display geometry on matplotlib axes

### Changed
- raster.read_raster, Added option to return gdal.dataset object instead
of data an metadata separately 

## [0.4.0] - 2021-08-27
### Added
- Added merge_polygons; and 
- functions for creating new vector data_sources and features

## [0.3.0] - 2021-01-26
### Added
- raster.zoom_box and raster.get_zoom_box_geotransform functions
- vector.py 

### Changed
- improved raster documentation

## [0.2.2] - 2021-01-05
### Updated
- gdal imports to be "from osgeo import gdal"

## [0.2.1] - 2020-12-10
### Uspdated
- raster.zoom_to radius of 0 now can return the valuee at the pixel requested

## [0.2.0] - 2020-12-02
### Added
- raster.get_zoom_geotransform to build transform for data returned by zoom_to
function

## [0.1.1] - 2020-11-24
### Added
- OLD_STYLE_RASTER_METADATA for compatbility of reading raster metadata 
from old (as in previously written) yaml file

## [0.1.0] - 2020-11-23
### Initial Version
