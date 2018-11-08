# encoding: utf-8

import gvsig
from gvsig import geom
import datetime
from org.gvsig.symbology.fmap.mapcontext.rendering.legend.styling import LabelingFactory
from org.gvsig.symbology.fmap.mapcontext.rendering.legend.impl import SingleSymbolLegend
from java.awt import Color
from org.gvsig.symbology.swing import SymbologySwingLocator
from org.gvsig.fmap.mapcontext import MapContextLocator
from org.gvsig.tools import ToolsLocator
import datetime
import sys

def main(*args):
  proportionX = 1
  proportionY = 1
  nameFieldHour = "HORA"
  nameFieldDay = "DIA"
  patternHour = '%H:%M:%S'
  patternDay = '%Y-%m-%d'
  xi = 0
  yi = 0
  #store = gvsig.currentView().getLayer("20f").getFeatureStore()
  store = gvsig.currentLayer().getFeatureStore()
  aoristicClock(store,
                      proportionX,
                      proportionY,
                      nameFieldHour,
                      nameFieldDay,
                      patternHour,
                      patternDay,
                      0,
                      0)
  



from gvsig.geom import *
import math
from java.awt import Color
from org.gvsig.symbology.fmap.mapcontext.rendering.legend.impl import VectorialIntervalLegend, SingleSymbolLegend
from org.gvsig.symbology.fmap.mapcontext.rendering.legend.styling import LabelingFactory
import pdb
# math.radians(x)
to_radian = lambda degree: math.pi / 180.0 * degree
# math.degrees(x)
to_degree = lambda radian: radian * (180.0 / math.pi)

# create_point
def create_point(centroid, radian, radius):
    dx = math.cos(radian) * radius
    dy = math.sin(radian) * radius
    x = centroid.getX()
    y = centroid.getY()
    return createPoint(D2, x + dx, y + dy)
    
# create_ring_cell
def create_ring_cell(centroid, from_deg, to_deg, from_radius, to_radius, default_segs):
  step = abs(to_deg - from_deg) / default_segs
  radian = 0.0
  outer_ring = []
  # first interior
  first = True
  for index in xrange(default_segs+1):
    radian = to_radian(from_deg - (index * step))
    outer_ring.append(create_point(centroid, radian, from_radius))
    if first==True:
      point1 = create_point(centroid, radian, from_radius)
      first = False
  
  # second outer
  for index in xrange(default_segs,-1,-1):
    radian = to_radian(from_deg-(index * step))
    outer_ring.append(create_point(centroid, radian, to_radius))

  outer_ring.append(point1)
  polygon = createPolygon(D2, outer_ring)
  #print polygon
  #g = createGeometry(POLYGON, D2)
  #for i in outer_ring:
  #  g.addVertex(i)
  return polygon
    
                
def getRingInitVertex(ring, centroid, r, rk, deg, factorReduction):
  radius = r + 0.5 #(rk/2)#(rk/factorReduction)# + (rk/2)
  radian = to_radian(deg)
  point = create_point(centroid, radian, radius)
  return point
  
def getRingCentroid(ring, centroid, r, rk,from_deg, to_deg, factorReduction):
  d = (from_deg + to_deg)/2
  radius = r + (rk/factorReduction)
  radian = to_radian(d)
  point = create_point(centroid, radian, radius)
  return point

def getRadiusFromEnvelope(envelope):
  minx = envelope.getLowerCorner().getX()
  miny = envelope.getLowerCorner().getY()
  maxx = envelope.getUpperCorner().getX()
  maxy = envelope.getUpperCorner().getY()
  radius = (((maxx - minx)**2 + (maxy - miny)**2) **0.5) / 2.0
  return radius

