# -*- coding: utf-8 -*-
# file: blendervr/plugins/oculus/virtual_environment/__init__.py

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

from .. import base
from . import user

from mathutils import Matrix, Quaternion

VERBOSE = True

class Oculus(base.Base):
    def __init__(self, parent, configuration):
        super(Oculus, self).__init__(parent)

        self._user = None
        self._hmd = None

        self.checkLibraryPath()

        try:
            import bridge

        except ImportError:
            self.logger.info('Oculus plugin error: no \"hmd_bridge_sdk\" module available. Make sure you have the project submodules. Please refer to the BlenderVR documentation')
            self._available = False
            return

        except Exception as err:
            self.logger.error(err)
            self._available = False
            return

        if 'users' in configuration:
            for user_entry in configuration['users']:
                try:
                    _user = user.User(self, user_entry)
                    if _user.isAvailable():
                        viewer = _user.getUser()
                        if viewer is not None:
                            self._user = _user
                            # each computer can only have one user/viewer
                            break
                except:
                    self.logger.log_traceback(False)

        self._backend = self._user.getBackend()
        self._available = True

    def start(self):
        super(Oculus, self).start()

        try:
            self.checkOculus()

        except Exception:
            self._available = False

    def run(self):
        pass

    def checkMethods(self):
        if not self._available:
            self.logger.info('Oculus python module not available !')
            return False

        if not self._user:
            self.logger.info('Oculus python module not available ! No valid user found for this computer.')
            return False

        if not self._user.checkMethod(True):
            self.logger.info('No Oculus processor method available !')
            del self._user
            self._user = None
            return False

        return True

    def checkLibraryPath(self):
        """if library exists append it to sys.path"""
        import sys
        import os
        from .... import tools

        libs_path = tools.getLibsPath()
        oculus_path = os.path.join(libs_path, "hmd_sdk_bridge")

        if oculus_path not in sys.path:
            sys.path.append(oculus_path)

    def _getHMDClass(self):
        backend = self._user.getBackend()

        if backend == 'oculus_latest':
            return BridgeOculus

        elif backend == 'oculus_legacy':
            return BridgeOculusLegacy

        else:
            self.logger.error('Oculus backend \"{0}\" not supported'.format(backend))
            return None

    def checkOculus(self):
        """
        check if Oculus is connected
        """
        # TODO check is oculus is connected
        return True

    def startOculus(self):
        from bge import logic

        try:
            scene = logic.getCurrentScene()

            self._hmd = self._getHMDClass()(scene, self.logger.error)

            if not self._hmd.init():
                self.logger.error("Error initializing device")
                return False

            # get the data from device
            color_texture = [0, 0]
            for i in range(2):
                self._hmd.setEye(i)
                color_texture[i] = self._hmd.color_texture

        except Exception as E:
            self.logger.log_traceback(E)
            self._hmd = None
            return False

        else:
            return True

    def loopOculus(self):
        from bge import texture
        from bge import logic

        self._hmd.loop()

        scene = logic.getCurrentScene()
        camera = scene.active_camera

        for i in range(2):
            self._hmd.setEye(i)

            offscreen = self._hmd.offscreen
            projection_matrix = self._hmd.projection_matrix
            modelview_matrix = self._hmd.modelview_matrix

            self._setMatrices(camera, projection_matrix, modelview_matrix)

            # drawing
            ir = texture.ImageRender(scene, camera, offscreen)
            ir.render()
            ir.refresh()

        self._hmd.frameReady()

    def _setMatrices(self, camera, projection_matrix, modelview_matrix):
        camera.projection_matrix = projection_matrix

        modelview_matrix.invert()
        camera.worldPosition = modelview_matrix.translation
        camera.worldOrientation = modelview_matrix.to_quaternion()


# #####################################
# HMD BRIDGE SDK
# github.com/dfelinto/hmd_sdk_bridge
# #####################################

