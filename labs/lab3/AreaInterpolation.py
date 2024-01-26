"""
Model exported as python.
Name : AreaInterprolation
Group : AreaInterprolation
With QGIS : 32204
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
import processing


class Areainterprolation(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('sourcelayer', 'Source Layer', defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('targetlayer', 'Target Layer', defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(5, model_feedback)
        results = {}
        outputs = {}

        # Intersection
        alg_params = {
            'INPUT': parameters['targetlayer'],
            'INPUT_FIELDS': [''],
            'OUTPUT': '/home/daviddemmers/Documents/uu/SDA/labs/lab3/data/intersection.gpkg',
            'OVERLAY': parameters['sourcelayer'],
            'OVERLAY_FIELDS': [''],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Intersection'] = processing.run('native:intersection', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Add geometry attributes
        alg_params = {
            'CALC_METHOD': 0,  # Layer CRS
            'INPUT': outputs['Intersection']['OUTPUT'],
            'OUTPUT': '/home/daviddemmers/Documents/uu/SDA/labs/lab3/data/add_geom.gpkg',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AddGeometryAttributes'] = processing.run('qgis:exportaddgeometrycolumns', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Field calculator
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'product',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': "CASE\nWHEN attribute($currentfeature, 'BU_CODE') IS NULL\nOR attribute($currentfeature, 'P_65_EO_JR') <= 0\nTHEN NULL\nELSE attribute($currentfeature, 'area') * attribute($currentfeature,\n'P_65_EO_JR')\nEND",
            'INPUT': outputs['AddGeometryAttributes']['OUTPUT'],
            'OUTPUT': '/home/daviddemmers/Documents/uu/SDA/labs/lab3/data/calc.gpkg',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculator'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Aggregate
        alg_params = {
            'AGGREGATES': [{'aggregate': 'first_value','delimiter': ',','input': '"Postcode4"','length': 4,'name': 'Postcode4','precision': 0,'type': 10},{'aggregate': 'sum','delimiter': ',','input': '"area"','length': 23,'name': 'area','precision': 15,'type': 6},{'aggregate': 'sum','delimiter': ',','input': '"product"','length': 10,'name': 'product','precision': 3,'type': 6}],
            'GROUP_BY': 'Postcode4',
            'INPUT': outputs['FieldCalculator']['OUTPUT'],
            'OUTPUT': '/home/daviddemmers/Documents/uu/SDA/labs/lab3/data/aggr.gpkg',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Aggregate'] = processing.run('native:aggregate', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Field calculator
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'WVALUE',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': "attribute($currentfeature, 'product') / attribute($currentfeature, 'area')",
            'INPUT': outputs['FieldCalculator']['OUTPUT'],
            'OUTPUT': '/home/daviddemmers/Documents/uu/SDA/labs/lab3/data/final.gpkg',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculator'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        return results

    def name(self):
        return 'AreaInterprolation'

    def displayName(self):
        return 'AreaInterprolation'

    def group(self):
        return 'AreaInterprolation'

    def groupId(self):
        return 'AreaInterprolation'

    def createInstance(self):
        return Areainterprolation()
