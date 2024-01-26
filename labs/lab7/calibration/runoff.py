from pcraster import *
from pcraster.framework import *


# helper function 1 to read values from a map
def getCellValue(Map, Row, Column):
    Value, Valid=cellvalue(Map, Row, Column)
    if Valid:
      return Value
    else:
      raise RuntimeError('missing value in input of getCellValue')

# helper function 2 to read values from a map
def getCellValueAtBooleanLocation(location,map):
    # map can be any type, return value always float
    valueMap=mapmaximum(ifthen(location,scalar(map)))
    value=getCellValue(valueMap,1,1)
    return value


class MyFirstModel(DynamicModel):
    def __init__(self, meltRateParameter):
        DynamicModel.__init__(self)
        setclone('clone.map')

        # assign 'external' input to the model variable
        self.meltRateParameter = meltRateParameter 

    def initial(self):
        self.clone = self.readmap('clone')

        dem = self.readmap('dem')

        # elevation (m) of the observed meteorology, this is taken from the
        # reanalysis input data set
        elevationMeteoStation = 1180.0
        elevationAboveMeteoStation = dem - elevationMeteoStation
        temperatureLapseRate = 0.005
        self.temperatureCorrection = elevationAboveMeteoStation * temperatureLapseRate

        # potential loss of water to the atmosphere (m/day)
        self.atmosphericLoss = 0.002 

        # infiltration capacity, m/day
        self.infiltrationCapacity = scalar(0.0018 * 24.0)

        # proportion of subsurface water that seeps out to surface water per day
        self.seepageProportion =  0.06 

        # amount of water in the subsurface water (m), initial value
        self.subsurfaceWater = 0.0

        # amount of upward seepage from the subsurface water (m/day), initial value
        self.upwardSeepage = 0.0
 
        # snow thickness (m), initial value
        self.snow = 0.0

        # flow network
        self.ldd = self.readmap('ldd')

        # location where streamflow is measured (and reported by this model)
        self.sampleLocation = self.readmap("sample_location")

        # initialize streamflow timeseries for directly writing to disk
        self.runoffTss = TimeoutputTimeseries("streamflow_modelled", self, self.sampleLocation, noHeader=True)
        # initialize streamflow timeseries as numpy array for directly writing to disk
        self.simulation = numpy.zeros(self.nrTimeSteps())


    def dynamic(self):
        precipitation = timeinputscalar('precipitation.txt',self.clone)/1000.0
        temperatureObserved = timeinputscalar('temperature.txt',self.clone)
        temperature = temperatureObserved - self.temperatureCorrection

        freezing=temperature < 0.0
        snowFall=ifthenelse(freezing,precipitation,0.0)
        rainFall=ifthenelse(pcrnot(freezing),precipitation,0.0)

        self.snow = self.snow+snowFall

        potentialMelt = ifthenelse(pcrnot(freezing),temperature * self.meltRateParameter, 0)
        actualMelt = min(self.snow, potentialMelt)

        self.snow = self.snow - actualMelt

        # sublimate first from atmospheric loss
        self.sublimation = min(self.snow,self.atmosphericLoss)
        self.snow = self.snow - self.sublimation
   
        # potential evapotranspiration from subsurface water (m/day)
        self.potential_evapotranspiration = max(self.atmosphericLoss - self.sublimation,0.0)

        # actual evapotranspiration from subsurface water (m/day)
        self.evapotranspiration = min(self.subsurfaceWater, self.potential_evapotranspiration)

        # subtract actual evapotranspiration from subsurface water
        self.subsurfaceWater = max(self.subsurfaceWater - self.evapotranspiration, 0)

        # available water on surface (m/day) and infiltration
        availableWater = actualMelt + rainFall
        infiltration = min(self.infiltrationCapacity,availableWater)
        self.runoffGenerated = availableWater - infiltration

        # streamflow in m water depth per day
        discharge = accuflux(self.ldd,self.runoffGenerated + self.upwardSeepage)

        # upward seepage (m/day) from subsurface water
        self.upwardSeepage = self.seepageProportion * self.subsurfaceWater 

        # update subsurface water
        self.subsurfaceWater = max(self.subsurfaceWater + infiltration - self.upwardSeepage, 0)

        # convert streamflow from m/day to m3 per second
        dischargeMetrePerSecond = (discharge * cellarea()) / (24 * 60 * 60)
        # sample the discharge to be stored as timeseries file
        self.runoffTss.sample(dischargeMetrePerSecond)

        # read streamflow at the observation location 
        runoffAtOutflowPoint=getCellValueAtBooleanLocation(self.sampleLocation,dischargeMetrePerSecond)
        # insert it in place in the output numpy array
        self.simulation[self.currentTimeStep() - 1] = runoffAtOutflowPoint

        # report every x days (change % 1 to e.g. % 10 to report every ten days)
        if self.currentTimeStep() % 1 == 0:
            self.report(self.snow,'snow')
            self.report(self.subsurfaceWater,'sub')
            self.report(dischargeMetrePerSecond,'dis')
        # read observed discharge
        dis_obs = timeinputscalar('streamflow.txt', ifthen(self.sampleLocation,boolean(1)))
        # modelled minus observed discharge
        disMmO = dischargeMetrePerSecond - dis_obs
        # write to disk
        self.report(disMmO, "dMm0")
        self.report(dis_obs, 'd0')

nrOfTimeSteps=1461

# read the observed streamflow from disk and store in numpy array
streamFlowObservedFile = open("streamflow.txt", "r")
streamFlowObserved = numpy.zeros(nrOfTimeSteps)
streamFlowObservedFileContent = streamFlowObservedFile.readlines()
for i in range(0,nrOfTimeSteps):
    splitted = str.split(streamFlowObservedFileContent[i])
    dischargeModelled = splitted[1]
    streamFlowObserved[i]=float(dischargeModelled)
streamFlowObservedFile.close()


# run the model with a particular value of the meltrate parameter
# for brute force calibration put the code below in a loop
meltRateParameter = 0.003
myModel = MyFirstModel(meltRateParameter)
dynamicModel = DynamicFramework(myModel,nrOfTimeSteps)
dynamicModel.setQuiet()
dynamicModel.run()
# obtain modelled streamflow
streamFlowModelled = myModel.simulation
# calculate objective function, i.e. mean of sum of squares and ignore first year
SS = numpy.mean((streamFlowModelled[365:] - streamFlowObserved[365:])**2.0)
print('meltrate parameter is:', meltRateParameter, 'sum of squares is ', SS)
