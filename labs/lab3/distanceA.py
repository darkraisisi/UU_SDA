"""
Model exported as python.
Name : DistanceA
Group : DistanceA
With QGIS : 32204
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterField
from qgis.core import QgsProcessingParameterVectorLayer
import processing


class Distancea(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterField('attrivutes', 'Attributes', type=QgsProcessingParameterField.String, parentLayerParameterName='landuse2017', allowMultiple=False, defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('landuse2017', 'Landuse2017', defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('pc4area', 'PC4 area', defaultValue=None))

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

        # Proximity (raster distance)
        alg_params = {
            'BAND': 1,
            'DATA_TYPE': 5,  # Float32
            'EXTRA': '',
            'INPUT': outputs['RasterizeVectorToRaster']['OUTPUT'],
            'MAX_DISTANCE': 0,
            'NODATA': 0,
            'OPTIONS': '',
            'OUTPUT': '/home/daviddemmers/Documents/uu/SDA/labs/lab3/data/dist2parks.tif',
            'REPLACE': 0,
            'UNITS': 0,  # Georeferenced coordinates
            'VALUES': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ProximityRasterDistance'] = processing.run('gdal:proximity', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Zonal statistics
        alg_params = {
            'COLUMN_PREFIX': 'dist_',
            'INPUT': parameters['pc4area'],
            'INPUT_RASTER': outputs['ProximityRasterDistance']['OUTPUT'],
            'OUTPUT': '/home/daviddemmers/Documents/uu/SDA/labs/lab3/data/avgDist.shp',
            'RASTER_BAND': 1,
            'STATISTICS': [2],  # Mean
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ZonalStatistics'] = processing.run('native:zonalstatisticsfb', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        return results

    def name(self):
        return 'DistanceA'

    def displayName(self):
        return 'DistanceA'

    def group(self):
        return 'DistanceA'

    def groupId(self):
        return 'DistanceA'

    def createInstance(self):
        return Distancea()
