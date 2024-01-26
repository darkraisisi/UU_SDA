import os
import qgis.core as qc
import qgis.gui as qgui
import qgis.utils as qutil
import qgis.PyQt.QtCore as qpy_c
import qgis.PyQt.QtGui as qpy_gui
from math import sqrt

# Create a reference to the QgsApplication. Setting the
# second argument to False disables the GUI.
qgs = qc.QgsApplication([], True)
# Load providers

qgs.initQgis()
local = r"/home/daviddemmers/Documents/uu/SDA/labs/lab1"
tutorial_schools = os.path.join(local,"schools_poly_osm.geojson")
assignment_toilets = os.path.join(local,"assignment/complete_toilets_points_osm.geojson")

def getExtent(layer):
    ext = layer.extent()
    xmin = ext.xMinimum()
    xmax = ext.xMaximum()
    ymin = ext.yMinimum()
    ymax = ext.yMaximum()
    coords = "%f\n%f\n%f\n%f" % (xmin, xmax, ymin, ymax)
    # this is a string that stores the coordinates
    print("Extent is "+coords)
    return coords

def getsmallestlength(ring, smallestlength):
    lastpoint = None
    for point in ring:
        length = smallestlength
        if lastpoint is not None:
            length = sqrt(point.sqrDist(lastpoint))
        lastpoint = point
        if length < smallestlength:
            smallestlength = length
    return smallestlength

def getResolution(layer):
    features = layer.getFeatures()
    smallestLength = 1000
    nofeatures = 0

    for feature in features:
        geom = feature.geometry()
        nofeatures +=1
        geotype = ""
        if geom.wkbType() == qc.QgsWkbTypes.MultiPolygon:
            geotype = "MultiPolygon"
            x = geom.asMultiPolygon()
            numPts = 0
            for polyg in x:
                for ring in polyg:
                    numPts += len(ring)
                    smallestLength = getsmallestlength(ring,smallestLength)
    print(geotype)
    print("smallest distinguishable length : " + str(smallestLength) + " in "+ str(nofeatures) +" " + geotype+"features")


# vlayer = qc.QgsVectorLayer(os.path.join(local,r"Lab1 data-quality/basisschoolen.shp"), "Basisschoolen", "ogr")
vlayer = qc.QgsVectorLayer(tutorial_schools, "Basisschoolen", "ogr")
_ = getExtent(vlayer)
_ = getResolution(vlayer)

vlayer = qc.QgsVectorLayer(assignment_toilets, "Toilets", "ogr")
_ = getExtent(vlayer)


qgs.exitQgis()

# Measuring completeness and spatial accuracy
# How to assess completeness and spatial accuracy

# a: 61 matched schools / 75 schoolwijzer schools. = 0.813 = 81%
# b: 'MEAN': 44.54871072520187 