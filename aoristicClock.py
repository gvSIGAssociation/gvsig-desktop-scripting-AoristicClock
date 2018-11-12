# encoding: utf-8

import gvsig
from gvsig import geom
import datetime
from java.awt import Color
from org.gvsig.symbology.swing import SymbologySwingLocator
from org.gvsig.fmap.mapcontext import MapContextLocator
from org.gvsig.tools import ToolsLocator
import datetime
import sys
from gvsig.geom import *
import math
from java.awt import Color
from org.gvsig.symbology.fmap.mapcontext.rendering.legend.impl import VectorialIntervalLegend, SingleSymbolLegend
from org.gvsig.symbology.fmap.mapcontext.rendering.legend.styling import LabelingFactory
import pdb
from java.util import Date
from java.util import Calendar
from java.text import SimpleDateFormat
from org.gvsig.expressionevaluator import ExpressionEvaluatorLocator

def main(*args):
  nameFieldHour = "CMPLNT_F_1"
  nameFieldDay = "CMPLNT_FR_"
  # Transformar de antemano a fecha
  patternHour = 'HH:mm:ss'
  patternDay = 'yyyy-MM-dd'
  rangeHoursParameter = "0-10,13"
  rangeDaysParameter = "0, 3-6,7"
  expression = ''
  expression = "OFNS_DESC = 'BURGLARY'"
  xi = 0
  yi = 0
  proportion = 1
  #store = gvsig.currentView().getLayer("20f").getFeatureStore()
  store = gvsig.currentLayer().getFeatureStore()
  aoristicClock(store,
                nameFieldHour,
                nameFieldDay,
                patternHour,
                patternDay,
                rangeHoursParameter,
                rangeDaysParameter,
                expression,
                xi,
                yi,
                proportion)

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
  radius = r + 0.5*factorReduction #(rk/2)#(rk/factorReduction)# + (rk/2)
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

def processRangeHoursParameter(rangesTextParameter):
  #"0-3,5-7"
  ranges = rangesTextParameter.split(",")
  all = []
  for rs in ranges:
    r = rs.split("-")
    if len(r)!=1:
      i=int(r[0])
      f=int(r[1])+1
      if i < 0:
        i=0
      if f>24:
        f=24
      for v in range(i,f):
        all.append(v)
    else:
      v=int(r[0])
      if 0 <= v <= 24:
        all.append(v)
  return all
  
def processRangeDaysParameter(rangesTextParameter):
  #"0-3,5-7"
  ranges = rangesTextParameter.split(",")
  all = []
  for rs in ranges:
    r = rs.split("-")
    if len(r)!=1:
      i=int(r[0])
      f=int(r[1])+1
      if i < 0:
        i=0
      if f>7:
        f=7
      for v in range(i,f):
        all.append(v)
    else:
      v=int(r[0])
      if 0 <= v <= 6:
        all.append(v)
  correction = []
  interChange = {0:Calendar.MONDAY,
          1:Calendar.TUESDAY,
          2:Calendar.WEDNESDAY,
          3:Calendar.THURSDAY,
          4:Calendar.FRIDAY,
          5:Calendar.SATURDAY,
          6:Calendar.SUNDAY
          }
  for i in all:
    correction.append(interChange[i])
  return correction
  
