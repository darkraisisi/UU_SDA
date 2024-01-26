"""
3.2 Merging geometries A
"""

from osgeo import gdal, ogr
from osgeo.osr import SpatialReference
import os

rdNew = SpatialReference()
rdNew.ImportFromEPSG(28992)

folder = "labs/lab2/Lab 2 - data/"

data_source = ogr.GetDriverByName('GPKG').Open(os.path.join(folder, 'schools.gpkg'), update=1)
buffer_layer = data_source.GetLayerByName('buffer')

layer_name = "merge"

# If it doesn't exit run the calc else only show me the questions.
if data_source.GetLayerByName(layer_name):
    data_source.DeleteLayer(layer_name)

print(f"Question: What kind of geometry type does the layer merge need to be?\nMultiPolygon, Polygon seems to give warnings against my instinct that merged polygons van be only one.")

merge_layer = data_source.CreateLayer(layer_name, srs=rdNew, geom_type=ogr.wkbMultiPolygon)

buffer_feature = buffer_layer.GetNextFeature()

# Check if there are features in the buffer layer
merge_geometry = buffer_feature.GetGeometryRef().Clone()
merge_layer_def = merge_layer.GetLayerDefn()

# Iterate over the features in the buffer layer
while buffer_feature:
    # Get the geometry of the current buffer feature
    buffer_geometry = buffer_feature.GetGeometryRef()

    # Merge the current buffer geometry with merge_geometry
    union = merge_geometry.Union(buffer_geometry)

    # Update merge_geometry with union
    merge_geometry = union.Clone()

    # Move to the next buffer feature
    buffer_feature = buffer_layer.GetNextFeature()

# Create a new feature and set its geometry to merge_geometry
merge_feature = ogr.Feature(merge_layer_def)
merge_feature.SetGeometry(merge_geometry)

# Add the feature to the merge layer
merge_layer.CreateFeature(merge_feature)