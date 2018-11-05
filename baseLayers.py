# encoding: utf-8

import gvsig
from gvsig import geom
import datetime
from org.gvsig.symbology.fmap.mapcontext.rendering.legend.styling import LabelingFactory
from org.gvsig.symbology.fmap.mapcontext.rendering.legend.impl import SingleSymbolLegend
from java.awt import Color

def main(*args):
  proportionX = 1
  proportionY = 1
  createBaseLayers(proportionX, proportionY)
  
  
  # Setting coordinates to aoristic clock
  nameFieldHour = "HORA"
  nameFieldDay = "DIA"
  layer = gvsig.currentLayer()
    
  # New points layer
  schema = gvsig.createFeatureType(layer.getFeatureStore().getDefaultFeatureType()) # DefaultFeatureType
  newPoints = gvsig.createShape(schema)

  # Transform
  set = layer.getFeatureStore().getFeatureSet()
  newPoints.edit()
  store = newPoints.getFeatureStore()
  for f in set:
    fieldHour = f.get(nameFieldHour)
    d = datetime.datetime.strptime(fieldHour, '%H:%M:%S').time()
    totalSecs = float(d.minute*60 + d.second)/3600
    x = float(d.hour) + float(totalSecs)
    x = x * proportionX
    fieldDay = f.get(nameFieldDay)
    dday = datetime.datetime.strptime(fieldDay, '%Y-%m-%d')
    y = dday.weekday()
    y = y * proportionY
    
    nf = store.createNewFeature(f)
    newGeom = geom.createPoint(geom.D2, x, y)
    nf.setDefaultGeometry(newGeom)
    store.insert(nf)
  newPoints.commit()
  gvsig.currentView().addLayer(newPoints)
    
  
def createBaseLayers( proportionX = 1, proportionY = 1):

  schema = gvsig.createFeatureType() # DefaultFeatureType
  schema.append("GEOMETRY", "GEOMETRY")
  schema.get("GEOMETRY").setGeometryType(geom.LINE, geom.D2)
  baseLines = gvsig.createShape(schema)

  schema = gvsig.createFeatureType() # DefaultFeatureType
  schema.append("LABEL", "STRING", 20)
  schema.append("GEOMETRY", "GEOMETRY")
  schema.get("GEOMETRY").setGeometryType(geom.POINT, geom.D2)
  basePoints = gvsig.createShape(schema)
  days = {0:"Monday",
          1:"Tuesday",
          2:"Wednesday",
          3:"Thursday",
          4:"Friday",
          5:"Saturday",
          6:"Sunday"
          }

  # Y axis: Days
  
  numberDays = 7
  numberHours = 24
  
  for k in range(0, numberHours+1):
    line = geom.createGeometry(geom.LINE)
    for i in range(0,numberDays):
      x = proportionX * k
      y = proportionY * i
      point = geom.createPoint(geom.D2,x, y)
      line.addVertex(point)
      if i==numberDays-1:
        x = x
        y = y+0.2
        point = geom.createPoint(geom.D2,x, y)
        basePoints.append({"LABEL":k,"GEOMETRY":point})
      
    baseLines.append({"GEOMETRY": line})
  
  # X axis: Days
  numberDays = 7
  numberHours = 24
  
  for i in range(0, numberDays):
    line = geom.createGeometry(geom.LINE)
    x = 0
    y = proportionY * i
    point = geom.createPoint(geom.D2,x, y)
    line.addVertex(point)
    
    x = proportionX * numberHours
    point = geom.createPoint(geom.D2,x, y)
    line.addVertex(point)
      
    baseLines.append({"GEOMETRY": line})

    x = -2.5
    y = y - 0.2
    point = geom.createPoint(geom.D2,x, y)
    basePoints.append({"LABEL":days[i],"GEOMETRY":point})

  # Commits
  basePoints.commit()
  baseLines.commit()
  
  # Labels and legends
  ds = LabelingFactory().createDefaultStrategy(basePoints)
  
  ds.setTextField("LABEL")
  ds.setFixedSize(20)
  basePoints.setLabelingStrategy(ds)
  basePoints.setIsLabeled(True)

  leg = SingleSymbolLegend()
  leg.setShapeType(geom.POINT)
  manager = leg.getSymbolManager()
  pointSymbol = manager.createSymbol(geom.POINT)
  pointSymbol.setColor(Color.black)
  pointSymbol.setSize(0)
  leg.setDefaultSymbol(pointSymbol)
  basePoints.setLegend(leg)


  leg = SingleSymbolLegend()
  leg.setShapeType(geom.LINE)
  manager = leg.getSymbolManager()
  newline = manager.createSymbol(geom.LINE)
  newline.setColor(Color.black)
  leg.setDefaultSymbol(newline)
  baseLines.setLegend(leg)
  
  gvsig.currentView().addLayer(basePoints)
  gvsig.currentView().addLayer(baseLines)
  
