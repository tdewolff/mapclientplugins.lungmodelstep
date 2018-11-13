from PySide import QtGui, QtCore

from mapclientplugins.lungmodelstep.view.ui_lungmodelwidget import Ui_LungModelWidget


class LungModelWidget(QtGui.QWidget):

    def __init__(self, model, pcaModel, parent=None):
        super(LungModelWidget, self).__init__(parent)
        self._model = model
        self._meshModel = model.getMeshModel()

        self._ui = Ui_LungModelWidget()
        self._ui.setupUi(self)

        self._settings = {'view-parameters': {}}
        self._doneCallback = None

        self._ui.sceneviewer_widget.setContext(self._model.getContext())
        self._initialUiState()
        self._makeConnections()

    def _makeConnections(self):
        self._ui.sceneviewer_widget.graphicsInitialized.connect(self._graphicsInitialized)
        self._ui.done_pushButton.clicked.connect(self._doneClicked)
        self._ui.leftlung_checkBox.clicked.connect(self._leftLungClicked)
        self._ui.rightlung_checkBox.clicked.connect(self._rightLungClicked)

    def _doneClicked(self):
        self._doneCallback()

    def _initialUiState(self):
        self._ui.leftlung_checkBox.setChecked(True)
        self._ui.rightlung_checkBox.setChecked(True)

    def _graphicsInitialized(self):
        sceneViewer = self._ui.sceneviewer_widget.getSceneviewer()
        if sceneViewer is not None:
            sceneViewer.setLookatParametersNonSkew([1.9, -4.5, 2.0], [0.0, 0.0, 0.0], [0.0, 0.0, 1.0])
            sceneViewer.setTransparencyMode(sceneViewer.TRANSPARENCY_MODE_SLOW)
            self._viewAll()

    def setSettings(self, settings):
        self._settings.update(settings)

    def getSettings(self):
        eye, look_at, up, angle = self.__ui.sceneviewer_widget.getViewParameters()
        self._settings['view-parameters'] = {'eye': eye, 'look_at': look_at, 'up': up, 'angle': angle}
        return self._settings

    def registerDoneCallback(self, done_callback):
        self._doneCallback = done_callback

    def _leftLungClicked(self):
        # num = self._model._logger.getNumberOfMessages()
        # print num
        # for i in range(0, num):
        #     print self._model._logger.getMessageTextAtIndex(i)
        self._meshModel.setDisplaySurfaces('displaySurfacesLeft', self._ui.leftlung_checkBox.isChecked())

    def _rightLungClicked(self):
        self._meshModel.setDisplaySurfaces('displaySurfacesRight', self._ui.rightlung_checkBox.isChecked())

    def _viewAll(self):
        if self._ui.sceneviewer_widget.getSceneviewer() is not None:
            self._ui.sceneviewer_widget.viewAll()

