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



from addons.AoristicClockGrid.aoristicClockGrid import aoristicClockGrid

from org.gvsig.tools import ToolsLocator

class AoristicClockGridGeoprocess(ToolboxProcess):
  def defineCharacteristics(self):
    self.setName("_Aoristic_clock_grid_name")
    self.setGroup("_Criminology_group")
    self.setUserCanDefineAnalysisExtent(False)
    params = self.getParameters()
    i18nManager = ToolsLocator.getI18nManager()
    params.addInputVectorLayer("LAYER",i18nManager.getTranslation("_Input_layer"), AdditionalInfoVectorLayer.SHAPE_TYPE_ANY, True)
    params.addNumericalValue("PROPORTIONX", i18nManager.getTranslation("_Proportion_X"),0, NUMERICAL_VALUE_DOUBLE)
    params.addNumericalValue("PROPORTIONY", i18nManager.getTranslation("_Proportion_Y"),0, NUMERICAL_VALUE_DOUBLE)
    params.addTableField("FIELDHOUR", i18nManager.getTranslation("_Field_hour"), "LAYER", True)
    params.addSelection("PATTERNHOUR", i18nManager.getTranslation("_Pattern_hour"),['%H:%M:%S'])
    
    params.addTableField("FIELDDAY", i18nManager.getTranslation("_Field_day"), "LAYER", True)
    params.addSelection("PATTERNDAY", i18nManager.getTranslation("_Pattern_day"),['%Y-%m-%d'])
    
  def processAlgorithm(self):
        features=None
        params = self.getParameters()
        sextantelayer = params.getParameterValueAsVectorLayer("LAYER")
        proportionX = params.getParameterValueAsDouble("PROPORTIONX")
        proportionY = params.getParameterValueAsDouble("PROPORTIONY")
        
        nameFieldHour = params.getParameterValueAsInt("FIELDHOUR")
        nameFieldDay =  params.getParameterValueAsInt("FIELDDAY")
        
        patternHour = params.getParameterValueAsString("PATTERNHOUR")
        patternDay =  params.getParameterValueAsString("PATTERNDAY")
        
        store = sextantelayer.getFeatureStore()

        aoristicClockGrid(store,
                      proportionX,
                      proportionY,
                      nameFieldHour,
                      nameFieldDay,
                      patternHour,
                      patternDay,
                      0,
                      0,
                      self)
        print "Proceso terminado %s" % self.getCommandLineName()
        return True
        
def main(*args):
        process = AoristicClockGridGeoprocess()
        process.selfregister("Scripting")
        process.updateToolbox()