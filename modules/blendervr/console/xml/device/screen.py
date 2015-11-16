## Copyright (C) LIMSI-CNRS (2014)
##
## contributor(s) : Jorge Gascon, Damien Touraine, David Poirier-Quinot,
## Laurent Pointal, Julian Adenauer, 
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

from . import base

class Screen(base.Base):

    def __init__(self, parent, name, attrs, define_corners):
        super(Screen, self).__init__(parent, name, attrs)

        self._corners        = None
        self._corner_name    = None
        self._define_corners = define_corners

        if define_corners:
            self._attribute_list += ['corners']

        self._name = name

    def _getChildren(self, name, attrs):
        if name == 'corner':
            if not self._define_corners:
                self.raise_error('Screen type \"{0}\" takes no corner element !'.format(self._name))

            if self._corner_name is not None:
                self.raise_error('Cannot import corner inside corner !')

            if 'name' not in attrs: 
                self.raise_error("A corner must have a name attribute : 'topRightCorner', 'topLeftCorner' or 'bottomRightCorner' !")
            self._corner_name = attrs['name']

            if self._corner_name not in ['topRightCorner', 'topLeftCorner', 'bottomRightCorner']:
                self.raise_error("Corner name must be 'topRightCorner', 'topLeftCorner' or 'bottomRightCorner' !")
            return None
        return super(Screen, self)._getChildren(name, attrs)

    def characters(self, string):
        if self._corner_name is not None:
            if self._corners is None:
                self._corners = {}
            self._corners[self._corner_name] = self.getVector(string, 3, 0.0)
            self._corner_name = None

    def endElement(self, name):
        if self._corner_name:
            self._corner_name = False
            return
        super(Screen, self).endElement(name)
