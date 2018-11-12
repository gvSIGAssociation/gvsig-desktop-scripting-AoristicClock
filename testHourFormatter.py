# encoding: utf-8

import gvsig
from java.util import Date
from java.util import Calendar
from java.text import SimpleDateFormat

def main(*args):
  layer = gvsig.currentLayer()
  store = layer.getFeatureStore()
  fset = store.getFeatureSet()
  for feature in fset:
    field = feature.get("HORA")
    pattern = "HH:mm:ss"
    #field = "23:10:10"
    formatter = SimpleDateFormat(pattern)
    newDate = formatter.parse(field)
    
    cal = Calendar.getInstance()
    cal.setTime(newDate)
    hour = cal.get(Calendar.HOUR_OF_DAY)
    print hour