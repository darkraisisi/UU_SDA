from pcraster import *
from pcraster.framework import *
class MyFirstModel(DynamicModel):
    def __init__(self):
        DynamicModel.__init__(self)
        setclone('dem.map')

    def initial(self):
        dem = self.readmap('dem')
        self.snow = 0.0
        self.maxSnowThickness = 0.0
        elevationMeteoStation = 2058.1
        elevationAboveMeteoStation = dem - elevationMeteoStation
        temperatureLapseRate = 0.005
        self.temperatureCorrection = elevationAboveMeteoStation * \
        temperatureLapseRate
        self.report(self.temperatureCorrection,'tempCor')
        
        self.ldd=lddcreate(dem,1e31,1e31,1e31,1e31)
        self.report(self.ldd,'ldd')

    def dynamic(self):
        precipitation = timeinputscalar('precip.tss',1)
        self.report(precipitation,'pFromTss')
        temperatureObserved = timeinputscalar('temp.tss',1)
        self.report(temperatureObserved,'tempObs')

        temperature= temperatureObserved - self.temperatureCorrection
        self.report(temperature,'temp')
        
        freezing=temperature < 0.0
        self.report(freezing,'fr')
        snowFall=ifthenelse(freezing,precipitation,0.0)
        self.report(snowFall,'snF')
        rainFall=ifthenelse(pcrnot(freezing),precipitation,0.0)
        self.report(rainFall,'rF')
        
        self.snow = self.snow + snowFall
        
        potentialMelt = ifthenelse(pcrnot(freezing),temperature*0.01,0)
        self.report(potentialMelt,'pmelt')
        actualMelt = min(self.snow, potentialMelt)
        self.report(actualMelt,'amelt')
        
        self.snow = self.snow - actualMelt
        self.report(self.snow,'snow')
        
        runoffGenerated = actualMelt + rainFall
        self.report(runoffGenerated,'rg')
        discharge=accuflux(self.ldd,runoffGenerated*cellarea())
        self.report(discharge,'q')
        
        snowInSkiRegion = areaaverage(self.snow,self.skiRegions)
        self.report(snowInSkiRegion,'avsn')
        thickEnough = ifthenelse(self.snow > 0.2, boolean(1), boolean(0))
        self.report(thickEnough,'th')
        numberCellsThickEnough = areatotal(scalar(thickEnough),self.skiRegions)
        self.report(numberCellsThickEnough,'nth')
        proportionThickEnough = numberCellsThickEnough / self.numberCellsRegion
        self.report(proportionThickEnough,'ski')
        
        self.maxSnowThickness = max(self.snow,self.maxSnowThickness)
        self.report(self.maxSnowThickness,'max')

nrOfTimeSteps=181
myModel = MyFirstModel()
dynamicModel = DynamicFramework(myModel,nrOfTimeSteps)
dynamicModel.run()