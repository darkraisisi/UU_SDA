"""
3.3 Compute area far from schools
"""

from osgeo import gdal, ogr
from osgeo.osr import SpatialReference
import os

rdNew = SpatialReference()
rdNew.ImportFromEPSG(28992)

folder = "labs/lab2/Lab 2 - data/"

# Load the districts layer
dist_data_source = ogr.GetDriverByName('GPKG').Open(os.path.join(folder, 'Amsterdam_BAG.gpkg'), update=1)
full_district_layer = dist_data_source.GetLayerByName('merge')

school_data_source = ogr.GetDriverByName('GPKG').Open(os.path.join(folder, 'schools.gpkg'), update=0)
full_schools_layer = school_data_source.GetLayerByName('merge')

print(f"Question: Which operation will you use to compute the area far away from schools?\nErase\n")

layer_name = "away"
if dist_data_source.GetLayerByName(layer_name):
    dist_data_source.DeleteLayer(layer_name)

away_layer = dist_data_source.CreateLayer(layer_name, srs=rdNew, geom_type=ogr.wkbMultiPolygon)
full_district_layer.Erase(full_schools_layer, away_layer)

# Get the first (and only) feature from the away_layer & its geometry
away_feature = away_layer.GetNextFeature()
away_geometry = away_feature.GetGeometryRef()

# Calculate the area of the geometry
away_area = away_geometry.GetArea()
print(f"Question: What is the size of the area considered as far away from public schools?\n{away_area*0.0000001} km2")