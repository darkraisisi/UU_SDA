"""
Model exported as python.
Name : distance_analysis_model
Group : 
With QGIS : 33400
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterFeatureSource
import processing


class Distance_analysis_model(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('buildings', 'buildings', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('farmland_switserland', 'Farmland Switserland', defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('ground_cover', 'ground cover', defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('provinces', 'Provinces', defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSource('rivers', 'rivers', types=[QgsProcessing.TypeVectorAnyGeometry], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('streets', 'streets', defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSource('water_bodies_lines', 'water bodies lines', types=[QgsProcessing.TypeVectorAnyGeometry], defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(9, model_feedback)
        results = {}
        outputs = {}

        # water bodies poly
        alg_params = {
            'INPUT': parameters['water_bodies_lines'],
            'KEEP_FIELDS': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['WaterBodiesPoly'] = processing.run('native:polygonize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Select Fribourg
        alg_params = {
            'FIELD': 'name',
            'INPUT': parameters['provinces'],
            'OPERATOR': 0,  # =
            'OUTPUT': 'TEMPORARY_OUTPUT',
            'VALUE': 'Fribourg',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['SelectFribourg'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # rivers Fribourg
        alg_params = {
            'INPUT': parameters['rivers'],
            'OVERLAY': outputs['SelectFribourg']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RiversFribourg'] = processing.run('native:clip', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # water bodies Fribourg
        alg_params = {
            'INPUT': outputs['WaterBodiesPoly']['OUTPUT'],
            'OVERLAY': outputs['SelectFribourg']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['WaterBodiesFribourg'] = processing.run('native:clip', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # streets fribourg
        alg_params = {
            'INPUT': parameters['streets'],
            'OVERLAY': outputs['SelectFribourg']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StreetsFribourg'] = processing.run('native:clip', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Farmland Fribourg
        alg_params = {
            'DATA_TYPE': 0,  # Gegevenstype van invoerlaag gebruiken
            'EXTRA': '',
            'INPUT': parameters['farmland_switserland'],
            'NODATA': None,
            'OPTIONS': '',
            'OUTPUT': 'C:/Users/dhett/Documents/data_science_master/SDASM/Final_assignment/farmland_Fribourg.tif',
            'OVERCRS': False,
            'PROJWIN': outputs['SelectFribourg']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FarmlandFribourg'] = processing.run('gdal:cliprasterbyextent', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # buildings Fribourg
        alg_params = {
            'INPUT': parameters['buildings'],
            'OVERLAY': outputs['SelectFribourg']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['BuildingsFribourg'] = processing.run('native:clip', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # ground cover Fribourg
        alg_params = {
            'INPUT': parameters['ground_cover'],
            'OVERLAY': outputs['SelectFribourg']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['GroundCoverFribourg'] = processing.run('native:clip', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # wetlands Fribourg
        alg_params = {
            'FIELD': 'objektart',
            'INPUT': outputs['GroundCoverFribourg']['OUTPUT'],
            'OPERATOR': 0,  # =
            'OUTPUT': 'C:/Users/dhett/Documents/data_science_master/SDASM/Final_assignment/wetlands_Fribourg.shp',
            'VALUE': 'Feuchtgebiet',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['WetlandsFribourg'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        return results

    def name(self):
        return 'distance_analysis_model'

    def displayName(self):
        return 'distance_analysis_model'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Distance_analysis_model()