def aoristicClock(store,
                      proportionX,
                      proportionY,
                      nameFieldHour,
                      nameFieldDay,
                      patternHour,
                      patternDay,
                      xi=0,
                      yi=0,
                      selfStatus=None):
  print "AoristicClock func"
  centroid = geom.createPoint(geom.D2, 0, 0)
  # 24 sectores
  # 7 ciruclos
  #hours = 24
  #days = 7
  
  rangeHours = [0,3] #1,2,3,6,7,10,11,22,23] #,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
  rangeDays = [0,1,2,6] #,4,5,6]
  days = len(rangeDays) #rangeDays[1] - rangeDays[0]
  hours = len(rangeHours) #rangeHours[1] - rangeHours[0]
  
  internalRadius = 1
  half_step = 90
  default_segs = 15
  separationGaps = 1
  centerTopSector = False
  radiusInterval = 1
  iLabel = True
  createSectorLabel=True
  labelOnlyFirstSector = True
  dayNames = {
      0:"_Monday",
      1:"_Tuesday",
      2:"_Wednesday",
      3:"_Thursday",
      4:"_Friday",
      5:"_Satuday",
      6:"_Sunday"
      }
  # Prepare schema
  newSchema = gvsig.createFeatureType()
  newSchema.append("LABEL", "STRING", 20)
  newSchema.append("VALUE", "DOUBLE", 20,5)
  newSchema.append("DAY", "INTEGER", 10)
  newSchema.append("HOUR", "INTEGER", 10)
  newSchema.append("ROTATION", "DOUBLE", 10,5)
  newSchema.append("GEOMETRY", "GEOMETRY")
  newSchema.get("GEOMETRY").setGeometryType(POLYGON, D2)
  ringShape = gvsig.createShape(newSchema)

  # Point-label shape
  pointSchema = gvsig.createFeatureType(ringShape.getFeatureStore().getDefaultFeatureType())
  pointSchema.append("STRVALUE", "STRING", 20)
  pointSchema.get("GEOMETRY").setGeometryType(POINT, D2)
  pointShape = gvsig.createShape(pointSchema)
  pointStore=pointShape.getFeatureStore()
  pointShape.edit()
  
  # Vars
  ringStore = ringShape.getFeatureStore()
  ringShape.edit()

  ring_num = days
  
  step_angle = 360.0 / hours
  if centerTopSector:
    half_step = half_step + (step_angle/2) #-((default_segs*gaps)/2)

  idx_side = 0

  
  if internalRadius > 0:
    radius = internalRadius
  # Prepare radiusInterval
  if radiusInterval > 0:
      radius_interval = radiusInterval
  else:
      radius_interval = radius / ring_num
  last = None
  gaps = 0
  for position in range(0, len(rangeHours)): #xrange(0, hours):
    i = rangeHours[position]
    if len(rangeHours)==(position+1):
      rangePosition = 0
    else:
      rangePosition = position+1
    if i != (rangeHours[rangePosition]-1):
      print i, rangeHours[rangePosition]
      if i==23 and rangeHours[rangePosition]==0:
        gaps = 0
      else:
        gaps=separationGaps
    else:
      gaps=0
    correction_from_deg = (((step_angle/default_segs)*0)/2)
    correction_to_deg = (((step_angle/default_segs)*gaps)/2)
  
    from_deg = half_step - (idx_side * step_angle) - correction_from_deg
    to_deg = half_step - ((idx_side + 1) * step_angle) + correction_to_deg
    # Get closest
    rin = radius+(radius_interval*(1))
    rout = radius
    rin, rout
    prering = create_ring_cell(centroid, from_deg, to_deg, rin, rout, default_segs).centroid()

    for iring in range(0, len(rangeDays)): #xrange(0, days):
      day = rangeDays[iring]
      new = ringStore.createNewFeature()
      rin = radius+(radius_interval*(iring+1))
      rout = radius+(radius_interval*iring)
      ring = create_ring_cell(centroid, from_deg, to_deg, rin, rout,  default_segs)
      #new.set("LABEL", fields[iring])
      #new.set("VALUE", feature.get(fields[iring]))
      #rotation = ((from_deg + to_deg) / 2)-90
      rotation = from_deg - 90
      if -90 < rotation < -240:
        rotation+=180
      new.set("ROTATION", rotation)
      new.set("HOUR", i)
      new.set("DAY", day)
      new.set("GEOMETRY", ring)
      ringStore.insert(new)
      if iLabel==True and labelOnlyFirstSector==True:
        pointLocation = getRingInitVertex(ring,centroid, rout,radius_interval, from_deg, 1)
        newFeaturePoint = pointStore.createNewFeature()
        newFeaturePoint.set("LABEL", day)
        #newFeaturePoint.set("VALUE", feature.get(fields[iring]))
        newFeaturePoint.set("STRVALUE", str(dayNames[day]))
        newFeaturePoint.set("ROTATION", rotation)
        newFeaturePoint.set("HOUR", i)
        newFeaturePoint.set("DAY", day)
        newFeaturePoint.set("GEOMETRY", pointLocation)
        pointStore.insert(newFeaturePoint)
        
    if createSectorLabel==True:
      pointLocation = getRingInitVertex(ring,centroid, rout+radius_interval,radius_interval, from_deg, 5)
      newFeaturePoint = pointStore.createNewFeature()
      newFeaturePoint.set("LABEL", i)
      newFeaturePoint.set("VALUE", 0)
      newFeaturePoint.set("STRVALUE", " "+str(i)+":00")
      newFeaturePoint.set("ROTATION", from_deg -90)
      newFeaturePoint.set("HOUR", i)
      #newFeaturePoint.set("DAY", iring)
      newFeaturePoint.set("GEOMETRY", pointLocation)
      pointStore.insert(newFeaturePoint)
      if gaps>0:
        pointLocation = getRingInitVertex(ring,centroid, rout+radius_interval,radius_interval, to_deg+(1.5*correction_to_deg), 1)
        newFeaturePoint = pointStore.createNewFeature()
        newFeaturePoint.set("LABEL", i)
        newFeaturePoint.set("VALUE", 0)
        newFeaturePoint.set("STRVALUE", " "+str(i+1)+":00")
        newFeaturePoint.set("ROTATION", (to_deg+(1.5*correction_to_deg)) -90)
        newFeaturePoint.set("HOUR", i)
        #newFeaturePoint.set("DAY", iring)
        newFeaturePoint.set("GEOMETRY", pointLocation)
        pointStore.insert(newFeaturePoint)
    if labelOnlyFirstSector:
      labelOnlyFirstSector = False
    idx_side  += 1
  ringShape.commit()


  # Get values
  fset = store.getFeatureSet()
  # init dict
  dictValues = {}
  for d in rangeDays:
    dictHour={}
    for h in rangeHours:
      dictHour[h] = 0
    dictValues[d] = dictHour
  
  for f in fset:
    fieldHour = f.get(nameFieldHour)
    fieldDay = f.get(nameFieldDay)
    d = datetime.datetime.strptime(fieldHour, patternHour).time()
    hour = d.hour
    dday = datetime.datetime.strptime(fieldDay, patternDay)
    day = dday.weekday()
    try:
      dictValues[day][hour] += 1
    except:
      pass

  # Fill values
  ringShape.edit()
  store = ringShape.getFeatureStore()
  fset = store.getFeatureSet()
  for f in fset:
    e = f.getEditable()
    h = f.get("HOUR")
    d = f.get("DAY")
    e.set("VALUE", dictValues[d][h])
    fset.update(e)

  # Commits
  ringShape.commit()
  ringShape.setName("Ao-Clock")
  pointShape.commit()
  pointShape.setName("Ao-Label")
  gvsig.currentView().addLayer(ringShape)
  gvsig.currentView().addLayer(pointShape)
  
  # Legend
  try:
    vil = VectorialIntervalLegend(POLYGON)
    vil.setStartColor(Color.green)
    vil.setEndColor(Color.red)
    vil.setIntervalType(1)
    ii = vil.calculateIntervals(ringShape.getFeatureStore(), "VALUE", 5, POLYGON)
    
    vil.setIntervals(ii)
    vil.setClassifyingFieldTypes([7])
    ringShape.setLegend(vil)
  except:
    pass
  ds = LabelingFactory().createDefaultStrategy(pointShape)
  ds.setTextField("STRVALUE")
  ds.setRotationField("ROTATION")
  ds.setFixedSize(20)
  pointShape.setLabelingStrategy(ds)
  pointShape.setIsLabeled(True)
  print "DONE"
    
def main1(*args):
  # Inputs
  idStore = "refman"
  idTable = "refman"
  fields = ["pob_0_14", "pob_15_65", "pob_66_mas"]
  #fields = ["Campo1", "Campo2"] #, "Campo3"]
  #fields = ["Campo1"]
  #layerName = "ejemplo_puntos"
  layerName = "pob_5fs"
  #layerName = "fewlines"
  store = gvsig.currentView().getLayer(layerName).getFeatureStore()
  table = gvsig.currentView().getLayer(layerName).getFeatureStore()
  #store = gvsig.currentLayer().getFeatureStore()
  #table = gvsig.currentLayer().getFeatureStore()
  default_segs = 15
  gaps = 1
  half_step = 90
  internalRadius = 0
  radiusInterval = 0
  centerTopSector = True
  iLabel = True
  labelOnlyFirstSector = False
  createSectorLabel = True
  createRingMap(store, table, idStore, idTable, fields, default_segs, gaps, half_step, internalRadius, radiusInterval, centerTopSector,iLabel, labelOnlyFirstSector, createSectorLabel)







  
