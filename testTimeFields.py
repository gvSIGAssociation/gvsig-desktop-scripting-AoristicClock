# encoding: utf-8

import gvsig
from java.util import Date
from java.util import Calendar

def main(*args):
  layer = gvsig.currentLayer()
  store = layer.getFeatureStore()
  print store.getDefaultFeatureType()
  
def main1(*args):
  layer = gvsig.currentLayer()
  store = layer.getFeatureStore()
  fset = store.getFeatureSelection() #.getFeatureSet()
  cal = Calendar.getInstance()
  print "First day: ", cal.getFirstDayOfWeek()
  print Calendar.MONDAY, Calendar.SUNDAY, Calendar.SATURDAY
  cal.setFirstDayOfWeek(Calendar.MONDAY)
  print "First day: ", cal.getFirstDayOfWeek()
  for feature in fset:
    field = feature.get(0)
    print type(field), field
    
    cal.setTime(field)
    print type(cal)
    value = cal.get(Calendar.DAY_OF_WEEK)
    print value