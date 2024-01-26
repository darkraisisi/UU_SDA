"""
2.1 Queries
"""

from osgeo import gdal, ogr
from multiprocessing import Pool

filename = "labs/lab2/Lab 2 - data/Amsterdam_BAG.gpkg"
data_source = ogr.GetDriverByName('GPKG').Open(filename, update=0)
n_layers = data_source.GetLayerCount()
print(f"Task: Print the number of layers included in the dataset.\n{n_layers}\n")

print(f"Task: Print for each layer the layer name and CRS.")
for layer_index in range (n_layers):
    layer = data_source.GetLayerByIndex(layer_index)
    srs = layer.GetSpatialRef()
    print(f"Name: {layer.GetName()}\nSrs: {srs.GetName()}, {srs.GetAuthorityName(None)}, {srs.GetAuthorityCode(None)}\n")

buildings = data_source.GetLayerByName('Verblijfsobject')
n_building_features = buildings.GetFeatureCount()
print(f"Task: Print the number of features in the layer.\nN building features: {n_building_features}\n")

locations_def = buildings.GetLayerDefn()
field_count = locations_def.GetFieldCount()
print(f"Task: Print the name and type of each field in the layer")
for i in range(field_count):
    field_name = locations_def.GetFieldDefn(i).GetName()
    print(f"field name: {field_name}, field type: {locations_def.GetFieldDefn(i).GetTypeName()}")

# total_area = 0
# for i in range(1, n_building_features):
#     feature = buildings.GetFeature(i)
#     total_area += feature.GetField('oppervlakte')

# print(total_area)

def calculate_area(feature):
    return feature.GetField('oppervlakte')

n_cores = 6
chunk_size = n_building_features // n_cores

def process_chunk(chunk):
    return sum(calculate_area(buildings.GetFeature(i)) for i in chunk)

with Pool(n_cores) as pool:
    total_area = sum(pool.map(process_chunk, [range(i, min(i + chunk_size, n_building_features)) for i in range(1, n_building_features, chunk_size)]))
print(f"Question: What is the total surface area given in the location layer?\n{total_area}\n")

f = buildings.GetFeature(439774)
geom = f.GetGeometryRef()
x, y = geom.GetX(), geom.GetY()
print(f"Question: What is the coordinate of the feature with the index 439774?\nCoordinates of 439774, X: {x}, Y: {y}")