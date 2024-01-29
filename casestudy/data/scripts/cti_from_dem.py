"""
Model exported as python.
Name : cti_from_dem
Group : dem
With QGIS : 32204
"""
import sys
sys.path.insert(0,"/usr/lib/python3/dist-packages")

# export LD_LIBRARY_PATH=/<qgispath>/lib

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterRasterDestination
import processing


class Cti_from_dem(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer('dem', 'dem', defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('resolution', 'resolution', type=QgsProcessingParameterNumber.Double, minValue=0.01, maxValue=100, defaultValue=2))
        self.addParameter(QgsProcessingParameterRasterDestination('Twi', 'TWI', createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(5, model_feedback)
        results = {}
        outputs = {}

        # Flow accumulation (qm of esp)
        # Will calculate for each pixel the contributing upslope area.
        alg_params = {
            'DEM': parameters['dem'],
            'DZFILL': 0.01,
            'PREPROC': 1,  # [1] fill sinks temporarily
            'FLOW': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FlowAccumulationQmOfEsp'] = processing.run('sagang:flowaccumulationqmofesp', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Slope
        alg_params = {
            'AS_PERCENT': False,
            'BAND': 1,
            'COMPUTE_EDGES': False,
            'EXTRA': '',
            'INPUT': parameters['dem'],
            'OPTIONS': '',
            'SCALE': 1,
            'ZEVENBERGEN': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Slope'] = processing.run('gdal:slope', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Modify slopes - Raster calculator
        # Remove zero's from the map as later on the natural log will be taken on this map, this will cause problems.
        alg_params = {
            'CELLSIZE': 0,
            'CRS': None,
            'EXPRESSION': '("\'Slope\' from algorithm \'Slope\'@1"  <= 0) * 1 + ("\'Slope\' from algorithm \'Slope\'@1" > 0) * "\'Slope\' from algorithm \'Slope\'@1"',
            'EXTENT': None,
            'LAYERS': outputs['Slope']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ModifySlopesRasterCalculator'] = processing.run('qgis:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Degrees to Radians - Raster calculator
        alg_params = {
            'CELLSIZE': 0,
            'CRS': None,
            'EXPRESSION': '"\'Output\' from algorithm \'Modify slopes - Raster calculator\'@1" * 0.01745',
            'EXTENT': None,
            'LAYERS': outputs['ModifySlopesRasterCalculator']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DegreesToRadiansRasterCalculator'] = processing.run('qgis:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # TWI - Raster calculator
        #  ln( ("'upslope_area' from algorithm 'Flow accumulation (qm of esp)'@1" + 1 * "resolution") / tan("'slope_radians' from algorithm 'Raster calculator'@1"))
        alg_params = {
            'CELLSIZE': parameters['resolution'],
            'CRS': None,
            'EXPRESSION': f'ln( ("\'Contributing Area\' from algorithm \'Flow accumulation (qm of esp)\'@1 * {parameters["resolution"]} * {parameters["resolution"]}) / tan("\'Output\' from algorithm \'Degrees to Radians - Raster calculator\'@1"))',
            'EXTENT': None,
            'LAYERS': [outputs['DegreesToRadiansRasterCalculator']['OUTPUT'],outputs['FlowAccumulationQmOfEsp']['FLOW']],
            'OUTPUT': parameters['Twi']
        }
        outputs['TwiRasterCalculator'] = processing.run('qgis:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Twi'] = outputs['TwiRasterCalculator']['OUTPUT']
        return results

    def name(self):
        return 'cti_from_dem'

    def displayName(self):
        return 'cti_from_dem'

    def group(self):
        return 'dem'

    def groupId(self):
        return 'dem'

    def createInstance(self):
        return Cti_from_dem()

if __name__ == "__main__":
    mdl = Cti_from_dem()
    x = mdl.displayName()
    print(x)