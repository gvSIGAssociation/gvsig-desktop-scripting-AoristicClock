# encoding: utf-8

import gvsig
import pdb
from gvsig import geom
from gvsig import commonsdialog
from gvsig.libs.toolbox import ToolboxProcess, NUMERICAL_VALUE_DOUBLE,SHAPE_TYPE_POLYGON,NUMERICAL_VALUE_INTEGER,SHAPE_TYPE_POLYGON, SHAPE_TYPE_POINT, SHAPE_TYPE_MIXED
from es.unex.sextante.gui import core
from es.unex.sextante.gui.core import NameAndIcon
from es.unex.sextante.additionalInfo import AdditionalInfoVectorLayer
from es.unex.sextante.gui.core import SextanteGUI
from org.gvsig.geoprocess.lib.api import GeoProcessLocator



from addons.AoristicClock.aoristicClock import aoristicClock

from org.gvsig.tools import ToolsLocator

class AoristicClockGeoprocess(ToolboxProcess):
  def defineCharacteristics(self):
    self.setName("_Aoristic_clock_name")
    self.setGroup("_Criminology_group")
    self.setUserCanDefineAnalysisExtent(False)
    params = self.getParameters()
    """
    nameFieldHour = "HORA"
    nameFieldDay = "DIA"
    patternHour = '%H:%M:%S'
    patternDay = '%Y-%m-%d'
    rangeHoursParameter = "0-10"
    rangeDaysParameter = "0,2,3-5"
    xi = 15
    yi = 0
    proportion = 1
    """
    i18nManager = ToolsLocator.getI18nManager()
    params.addInputVectorLayer("LAYER",i18nManager.getTranslation("_Input_layer"), AdditionalInfoVectorLayer.SHAPE_TYPE_ANY, True)
    params.addNumericalValue("PROPORTION", i18nManager.getTranslation("_Proportion"),0, NUMERICAL_VALUE_DOUBLE)
    params.addTableField("FIELDHOUR", i18nManager.getTranslation("_Field_hour"), "LAYER", True)
    params.addSelection("PATTERNHOUR", i18nManager.getTranslation("_Pattern_hour"),['%H:%M:%S'])
    
    params.addTableField("FIELDDAY", i18nManager.getTranslation("_Field_day"), "LAYER", True)
    params.addSelection("PATTERNDAY", i18nManager.getTranslation("_Pattern_day"),['%Y-%m-%d'])
    
    params.addString("RANGEHOURS",i18nManager.getTranslation("_Range_hours"))
    params.addString("RANGEDAYS",i18nManager.getTranslation("_Range_days"))
    
    params.addNumericalValue("INITIAL_X", i18nManager.getTranslation("_Initial_Point_X"),0, NUMERICAL_VALUE_DOUBLE)
    params.addNumericalValue("INITIAL_Y", i18nManager.getTranslation("_Initial_Point_Y"),0, NUMERICAL_VALUE_DOUBLE)
    
    
  def processAlgorithm(self):
    features=None
    params = self.getParameters()
    sextantelayer = params.getParameterValueAsVectorLayer("LAYER")
    proportion = params.getParameterValueAsDouble("PROPORTION")
    nameFieldHour = params.getParameterValueAsInt("FIELDHOUR")
    nameFieldDay =  params.getParameterValueAsInt("FIELDDAY")
    
    patternHour = params.getParameterValueAsString("PATTERNHOUR")
    patternDay =  params.getParameterValueAsString("PATTERNDAY")
    
    rangeHoursParameter = params.getParameterValueAsString("RANGEHOURS")
    rangeDaysParameter = params.getParameterValueAsString("RANGEDAYS")
    
    xi = params.getParameterValueAsDouble("INITIAL_X")
    yi = params.getParameterValueAsDouble("INITIAL_Y")
    store = sextantelayer.getFeatureStore()

    aoristicClock(store,
                  nameFieldHour,
                  nameFieldDay,
                  patternHour,
                  patternDay,
                  rangeHoursParameter,
                  rangeDaysParameter,
                  xi,
                  yi,
                  proportion,
                  self)
    print "Proceso terminado %s" % self.getCommandLineName()
    return True
        
def main(*args):
        process = AoristicClockGeoprocess()
        process.selfregister("Scripting")
        process.updateToolbox()