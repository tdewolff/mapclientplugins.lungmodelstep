from PySide import QtGui, QtCore

from mapclientplugins.lungmodelstep.view.ui_lungmodelwidget import Ui_LungModelWidget


class LungModelWidget(QtGui.QWidget):

    def __init__(self, model, parent=None):
        super(LungModelWidget, self).__init__(parent)
        self._model = model

        self._ui = Ui_LungModelWidget()
        self._ui.setupUi(self)

        self._settings = {'view-parameters': {}}
        self._done_callback = None

        self._ui.sceneviewer_widget.setContext(self._model.get_context())
        self._initial_ui_state()
        self._make_connections()

    def _make_connections(self):
        self._ui.sceneviewer_widget.graphicsInitialized.connect(self._graphics_initialized)
        self._ui.done_pushButton.clicked.connect(self._done_clicked)
        self._ui.leftlung_checkBox.clicked.connect(self._left_lung_clicked)
        self._ui.rightlung_checkBox.clicked.connect(self._right_lung_clicked)

    def _done_clicked(self):
        self._done_callback()

    def _initial_ui_state(self):
        self._ui.leftlung_checkBox.setChecked(True)
        self._ui.rightlung_checkBox.setChecked(True)

    def _graphics_initialized(self):
        """
        Callback for when sceneviewer_widget is initialised
        Set custom scene from model
        """
        scene_viewer = self._ui.sceneviewer_widget.getSceneviewer()
        if scene_viewer is not None:
            scene_viewer.setLookatParametersNonSkew([1.9, -4.5, 2.0], [0.0, 0.0, 0.0], [0.0, 0.0, 1.0])
            scene_viewer.setTransparencyMode(scene_viewer.TRANSPARENCY_MODE_SLOW)
            self._view_all()

    def set_settings(self, settings):
        self._settings.update(settings)

    def get_settings(self):
        eye, look_at, up, angle = self.__ui.sceneviewer_widget.getViewParameters()
        self._settings['view-parameters'] = {'eye': eye, 'look_at': look_at, 'up': up, 'angle': angle}
        return self._settings

    def register_done_callback(self, done_callback):
        self._done_callback = done_callback

    def _left_lung_clicked(self):
        # num = self._model._logger.getNumberOfMessages()
        # print num
        # for i in range(0, num):
        #     print self._model._logger.getMessageTextAtIndex(i)
        if self._ui.leftlung_checkBox.isChecked():
            print("left clicked")
        else:
            pass

    def _right_lung_clicked(self):
        pass

    def _view_all(self):
        if self._ui.sceneviewer_widget.getSceneviewer() is not None:
            self._ui.sceneviewer_widget.viewAll()
