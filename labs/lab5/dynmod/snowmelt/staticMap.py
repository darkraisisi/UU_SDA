from pcraster import *
from pcraster.framework import *
class MyFirstModel(DynamicModel):
    def __init__(self):
        DynamicModel.__init__(self)
        setclone('dem.map')

    def initial(self):
        dem = self.readmap('dem')
        slopeOfDem = slope(dem)
        self.report(slopeOfDem,'gradient')

    def dynamic(self):
        precipitation=self.readmap('precip')
        precipitationMMPerHour=precipitation*1000.0
        self.report(precipitationMMPerHour,'pmm')
        highPrecipitation=precipitation > 0.01
        self.report(highPrecipitation,'high')

nrOfTimeSteps=181
myModel = MyFirstModel()
dynamicModel = DynamicFramework(myModel,nrOfTimeSteps)
dynamicModel.run()