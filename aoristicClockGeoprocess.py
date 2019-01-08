# encoding: utf-8
from gvsig.uselib import use_plugin
use_plugin("org.gvsig.toolbox")
use_plugin("org.gvsig.geoprocess.app.mainplugin")

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
from org.gvsig.andami import PluginsLocator
import os
from java.io import File

class AoristicClockGeoprocess(ToolboxProcess):
  def getHelpFile(self):
    name = "aoristicclock"
    extension = ".xml"
    locale = PluginsLocator.getLocaleManager().getCurrentLocale()
    tag = locale.getLanguage()
    #extension = ".properties"

    helpPath = gvsig.getResource(__file__, "help", name + "_" + tag + extension)
    if os.path.exists(helpPath):
        return File(helpPath)
    #Alternatives
    alternatives = PluginsLocator.getLocaleManager().getLocaleAlternatives(locale)
    for alt in alternatives:
        helpPath = gvsig.getResource(__file__, "help", name + "_" + alt.toLanguageTag() + extension )
        if os.path.exists(helpPath):
            return File(helpPath)
    # More Alternatives
    helpPath = gvsig.getResource(__file__, "help", name + extension)
    if os.path.exists(helpPath):
        return File(helpPath)
    return None
    
  def defineCharacteristics(self):
    i18nManager = ToolsLocator.getI18nManager()
    self.setName(i18nManager.getTranslation("_Aoristic_clock_name"))
    self.setGroup(i18nManager.getTranslation("_Criminology_group"))
    self.setUserCanDefineAnalysisExtent(False)
    params = self.getParameters()

    params.addInputVectorLayer("LAYER",i18nManager.getTranslation("_Input_layer"), AdditionalInfoVectorLayer.SHAPE_TYPE_ANY, True)
    params.addNumericalValue("PROPORTION", i18nManager.getTranslation("_Proportion"),0, NUMERICAL_VALUE_DOUBLE)
    params.addTableField("FIELDHOUR", i18nManager.getTranslation("_Field_hour"), "LAYER", True)
    #params.addSelection("PATTERNHOUR", i18nManager.getTranslation("_Pattern_hour"),['%H:%M:%S'])
    #params.addString("PATTERNHOUR", i18nManager.getTranslation("_Pattern_hour"))
    params.addTableField("FIELDDAY", i18nManager.getTranslation("_Field_day"), "LAYER", True)
    #params.addSelection("PATTERNDAY", i18nManager.getTranslation("_Pattern_day"),['%Y-%m-%d'])
    #params.addString("PATTERNDAY", i18nManager.getTranslation("_Pattern_day"))
    params.addString("RANGEHOURS",i18nManager.getTranslation("_Range_hours"))
    params.addString("RANGEDAYS",i18nManager.getTranslation("_Range_days"))
    params.addTableFilter("FILTEREXPRESSION",i18nManager.getTranslation("_Filter_expression"),"LAYER", True)
    #params.addNumericalValue("INITIAL_X", i18nManager.getTranslation("_Initial_Point_X"),0, NUMERICAL_VALUE_DOUBLE)
    #params.addNumericalValue("INITIAL_Y", i18nManager.getTranslation("_Initial_Point_Y"),0, NUMERICAL_VALUE_DOUBLE)
    params.addPoint("INITIAL_POINT", i18nManager.getTranslation("_Initial_Point"))
    
  def processAlgorithm(self):
    features=None
    params = self.getParameters()
    sextantelayer = params.getParameterValueAsVectorLayer("LAYER")
    proportion = params.getParameterValueAsDouble("PROPORTION")
    nameFieldHour = params.getParameterValueAsString("FIELDHOUR")
    nameFieldDay =  params.getParameterValueAsString("FIELDDAY")
    
    #patternHour = params.getParameterValueAsString("PATTERNHOUR")
    #patternDay =  params.getParameterValueAsString("PATTERNDAY")
    
    rangeHoursParameter = params.getParameterValueAsString("RANGEHOURS")
    rangeDaysParameter = params.getParameterValueAsString("RANGEDAYS")
    expression = params.getParameterValueAsObject("FILTEREXPRESSION")

    point = params.getParameterValueAsObject("INITIAL_POINT")
    xi = point.getX()
    yi = point.getY()
    store = sextantelayer.getFeatureStore()

    aoristicClock(store,
                  nameFieldHour,
                  nameFieldDay,
                  rangeHoursParameter,
                  rangeDaysParameter,
                  expression,
                  xi,
                  yi,
                  proportion,
                  self)

    return True

def main(*args):
        process = AoristicClockGeoprocess()
        process.selfregister("Scripting")
        process.updateToolbox()