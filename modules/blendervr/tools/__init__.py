# -*- coding: utf-8 -*-
# file: blendervr/tools/__init__.py

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


def getModulePath():
    """The path of the current module"""
    import inspect
    stack = inspect.stack()
    module_file = stack[1][1]

    import os
    path = os.path.dirname(module_file)
    if os.path.basename(path) == '__pycache__':
        return os.path.dirname(path)
    return path


def getRootPath():
    """The root path of the project"""
    import os
    # hardcoded: returns the folder 3 levels up from this (//modules/blendervr/tools)
    return os.path.dirname(os.path.dirname(os.path.dirname(getModulePath())))


def getLibsPath():
    """The path for the external libs"""
    import os
    root_path = getRootPath()
    return os.path.join(root_path, "libs")