class HMD_Base:
    __slots__ = {
        "_name",
        "_current_eye",
        "_error_callback",
        "_width",
        "_height",
        "_projection_matrix",
        "_head_transformation",
        "_is_direct_mode",
        "_eye_pose",
        "_offscreen",
        "_color_texture",
        "_modelview_matrix",
        "_near",
        "_far",
        }

    def __init__(self, name, is_direct_mode, context, error_callback):
        self._name = name
        self._is_direct_mode = is_direct_mode
        self._error_callback = error_callback
        self._current_eye = 0
        self._width = [0, 0]
        self._height = [0, 0]
        self._projection_matrix = [Matrix.Identity(4), Matrix.Identity(4)]
        self._modelview_matrix = [Matrix.Identity(4), Matrix.Identity(4)]
        self._color_texture = [0, 0]
        self._offscreen = [None, None]
        self._eye_orientation_raw = [[1.0, 0.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0]]
        self._eye_position_raw = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
        self._scale = self._calculateScale()

        self._updateViewClipping()

    @property
    def is_direct_mode(self):
        return self._is_direct_mode

    @property
    def width(self):
        return self._width[self._current_eye]

    @width.setter
    def width(self, value):
        self._width[self._current_eye] = value

    @property
    def height(self):
        return self._height[self._current_eye]

    @height.setter
    def height(self, value):
        self._height[self._current_eye] = value

    @property
    def offscreen(self):
        return self._offscreen[self._current_eye]

    @property
    def color_texture(self):
        return self._color_texture[self._current_eye]

    @property
    def projection_matrix(self):
        return self._projection_matrix[self._current_eye]

    @property
    def modelview_matrix(self):
        return self._modelview_matrix[self._current_eye]

    def setEye(self, eye):
        self._current_eye = int(bool(eye))

    def init(self):
        """
        Initialize device

        :return: return True if the device was properly initialized
        :rtype: bool
        """
        from bge import render

        try:
            for i in range(2):
                self._offscreen[i] = render.offScreenCreate(self._width[i], self._height[i], 0, render.RAS_OFS_RENDER_TEXTURE)
                self._color_texture[i] = self._offscreen[i].color

        except Exception as E:
            self.error('init', E, True)
            self._offscreen[0] = None
            self._offscreen[1] = None
            return False

        else:
            return True

    def loop(self):
        """
        Get fresh tracking data
        """
        self._updateViewClipping()
        self.updateMatrices()

    def frameReady(self):
        """
        The frame is ready to be sent to the device
        """
        assert False, "frameReady() not implemented for the \"{0}\" device".format(self._name)

    def reCenter(self):
        """
        Re-center the HMD device

        :return: return True if success
        :rtype: bool
        """
        assert False, "reCenter() not implemented for the \"{0}\" device".format(self._name)

    def quit(self):
        """
        Garbage collection
        """
        try:
            for i in range(2):
                self._offscreen[i] = None

        except Exception as E:
            print(E)

    def error(self, function, exception, is_fatal):
        """
        Handle error messages
        """
        if VERBOSE:
            print("ADD-ON :: {0}() : {1}".format(function, exception))
            import sys
            traceback = sys.exc_info()

            if traceback and traceback[0]:
                print(traceback[0])

        if hasattr(exception, "strerror"):
            message = exception.strerror
        else:
            message = str(exception)

        # send the error the interface
        self._error_callback(message, is_fatal)

    def updateMatrices(self):
        """
        Update OpenGL drawing matrices
        """
        view_matrix = self._getViewMatrix()

        for i in range(2):
            rotation_raw = self._eye_orientation_raw[i]
            rotation = Quaternion(rotation_raw).to_matrix().to_4x4()

            position_raw = self._eye_position_raw[i]

            # take scene units into consideration
            position_raw = self._scaleMovement(position_raw)
            position = Matrix.Translation(position_raw)

            transformation = position * rotation

            self._modelview_matrix[i] = transformation.inverted() * view_matrix

    def _getViewMatrix(self):
        from bge import logic

        scene = logic.getCurrentScene()
        camera = scene.active_camera

        return camera.worldTransform.inverted()

    def _updateViewClipping(self):
        from bge import logic

        scene = logic.getCurrentScene()
        camera = scene.active_camera

        self._near = camera.near
        self._far = camera.far

    def _calculateScale(self):
        """
        if BU != 1 meter, scale the transformations
        """
        # Scene unit system not supported in the BGE
        return None

    def _scaleMovement(self, position):
        """
        if BU != 1 meter, scale the transformations
        """
        if self._scale is None:
            return position

        return [position[0] * self._scale,
                position[1] * self._scale,
                position[2] * self._scale]

    def _convertMatrixTo4x4(self, value):
        matrix = Matrix()

        matrix[0] = value[0:4]
        matrix[1] = value[4:8]
        matrix[2] = value[8:12]
        matrix[3] = value[12:16]

        return matrix.transposed()


