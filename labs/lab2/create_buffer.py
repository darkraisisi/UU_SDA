"""
3.1 Adding buffer areas around schools
"""

from osgeo import gdal, ogr
from osgeo.osr import SpatialReference
import os

rdNew = SpatialReference()
rdNew.ImportFromEPSG(28992)

folder = "labs/lab2/Lab 2 - data/"

data_source = ogr.GetDriverByName('GPKG').Open(os.path.join(folder, 'schools.gpkg'), update=1)
point_layer = data_source.GetLayerByName('locations')

layer_name = "buffer"
buffer_distance = 250

# If it exist run the calc else only show me the questions.
if data_source.GetLayerByName(layer_name):
    data_source.DeleteLayer(layer_name)

buffer_layer = data_source.CreateLayer(layer_name, srs=rdNew, geom_type=ogr.wkbPolygon)

print(f"Question: What kind of geometry type does the layer buffer need to be?\nPolygon\n")

"""
Task: Create new features for the buffer geometries and add them to the buffer layer.
"""
for point_feature in point_layer:

    point_geometry = point_feature.GetGeometryRef()
    buffer_geometry = point_geometry.Buffer(buffer_distance)

    buffer_feature = ogr.Feature(buffer_layer.GetLayerDefn())
    buffer_feature.SetGeometry(buffer_geometry)

    buffer_layer.CreateFeature(buffer_feature)