"""
Model exported as python.
Name : FieldAgg
Group : FieldAgg
With QGIS : 32204
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
import processing


class Fieldagg(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('landuse', 'Land use', defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('postalcodeareas', 'Postal code areas', defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(4, model_feedback)
        results = {}
        outputs = {}

        # Rasterize (vector to raster)
        alg_params = {
            'BURN': 0,
            'DATA_TYPE': 5,  # Float32
            'EXTENT': '110187.009400000,134024.953600000,476769.538500000,493890.302900000 [EPSG:28992]',
            'EXTRA': '',
            'FIELD': 'CBScode2',
            'HEIGHT': 50,
            'INIT': None,
            'INPUT': parameters['landuse'],
            'INVERT': False,
            'NODATA': 0,
            'OPTIONS': '',
            'OUTPUT': '/home/daviddemmers/Documents/uu/SDA/labs/lab3/data/Landuse_raster.tif',
            'UNITS': 1,  # Georeferenced units
            'USE_Z': False,
            'WIDTH': 50,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RasterizeVectorToRaster'] = processing.run('gdal:rasterize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Reclassify by table
        alg_params = {
            'DATA_TYPE': 5,  # Float32
            'INPUT_RASTER': outputs['RasterizeVectorToRaster']['OUTPUT'],
            'NODATA_FOR_MISSING': True,
            'NO_DATA': -9999,
            'OUTPUT': '/home/daviddemmers/Documents/uu/SDA/labs/lab3/data/parks.tif',
            'RANGE_BOUNDARIES': 0,  # min < value <= max
            'RASTER_BAND': 1,
            'TABLE': ['39','40','1','-9999','39','-9999','40','9999','-9999'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ReclassifyByTable'] = processing.run('native:reclassifybytable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Zonal statistics
        alg_params = {
            'COLUMN_PREFIX': 'park_',
            'INPUT': parameters['postalcodeareas'],
            'INPUT_RASTER': outputs['ReclassifyByTable']['OUTPUT'],
            'RASTER_BAND': 1,
            'STATISTICS': [0],  # Count
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ZonalStatistics'] = processing.run('native:zonalstatisticsfb', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Field calculator
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'Parkarea',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': "(attribute($currentfeature,'park_count') * (50*50))/ attribute($currentfeature,'Opp_m2')",
            'INPUT': outputs['ZonalStatistics']['OUTPUT'],
            'OUTPUT': '/home/daviddemmers/Documents/uu/SDA/labs/lab3/data/parkarea.shp',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculator'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        return results

    def name(self):
        return 'FieldAgg'

    def displayName(self):
        return 'FieldAgg'

    def group(self):
        return 'FieldAgg'

    def groupId(self):
        return 'FieldAgg'

    def createInstance(self):
        return Fieldagg()
