# encoding: utf-8

import gvsig

from org.gvsig.fmap.mapcontext import MapContextLocator
from org.gvsig.symbology.swing import SymbologySwingLocator
def main1(*args):
  newPoints = gvsig.currentLayer()
  leg = newPoints.getLegend()
  print leg.getSourceColorTable()
  
def main(*args):
  newPoints = gvsig.currentLayer()
  mp = MapContextLocator.getMapContextManager()
  leg = mp.createLegend("HeatmapLegend")
  leg.setUseFixedViz(True)
  h = newPoints.getFullEnvelope().getGeometry().getBounds2D().getHeight()
  w = newPoints.getFullEnvelope().getGeometry().getBounds2D().getWidth()
  if h>w:
    correction = h * 8
  else:
    correction = w * 8
  print correction
  
  leg.setCorrectionFixedViz(int(correction))
  leg.setDistance(30)
  colorTables = SymbologySwingLocator.getSwingManager().createColorTables().get(5)
  print colorTables
  leg.setColorTable(colorTables.getColors())
  newPoints.setLegend(leg)