def aoristicClock(store,
                  nameFieldHour,
                  nameFieldDay,
                  patternHour,
                  patternDay,
                  rangeHoursParameter,
                  rangeDaysParameter,
                  expression,
                  xi=0,
                  yi=0,
                  proportion=1,
                  selfStatus=None):
  
  i18nManager = ToolsLocator.getI18nManager()
  
  centroid = geom.createPoint(geom.D2, xi, yi)

  if rangeHoursParameter == "":
      rangeHoursParameter = "0-23"
      
  if rangeDaysParameter == "":
      rangeDaysParameter = "0-6"
      
  try:
    rangeHours = processRangeHoursParameter(rangeHoursParameter)
  except:
    rangeHours = processRangeHoursParameter("0-23")
    print "*****+ error h"

  try:
    rangeDays = processRangeDaysParameter(rangeDaysParameter)
  except:
    rangeDays = processRangeDaysParameter("0-6")
    print "****** error d"
    return

  days = len(rangeDays)
  hours = len(rangeHours)

  internalRadius = 1*proportion
  half_step = 90
  default_segs = 15
  separationGaps = 1
  centerTopSector = False
  radiusInterval = 1*proportion
  iLabel = True
  createSectorLabel=True
  labelOnlyFirstSector = True
  dayOrderRange = [ Calendar.MONDAY,
          Calendar.TUESDAY,
          Calendar.WEDNESDAY,
          Calendar.THURSDAY,
          Calendar.FRIDAY,
          Calendar.SATURDAY,
          Calendar.SUNDAY
          ]
  
  dayNames = {Calendar.MONDAY:i18nManager.getTranslation("_Monday"),
          Calendar.TUESDAY:i18nManager.getTranslation("_Tuesday"),
          Calendar.WEDNESDAY:i18nManager.getTranslation("_Wednesday"),
          Calendar.THURSDAY:i18nManager.getTranslation("_Thursday"),
          Calendar.FRIDAY:i18nManager.getTranslation("_Friday"),
          Calendar.SATURDAY:i18nManager.getTranslation("_Saturday"),
          Calendar.SUNDAY:i18nManager.getTranslation("_Sunday")
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
      radius_interval = (radius / ring_num)*proportion
  last = None
  gaps = 0
  if selfStatus!=None: selfStatus.setRangeOfValues(0,len(rangeHours))
  processText = i18nManager.getTranslation("_Processing")
  for position in range(0, len(rangeHours)): #xrange(0, hours):
    if selfStatus!=None: 
      selfStatus.setProgressText(processText + ": " + str(position)+" / "+str(int(len(rangeHours))))
      if selfStatus.isCanceled() == True:
        ringShape.finishEditing()
        return True
    i = rangeHours[position]
    if len(rangeHours)==(position+1):
      rangePosition = 0
    else:
      rangePosition = position+1
    if i != (rangeHours[rangePosition]-1):
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
    
    rin = (radius+(radius_interval*(1)))*proportion
    rout = radius*proportion
    rin, rout
    prering = create_ring_cell(centroid, from_deg, to_deg, rin, rout, default_segs).centroid()

    for iring, day in enumerate(rangeDays, 1): #range(0, dayOrderRange)
      #day = rangeDays[iring]
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
        pointLocation = getRingInitVertex(ring,centroid, rout,radius_interval, from_deg, proportion)
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
      pointLocation = getRingInitVertex(ring,centroid, rout+radius_interval,radius_interval, from_deg, proportion)
      newFeaturePoint = pointStore.createNewFeature()
      newFeaturePoint.set("LABEL", i)
      newFeaturePoint.set("VALUE", 0)
      newFeaturePoint.set("STRVALUE", " "+str(i)+":00")
      newFeaturePoint.set("ROTATION", from_deg -90)
      newFeaturePoint.set("HOUR", i)
      #newFeaturePoint.set("DAY", iring)
      newFeaturePoint.set("GEOMETRY", pointLocation)
      pointStore.insert(newFeaturePoint)
      #if gaps>0: #create anotation end of gaps time
      #  pointLocation = getRingInitVertex(ring,centroid, rout+radius_interval,radius_interval, to_deg+(1.5*correction_to_deg), 1)
      #  newFeaturePoint = pointStore.createNewFeature()
      #  newFeaturePoint.set("LABEL", i)
      #  newFeaturePoint.set("VALUE", 0)
      #  newFeaturePoint.set("STRVALUE", " "+str(i+1)+":00")
      #  newFeaturePoint.set("ROTATION", (to_deg+(1.5*correction_to_deg))-90)
      #  newFeaturePoint.set("HOUR", i)
      #  #newFeaturePoint.set("DAY", iring)
      #  newFeaturePoint.set("GEOMETRY", pointLocation)
      #  pointStore.insert(newFeaturePoint)
    if labelOnlyFirstSector:
      labelOnlyFirstSector = False
    idx_side  += 1
  ringShape.commit()

  ###
  ### GET VALUES
  ###
  if expression != '':
    expressionEvaluatorManager = ExpressionEvaluatorLocator.getManager()
    try:
      evaluator = expressionEvaluatorManager.createEvaluator(expression)
      fq = store.createFeatureQuery()
      fq.addFilter(evaluator)
      fset = store.getFeatureSet(fq)
    except:
      fset = store.getFeatureSet()
  else:
    fset = store.getFeatureSet()
 
  ###
  ### INIT DICT 
  ###
  
  dictValues = {}
  for d in dayOrderRange:
    dictHour={}
    for h in range(0,24):
      dictHour[h] = 0
    dictValues[d] = dictHour

  ###
  ### FILL DICT
  ###
  for f in fset:
    dateFieldHour = getFieldAsDate(f.get(nameFieldHour), patternHour)
    dateFieldDay = getFieldAsDate(f.get(nameFieldDay), patternDay)
    
    if isinstance(dateFieldDay, Date) and isinstance(dateFieldHour, Date):
      cal = Calendar.getInstance()
      cal.setTime(dateFieldDay)
      day = cal.get(Calendar.DAY_OF_WEEK)
      cal = Calendar.getInstance()
      cal.setTime(dateFieldHour)
      hour = cal.get(Calendar.HOUR_OF_DAY)
      dictValues[day][hour] += 1
  
  ###
  ### FILL SHAPE WITH VALUES
  ###
  ringShape.edit()
  store = ringShape.getFeatureStore()
  fset = store.getFeatureSet()
  for f in fset:
    e = f.getEditable()
    h = f.get("HOUR")
    d = f.get("DAY")
    e.set("VALUE", dictValues[d][h])
    fset.update(e)
  
  ###
  ### FINISH
  ###
  ringShape.commit()
  ringShape.setName("Ao-Clock")
  pointShape.commit()
  pointShape.setName("Ao-Label")
  gvsig.currentView().addLayer(ringShape)
  gvsig.currentView().addLayer(pointShape)

  ###
  ### LEGEND AND LABELS
  ###
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
  
  leg = SingleSymbolLegend()
  leg.setShapeType(geom.POINT)
  manager = leg.getSymbolManager()
  pointSymbol = manager.createSymbol(geom.POINT)
  pointSymbol.setColor(Color.black)
  pointSymbol.setSize(0)
  leg.setDefaultSymbol(pointSymbol)
  pointShape.setLegend(leg)
  return True
    
def main1(*args):
  print processRangeDaysParameter("0,2,3,6,9")


def getFieldAsDate(field, pattern):
    if isinstance(field, unicode):
      formatter = SimpleDateFormat(pattern)
      newDate = formatter.parse(field)
      return newDate
    elif isinstance(field, Date):
      return field
    else:
      return None

  
