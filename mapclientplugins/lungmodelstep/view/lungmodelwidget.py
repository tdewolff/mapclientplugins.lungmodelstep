from PySide import QtGui, QtCore

from opencmiss.zinc.context import Context

from mapclientplugins.lungmodelstep.view.ui_lungmodelwidget import Ui_LungModelWidget


class LungModelWidget(QtGui.QWidget):

    def __init__(self, parent=None):
        super(LungModelWidget, self).__init__(parent)

        self._context = Context("ZincViewGraphics")
        self._context.getMaterialmodule().defineStandardMaterials()
        self._context.getGlyphmodule().defineStandardGlyphs()

        self._ui = Ui_LungModelWidget()
        self._ui.setupUi(self)

        self._settings = {'view-parameters': {}}
        self._done_callback = None

        self._make_connections()

        self._ui.sceneviewer_widget.get_context(self._context)
        self._ui.sceneviewer_widget.graphics_initialized.connect(self._graphics_initialized())

    def _make_connections(self):
        self._ui.sceneviewer_widget.graphics_initialized.connect(self._graphics_initialized)
        self._ui.done_pushButton.clicked.connect(self._done_clicked)
        self._ui.leftlung_checkBox.clicked.connect(self._left_lung_clicked)
        self._ui.rightlung_checkBox.clicked.connect(self._right_lung_clicked)

    def _done_clicked(self):
        self._done_callback()

    def _graphics_initialized(self):
        """
        Callback for when SceneviewerWidget is initialised
        Set custom scene from model
        """
        scene_viewer = self._ui.sceneviewer_widget.get_zinc_sceneviewer()
        if scene_viewer is not None:
            scene = self._model.get_scene()
            self._ui.sceneviewer_widget.set_tumble_rate(0)
            self._ui.sceneviewer_widget.set_scene(scene)
            if len(self._settings['view-parameters']) == 0:
                self._view_all()
            else:
                eye = self._settings['view-parameters']['eye']
                look_at = self._settings['view-parameters']['look_at']
                up = self._settings['view-parameters']['up']
                angle = self._settings['view-parameters']['angle']
                self._ui.sceneviewer_widget.set_view_parameters(eye, look_at, up, angle)

    def set_settings(self, settings):
        self._settings.update(settings)

    def get_settings(self):
        eye, look_at, up, angle = self._ui.sceneviewer_widget.get_view_parameters()
        self._settings['view-parameters'] = {'eye': eye, 'look_at': look_at, 'up': up, 'angle': angle}
        return self._settings

    def register_done_callback(self, done_callback):
        self._done_callback = done_callback

    def _left_lung_clicked(self):
        pass

    def _right_lung_clicked(self):
        pass

