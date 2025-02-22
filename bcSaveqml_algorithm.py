# -*- coding: utf-8 -*-
"""
/***************************************************************************
 bcSaveqml3
                           A QGIS Processing algorithm
                     Save a qml file for each selected layer

 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-05-19
        copyright            : (C) 2019-2023 by GeoProc.com
        email                : info@geoproc.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
Icon modified from Freepik on www.flaticon.com.
WARNING: code formatting does not follow pycodestyle recommendations
"""

__author__ = 'GeoProc.com'
__date__ = '2019-05-19'
__copyright__ = '(C) 2019-2023 by GeoProc.com'
__revision__ = '$Format:%H$'

import os
import codecs
import uuid
from qgis.PyQt.QtGui import QIcon
from qgis.core import (QgsProcessingUtils, QgsProcessing)
from processing.algs.qgis.QgisAlgorithm import QgisAlgorithm

from .setparams import set_param
from .HelpbcA import help_bcSaveqml
from .QgsBcUtils import save_qml

is_dependencies_satisfied = True

#-----------------------------------------------------------------------------------------
rlayers = QgsProcessing.TypeRaster
vlayers = QgsProcessing.TypeVectorAnyGeometry
plugin_path = os.path.dirname(__file__)

the_url = 'http://www.geoproc.com/free/bcSaveqml3.htm'
help_string = help_bcSaveqml
the_tags = ['qml','save','bulk','layer','style']
#-----------------------------------------------------------------------------------------

