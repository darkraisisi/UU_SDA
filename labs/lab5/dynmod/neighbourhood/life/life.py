from pcraster import *
from pcraster.framework import *
class MyFirstModel(DynamicModel):
  def __init__(self):
    DynamicModel.__init__(self)
    setclone('clone.map')
  def initial(self):
    aUniformMap = uniform(1)
    self.report(aUniformMap,'uni')
    self.alive = aUniformMap < 0.1
    self.report(self.alive,'ini')
  def dynamic(self):
    aliveScalar=scalar(self.alive)
    numberOfAliveNeighbours=windowtotal(aliveScalar,3)-aliveScalar;
    self.report(numberOfAliveNeighbours,'na')
    threeAliveNeighbours = numberOfAliveNeighbours == 3
    self.report(threeAliveNeighbours,'tan')
    birth=pcrand(threeAliveNeighbours,pcrnot(self.alive))

nrOfTimeSteps=1
myModel = MyFirstModel()
dynamicModel = DynamicFramework(myModel,nrOfTimeSteps)
dynamicModel.run()

  




