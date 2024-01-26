"""
2.3 Computing building densities
"""

from osgeo import gdal, ogr
from osgeo.osr import SpatialReference
import os

rdNew = SpatialReference()
rdNew.ImportFromEPSG(28992)

folder = "labs/lab2/Lab 2 - data/"
ams_data_source = ogr.GetDriverByName('GPKG').Open(os.path.join(folder, "Amsterdam_BAG.gpkg"), update=0)
wijken = ams_data_source.GetLayerByName('Wijken')

centroid_source = ogr.GetDriverByName('GPKG').Open(os.path.join(folder, "centroids.gpkg"), update=1)
centroids = centroid_source.GetLayerByName('centroids')

layer_name = "density"

# If it doesn't exit run the calc else only show me the questions.
# centroid_source.DeleteLayer(layer_name)
if not centroid_source.GetLayerByName(layer_name):

    # Create a new layer and set the new fields (columns).
    density_layer = centroid_source.CreateLayer(layer_name, srs=rdNew, geom_type=ogr.wkbPolygon)

    field_name = ogr.FieldDefn('name', ogr.OFTString)
    field_density = ogr.FieldDefn('density', ogr.OFTReal)
    field_fraction = ogr.FieldDefn('fraction', ogr.OFTReal)
    density_layer.CreateField(field_name)
    density_layer.CreateField(field_density)
    density_layer.CreateField(field_fraction)

    density_layer_def = density_layer.GetLayerDefn()

    # n_district_features = wijken.GetFeatureCount()
    for feature in wijken:
        dist_geom = feature.GetGeometryRef()

        dist_name = feature.GetField('Buurtcombinatie')
        dist_size = dist_geom.GetArea()
        
        dist_n_houses = 0
        dist_are_houses = 0

        centroids.ResetReading()
        for centroid in centroids:
            centroid_geometry = centroid.GetGeometryRef()
            if centroid_geometry.Within(dist_geom):
                dist_n_houses += 1
                dist_are_houses += centroid.GetField('area')
        
        density = dist_n_houses / dist_size
        fraction = (dist_n_houses / dist_are_houses) * 100
        # print(f"Name: {dist_name}, Area: {dist_size}, Density: {density}")
        density_feature = ogr.Feature(density_layer_def)
        density_feature.SetField('name', dist_name)
        density_feature.SetField('density', density)
        density_feature.SetField('fraction', fraction)

        density_layer.CreateFeature(density_feature)

# Question: What is the density of the district with feature id 54 (Museumkwartier)?
density_layer = centroid_source.GetLayerByName('density')
print(f"Question: What is the density of the district with feature id 54 (Museumkwartier)?\n{density_layer.GetFeature(54).GetField('density')}\n")
