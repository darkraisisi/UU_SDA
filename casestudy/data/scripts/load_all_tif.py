from glob import glob
from multiprocessing.pool import ThreadPool as Pool
from qgis.core import QgsRasterLayer, QgsProject
from PyQt5.QtCore import QFileInfo

def load_and_add_raster(raster):
    # Check if string is provided
    fileInfo = QFileInfo(raster)
    path = fileInfo.filePath()
    baseName = fileInfo.baseName()

    layer = QgsRasterLayer(path, baseName)
    QgsProject.instance().addMapLayer(layer)

    if layer.isValid() is False:
        print(f"Unable to read basename and file path.\n{raster}")
    elif layer.isValid() and not layer.isValid():
        print(f"Error loading raster {raster}")


# Execution
rasters = glob('Documents/uu/SDA/casestudy/data/datasets/height/*.tif')
n_cores = 8

with Pool(processes=n_cores) as pool:
    pool.map(load_and_add_raster, rasters)