class bcSaveqmlAlgorithm(QgisAlgorithm):
    ''' Processing wrapper for the save qml algorithm. '''
    #
    # Parameters used
    THE_VLAYERS = 'THE_VLAYERS'
    THE_RLAYERS = 'THE_RLAYERS'
    OUTPUT      = 'OUTPUT'

    _default_output = 'result.htm'
    _ico = 'bcSaveqml'
    _the_strings = {"ALGONAME":"Save .qml",
                    "ERR":"ERROR",
                    "ERRSAVE":"ERROR: Cannot save qml for layer: ",
                    "WARN":"WARNING: No layer selected!",
                    "Q1":"A .qml file has been created for 1 selected vector layer.",
                    "Q2":"A .qml file has been created for 1 selected raster layer.",
                    "EXT1":".qml files have been created for %d selected vector layers.",
                    "EXT2":".qml files have been created for %d selected raster layers."}
    _pstr = ['Input QGIS vector layers',
             'Input QGIS raster layers',
            'Result file',
            'HTML files (*.html)']

    def __init__(self):
        super().__init__()
    #-------------------------------------------------------------------------------------

    def _define_params(self):
        ''' Define parameters needed. '''
        #
        #       [0] < 100  : "normal" parameter
        # 100 < [0] < 1000 : Advanced Parameter
        #       [0] > 1000 : Output parameter
        self.the_params = {
           self.THE_VLAYERS: [1,self._pstr[0],'MultipleLayers',{'layerType':vlayers}
                             ,True],
           self.THE_RLAYERS: [2,self._pstr[1],'MultipleLayers',{'layerType':rlayers}
                             ,True],
           self.OUTPUT:     [1001,self._pstr[2],'FileDestination',
                             {'FILTER':self._pstr[3],'defaultValue':self._default_output},
                             True]
        }
    #-------------------------------------------------------------------------------------

    def _create_HTML(self, outputFile, iv, ir):
        ''' Generate an output html file to show results. '''
        #
        with codecs.open(outputFile, 'w', encoding='utf-8') as f:
            f.write('<html>\n<head>\n')
            f.write('<meta http-equiv="Content-Type" content="text/html;') 
            f.write(' charset=utf-8" />\n</head>\n<body>\n')
            if self._error != '':
                f.write('<h1>%s</h1>\n' % self.tr(self._the_strings["ERR"]))
                f.write('<p style="color:red;">%s</p>\n' % self.tr(self._error))
            #
            elif iv == -1 and ir == -1:
                f.write('<h3>%s</h3>\n' % self.tr(self._the_strings["WARN"]))
            #
            else:
                if iv == 0:
                    vres = self._the_strings["Q1"]
                else:
                    vres = self._the_strings["EXT1"] % (iv + 1)
                if ir == 0:
                    rres = self._the_strings["Q2"]
                else:
                    rres = self._the_strings["EXT2"] % (ir + 1)
                #
                f.write('<h3>%s</h3>\n' % self.tr(vres))
                f.write('<h3>%s</h3>\n' % self.tr(rres))
            f.write('</body>\n</html>\n')
        #
        return outputFile
    #-------------------------------------------------------------------------------------

    def initAlgorithm(self, config):
        ''' Here we define the inputs and output of the algorithm. '''
        #
        self._define_params()
        for param in sorted(self.the_params, key=self.the_params.__getitem__):
            b = self.the_params[param][0]
            qparam = set_param(param, self.the_params)
            if qparam != None:
                if b < 100:
                    self.addParameter(qparam)
                elif b < 1000:
                    self.addParameter((qparam))
                else:
                    self.addParameter(qparam, True)

        # Other variables
        self._error = ''
        self.tmpDir = QgsProcessingUtils.tempFolder()
    #-------------------------------------------------------------------------------------

    def processAlgorithm(self, parameters, context, feedback):
        ''' Here is where the processing itself takes place. '''
        #
        tmpf = str(uuid.uuid4())
        res_file = os.path.join(self.tmpDir, tmpf + '.htm')
        self._error = ''

        the_vlayers = self.parameterAsLayerList(parameters, self.THE_VLAYERS, context)
        the_rlayers = self.parameterAsLayerList(parameters, self.THE_RLAYERS, context)
        output_file = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        if (self._default_output in output_file) or (output_file == ''):
            output_file = res_file
        else:
            output_file = os.path.splitext(output_file)[0] + '.htm'
        feedback.setProgress(10.)

        i = -1
        total = 35. / len(the_vlayers) if len(the_vlayers) > 0 else 0.
        for i, layer in enumerate(the_vlayers):
            if feedback.isCanceled():
                break
            feedback.setProgress(int(i * total) + 10.)
            #
            bOk = save_qml(layer, True)
            if not bOk:
                self._error += self._the_strings["ERRSAVE"] + layer.name() + '<br/>\n'

        j = -1
        total = 35. / len(the_rlayers) if len(the_rlayers) > 0 else 0.
        for j, layer in enumerate(the_rlayers):
            if feedback.isCanceled():
                break
            feedback.setProgress(int(i * total) + 45.)
            #
            bOk = save_qml(layer, True)
            if not bOk:
                self._error += self._the_strings["ERRSAVE"] + layer.name() + '<br/>\n'

        feedback.setProgress(90.)
        fil = self._create_HTML(output_file, i, j)
        feedback.setProgress(100.)
        #
        return {self.OUTPUT:fil}
    #-------------------------------------------------------------------------------------

    def get_error(self):
        ''' Return the error value. '''
        #
        return self.tr(self._error)
    #-------------------------------------------------------------------------------------

    def icon(self):
        ''' Returns a QIcon for the algorithm. '''
        #
        return QIcon(os.path.join(os.path.join(plugin_path, 'res', self._ico+'.svg')))
    #-------------------------------------------------------------------------------------

    def svgIconPath(self):
        ''' Returns a path to an SVG version of the algorithm's icon. '''
        #
        return QIcon(os.path.join(os.path.join(plugin_path, 'res', self._ico+'.svg')))
    #-------------------------------------------------------------------------------------

    def helpUrl(self):
        ''' Returns a url pointing to the algorithm's help page. '''
        #
        return the_url
    #-------------------------------------------------------------------------------------

    def shortHelpString(self):
        ''' Returns a localised short helper string for the algorithm. '''
        #
        return self.tr(help_string)
    #-------------------------------------------------------------------------------------

    def name(self):
        '''
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        '''
        return 'bcSaveqml3'
    #-------------------------------------------------------------------------------------

    def displayName(self):
        '''
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        '''
        return self.tr(self._the_strings["ALGONAME"])
    #-------------------------------------------------------------------------------------

    def tags(self):
        return self.tr(the_tags)
    #-------------------------------------------------------------------------------------

    def group(self):
        '''
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        '''
        return str(self.groupId()).capitalize()
    #-------------------------------------------------------------------------------------

    def groupId(self):
        '''
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        '''
        return 'layers'
    #-------------------------------------------------------------------------------------

    def tr(self, string):
        ''' No translation of strings. '''
        #
        return string
    #-------------------------------------------------------------------------------------

    def createInstance(self):
        ''' Creates a new instance of the algorithm class. '''
        #
        return bcSaveqmlAlgorithm()
    #-------------------------------------------------------------------------------------