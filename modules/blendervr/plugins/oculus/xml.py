# -*- coding: utf-8 -*-
# file: blendervr/plugins/oculus/xml.py

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

import os
from .. import xml

class XML(xml.XML):

    def __init__(self, parent, name, attrs):
        super(XML, self).__init__(parent, name, attrs)
        self._class_list += ['users']
        self._users = None

        if 'users' in attrs:
            self._users = attrs['users']
        else:
            self._users = None

    def _getChildren(self, name, attrs):
        if name == 'user':
            user = User(self, name, attrs)
            if self._users is None:
                self._users = [user]
            else:
                self._users.append(user)
            return user

        return super(XML, self)._getChildren(name, attrs)


class User(xml.mono):
    def __init__(self, parent, name, attrs):
        super(User, self).__init__(parent, name, attrs)
        self._attribute_list += ['viewer', 'processor_method', 'computer', 'backend']

        if 'viewer' not in attrs or \
           'computer' not in attrs:
            self.raise_error('Oculus User must have a viewer and a computer (and optionally a processor_method)!')

        self._viewer = attrs.get('viewer')
        self._computer = attrs.get('computer')
        self._processor_method = attrs.get('processor_method', 'user_position')
        self._backend = attrs.get('backend', 'oculus_latest')

        if self._backend not in {'oculus_latest','oculus_legacy'}:
            self.raise_error('Oculus User backend \"{0}\" not in {\"oculus_latest\", \"oculus_legacy\"}'.format(self._backend))
