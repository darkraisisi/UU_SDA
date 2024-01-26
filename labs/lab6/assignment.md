# Introducion
[Material - exercises](https://campo.computationalgeography.org/courses/campo_static/campo_static.html)

David Demmers

# 1. Static modelling

## 1.1. Campo data and visualisation basics for point objects
### 1.1.3. Point properties
Question: What is a uniform distribution? Why would one use in certain cases a uniform distribution instead of the often used Gaussian distribution?

A uniform distribution is that the entities are divided equally between the bounds. A normal distribution is centered and most likely to occur around a point and show a drop in likelyhood the farther from the center you move.

### 1.1.4 Writing data to disk and visualisation of point properties
`qgis data/roads.gpkg foodstores.gpkg`

## 1.3. Campo data and visualisation basics for field objects
### 1.3.1. Field properties and operations on field properties within a property set
Question: Give two other examples of the use of field-agents in spatial or spatio-temporal simulation.

1. Simulate animal movements and interactions, connections between habitats and interactions and needs of animals will show patterns over time in a certain simulation.

2. Congestion prediciton. Different people travel to different places at different times, this is a great use for temporal changes with agents and random choices.

### 1.3.2. Writing data to disk and visualisation of field properties
`qgis data/roads.gpkg c_*0.tiff foodstores.gpkg`

## 1.5. Operations between property sets: combining different phenomena and property sets
Question: What is approximately the range of values in the propensity of the foodstores? Compare this with the range in the propensity of the households. What is causing the observed difference?

Observed range - foodstores:
- 'MAX': 1.1399099776721668,
- 'MEAN': 0.08159556943042051,
- 'MEDIAN': 0.0402939209493567,
- 'MIN': -0.888756836665335,
- 'RANGE': 2.0286668143375017,
- 'STD_DEV': 0.3797855515605939,

Observed range - households:
- 'MAX': 1.9999409185115544,
- 'MEAN': -0.026357448378548528,
- 'MEDIAN': 0.021785861471864454,
- 'MIN': -1.9827452473587623,
- 'RANGE': 3.9826861658703168,
- 'STD_DEV': 1.175078637055575,

The difference is caused by the one time step, and the different initial values. The houses start between -2 and + 2 and stay tgere, the stores start between 0.01 and 1 and get changed a bit. Where the focus agent has influence the values get changed but this has a small influence as the range is rather small.

Question: What is the effect of the size of the neigbhourhood, for instance 250 or 500 m, on the resulting range in propensity values of the foodstores? Explain your answer.

Observed range - foodstores:
- 'MAX': 0.48834863299759224,
- 'MEAN': 0.011409147154294873,
- 'MEDIAN': -0.021700846113876997,
- 'MIN': -0.34899410319576435,
- 'RANGE': 0.8373427361933565,
- 'STD_DEV': 0.19200602227292382,

Observed range - households:
- 'MAX': 1.998200775244129,
- 'MEAN': 0.022261327066720325,
- 'MEDIAN': 0.007041300573768172,
- 'MIN': -1.9999074274449598,
- 'RANGE': 3.998108202689089,
- 'STD_DEV': 1.1394533757636063,

The observed ranges are different, the foodstores have a way different spread. They all are closer around 0 seen by the mean and median around 0. With the min and max and std showing the spread beeing contained. The larger focus/ influence averages the scores more towards 0.

# 2. Spatio-temporal Modelling

### 2.1. Point agents
Question: How does the value of the propensity change over time? What are the values at the last time step?

The values slowly converge to 0. In the last step every household is at 0.

### 2.2. Field agents used for input in temporal model
Question: What is the highest value of the household propensity in the area at the end of the model run? Does it correspond with what you would expect from the value of the differential equation plot in equations.pdf, centre row, right plot?

Aroung 0.8, This is definately a value that is expected. This equation adds the (positive) impat of the propensity of the stores to the decay of the slope. A couple of slopes converged to 0.8, which is the 0.2 - the max of 1 in the equation.

### 2.3. Field agents in a temporal simulation
Question: What is the spatial pattern in the household propensities at the start, halfway, and at the end of the run? Explain the mechanisms that determine the spatial pattern and how it changes over time.

At the start the household propensities are all equally (as far as visible) distributed between -2 and 2. Before the halfway a large group of household make a sharp change to fit to the propensities of their neighbourhood. And the rest slowly follow this trend to both extremes. At the end almost all households have converged to -2 or 2. Some equilibrium state has been achieved.