class BridgeOculus(HMD_Base):
    def __init__(self, context, error_callback):
        super(BridgeOculus, self).__init__('Oculus', True, context, error_callback)

    def _getHMDClass(self):
        from bridge.hmd.oculus import HMD
        return HMD

    @property
    def projection_matrix(self):
        if self._current_eye:
            matrix = self._hmd.getProjectionMatrixRight(self._near, self._far)
        else:
            matrix = self._hmd.getProjectionMatrixLeft(self._near, self._far)

        self.projection_matrix = matrix
        return super(BridgeOculus, self).projection_matrix

    @projection_matrix.setter
    def projection_matrix(self, value):
        self._projection_matrix[self._current_eye] = \
                self._convertMatrixTo4x4(value)

    def init(self):
        """
        Initialize device

        :return: return True if the device was properly initialized
        :rtype: bool
        """
        try:
            HMD = self._getHMDClass()
            self._hmd = HMD()

            # gather arguments from HMD

            self.setEye(0)
            self.width = self._hmd.width_left
            self.height = self._hmd.height_left

            self.setEye(1)
            self.width = self._hmd.width_right
            self.height = self._hmd.height_right

            # initialize FBO
            if not super(BridgeOculus, self).init():
                raise Exception("Failed to initialize HMD")

            # send it back to HMD
            if not self._setup():
                raise Exception("Failed to setup BridgeOculus")

        except Exception as E:
            self.error('init', E, True)
            self._hmd = None
            return False

        else:
            return True

    def _setup(self):
        return self._hmd.setup(self._color_texture[0], self._color_texture[1])

    def loop(self):
        """
        Get fresh tracking data
        """
        try:
            data = self._hmd.update()

            self._eye_orientation_raw[0] = data[0]
            self._eye_orientation_raw[1] = data[2]
            self._eye_position_raw[0] = data[1]
            self._eye_position_raw[1] = data[3]

            # update matrices
            super(BridgeOculus, self).loop()

        except Exception as E:
            self.error("loop", E, False)
            return False

        return True

    def frameReady(self):
        """
        The frame is ready to be sent to the device
        """
        try:
            self._hmd.frameReady()

        except Exception as E:
            self.error("frameReady", E, False)
            return False

        return True

    def reCenter(self):
        """
        Re-center the HMD device

        :return: return True if success
        :rtype: bool
        """
        return self._hmd.reCenter()

    def quit(self):
        """
        Garbage collection
        """
        self._hmd = None
        return super(BridgeOculus, self).quit()


class BridgeOculusLegacy(BridgeOculus):
    def __init__(self, context, error_callback):
        HMD_Base.__init__(self, 'BridgeOculus Legacy', False, context, error_callback)

    def _getHMDClass(self):
        from bridge.hmd.oculus_legacy import HMD
        return HMD
