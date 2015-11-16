# -*- coding: utf-8 -*-
# file: blendervr/plugins/oculus/__init__.py

## Copyright (C) LIMSI-CNRS (2015)
##
## This software is a computer program whose purpose is to distribute
## blender to render on Virtual Reality device systems.
##
## This software is governed by the CeCILL  license under French law and
## abiding by the rules of distribution of free software.  You can  use,
## modify and/ or redistribute the software under the terms of the CeCILL
## license as circulated by CEA, CNRS and INRIA at the following URL
## "http://www.cecill.info".
##
## As a counterpart to the access to the source code and  rights to copy,
## modify and redistribute granted by the license, users are provided only
## with a limited warranty  and the software's author,  the holder of the
## economic rights,  and the successive licensors  have only  limited
## liability.
##
## In this respect, the user's attention is drawn to the risks associated
## with loading,  using,  modifying and/or developing or reproducing the
## software by the user in light of its specific status of free software,
## that may mean  that it is complicated to manipulate,  and  that  also
## therefore means  that it is reserved for developers  and  experienced
## professionals having in-depth computer knowledge. Users are therefore
## encouraged to load and test the software's suitability as regards their
## requirements in conditions enabling the security of their systems and/or
## data to be ensured and,  more generally, to use and operate it in the
## same conditions as regards security.
##
## The fact that you are presently reading this means that you have had
## knowledge of the CeCILL license and that you accept its terms.
##

"""
Oculus Plugin
*******************

This script instantiates the Oculus plugin
"""

from .. import *
from .. import exceptions

if base.is_virtual_environment():
    class Base(base.Base):
        def __init__(self, parent):
            base.Base.__init__(self, parent)

        def setConfiguration(self, configuration):
            from . import virtual_environment
            self._main = virtual_environment.Oculus(self, configuration)

        def start(self):
            if not hasattr(self, '_main') or not self._main.checkMethods():
                raise exceptions.PluginError()
            self.setupMain(False)

elif base.is_console():
    class Base(base.Base):
        def __init__(self, parent):
            base.Base.__init__(self, parent)

        def getXMLParserClass(self):
            from . import xml
            return xml.XML
