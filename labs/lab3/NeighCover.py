"""
Model exported as python.
Name : NeighStat
Group : NeighStat
With QGIS : 32204
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterField
from qgis.core import QgsProcessingParameterVectorLayer
import processing


class Neighstat(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterField('attrivutes', 'Attributes', type=QgsProcessingParameterField.String, parentLayerParameterName='landuse2017', allowMultiple=False, defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('landuse2017', 'Landuse2017', defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(5, model_feedback)
        results = {}
        outputs = {}

        # Select by attribute
        alg_params = {
            'FIELD': parameters['attrivutes'],
            'INPUT': parameters['landuse2017'],
            'METHOD': 0,  # creating new selection
            'OPERATOR': 0,  # =
            'VALUE': '40'
        }
        outputs['SelectByAttribute'] = processing.run('qgis:selectbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Extract selected features
        alg_params = {
            'INPUT': outputs['SelectByAttribute']['OUTPUT'],
            'OUTPUT': '/home/daviddemmers/Documents/uu/SDA/labs/lab3/data/parks.shp',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractSelectedFeatures'] = processing.run('native:saveselectedfeatures', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Rasterize (vector to raster)
        alg_params = {
            'BURN': 0,
            'DATA_TYPE': 5,  # Float32
            'EXTENT': '110187.009400000,134024.953600000,476769.538500000,493890.302900000 [EPSG:28992]',
            'EXTRA': '',
            'FIELD': 'CBScode2',
            'HEIGHT': 40,
            'INIT': None,
            'INPUT': outputs['ExtractSelectedFeatures']['OUTPUT'],
            'INVERT': False,
            'NODATA': 0,
            'OPTIONS': '',
            'OUTPUT': '/home/daviddemmers/Documents/uu/SDA/labs/lab3/data/parksRaster.tif',
            'UNITS': 1,  # Georeferenced units
            'USE_Z': False,
            'WIDTH': 40,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RasterizeVectorToRaster'] = processing.run('gdal:rasterize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # r.neighbors
        alg_params = {
            '-a': False,
            '-c': False,
            'GRASS_RASTER_FORMAT_META': '',
            'GRASS_RASTER_FORMAT_OPT': '',
            'GRASS_REGION_CELLSIZE_PARAMETER': 0,
            'GRASS_REGION_PARAMETER': None,
            'gauss': None,
            'input': outputs['RasterizeVectorToRaster']['OUTPUT'],
            'method': 8,  # count
            'output': '/home/daviddemmers/Documents/uu/SDA/labs/lab3/data/neighParks.tif',
            'quantile': '',
            'selection': None,
            'size': 25,
            'weight': '',
            'output': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Rneighbors'] = processing.run('grass7:r.neighbors', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Zonal statistics
        alg_params = {
            'COLUMN_PREFIX': 'PDen_',
            'INPUT': 'PC4_c12ea706_804f_4b3e_86bc_e9b24d0d8000',
            'INPUT_RASTER': outputs['Rneighbors']['output'],
            'OUTPUT': '/home/daviddemmers/Documents/uu/SDA/labs/lab3/data/ParkDens.shp',
            'RASTER_BAND': 1,
            'STATISTICS': [2],  # Mean
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ZonalStatistics'] = processing.run('native:zonalstatisticsfb', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        return results

    def name(self):
        return 'NeighStat'

    def displayName(self):
        return 'NeighStat'

    def group(self):
        return 'NeighStat'

    def groupId(self):
        return 'NeighStat'

    def createInstance(self):
        return Neighstat()
