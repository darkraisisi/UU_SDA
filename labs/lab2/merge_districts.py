"""
3.2 Merging geometries B

Task: Create a second script merge_districts.py to merge the districts from the Wijken input layer
of the Amsterdam_BAG.gpkg dataset. Merge the district geometries to one new geometry and add the
result to the schools.gpkg dataset as the new layer districts.
"""

from osgeo import gdal, ogr
from osgeo.osr import SpatialReference
import os

rdNew = SpatialReference()
rdNew.ImportFromEPSG(28992)

folder = "labs/lab2/Lab 2 - data/"

# Load the districts layer
dist_data_source = ogr.GetDriverByName('GPKG').Open(os.path.join(folder, 'Amsterdam_BAG.gpkg'), update=1)
dist_layer = dist_data_source.GetLayerByName('Wijken')

layer_name = "merge"
if dist_data_source.GetLayerByName(layer_name):
    dist_data_source.DeleteLayer(layer_name)

merge_layer = dist_data_source.CreateLayer(layer_name, srs=rdNew, geom_type=ogr.wkbMultiPolygon)

dist_feature = dist_layer.GetNextFeature()

merge_geometry = dist_feature.GetGeometryRef().Clone()
merge_layer_def = merge_layer.GetLayerDefn()

# Iterate over the features in the buffer layer
while dist_feature:
    # Get the geometry of the current buffer feature
    dist_geometry = dist_feature.GetGeometryRef()

    # Merge the current buffer geometry with merge_geometry
    union = merge_geometry.Union(dist_geometry)

    # Update merge_geometry with union
    merge_geometry = union.Clone()

    # Move to the next buffer feature
    dist_feature = dist_layer.GetNextFeature()

# Create a new feature and set its geometry to merge_geometry
merge_feature = ogr.Feature(merge_layer_def)
merge_feature.SetGeometry(merge_geometry)

# Add the feature to the merge layer
merge_layer.CreateFeature(merge_feature)