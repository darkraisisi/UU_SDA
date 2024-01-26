"""
2.2 Obtaining building properties
"""

from osgeo import gdal, ogr
from osgeo.osr import SpatialReference

filename = "labs/lab2/Lab 2 - data/Amsterdam_BAG.gpkg"
data_source = ogr.GetDriverByName('GPKG').Open(filename, update=0)
pand = data_source.GetLayerByName('pand')

rdNew = SpatialReference()
rdNew.ImportFromEPSG(28992)

centroid_source = ogr.GetDriverByName('GPKG').CreateDataSource('labs/lab2/Lab 2 - data/centroids.gpkg')
centroid_layer = centroid_source.CreateLayer('centroids', srs=rdNew, geom_type=ogr.wkbPoint)

# Example: Delete a layer
# if data_source.GetLayerByName(layername):
    # data_source.DeleteLayer(layername)

# Example: Adding field holding floats to layer.
# field = ogr.FieldDefn('area', ogr.OFTReal)
# layer.CreateField(field)
"""
Task: Add a field area to your layer centroids
"""
field = ogr.FieldDefn('area', ogr.OFTReal)
centroid_layer.CreateField(field)

centroid_layer_def = centroid_layer.GetLayerDefn()
for feature in pand:
    house_geometry = feature.GetGeometryRef()
    centroid = house_geometry.Centroid()
    house_area = house_geometry.GetArea()
    """
    Task: Calculate the area and the centroid location of each building.
    """
    point_feature = ogr.Feature(centroid_layer_def)
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(centroid.GetX(), centroid.GetY())
    point_feature.SetGeometry(point)
    point_feature.SetField('area', house_area)
    centroid_layer.CreateFeature(point_feature)