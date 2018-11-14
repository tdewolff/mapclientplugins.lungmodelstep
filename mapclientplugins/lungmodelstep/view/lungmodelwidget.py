from PySide import QtGui, QtCore
import numpy as np

from mapclientplugins.lungmodelstep.view.ui_lungmodelwidget import Ui_LungModelWidget


class LungModelWidget(QtGui.QWidget):

    def __init__(self, model, pcaModelData, parent=None):
        super(LungModelWidget, self).__init__(parent)
        self._meshModel = model.getMeshModel()
        self._pcaModel = pcaModelData
        self._modeDict = {
            'modeOne': 0.0,
            'modeTwo': 0.0,
            'modeThree': 0.0,
            'modeFour': 0.0,
            'modeFive': 0.0,
        }

        self._ui = Ui_LungModelWidget()
        self._ui.setupUi(self)

        self._settings = {'view-parameters': {}}
        self._doneCallback = None

        self._ui.sceneviewer_widget.setContext(model.getContext())
        self._initialUiState()
        self._makeConnections()

    def _makeConnections(self):
        self._ui.sceneviewer_widget.graphicsInitialized.connect(self._graphicsInitialized)
        self._ui.done_pushButton.clicked.connect(self._doneClicked)
        self._ui.leftlung_checkBox.clicked.connect(self._leftLungClicked)
        self._ui.rightlung_checkBox.clicked.connect(self._rightLungClicked)
        self._ui.reset_pushButton.clicked.connect(self._resetClicked)
        self._ui.morph_pushButton.clicked.connect(self._morphItClicked)
        self._ui.doubleSpinBox.valueChanged.connect(self._modeOneChanged)
        self._ui.doubleSpinBox_2.valueChanged.connect(self._modeTwoChanged)
        self._ui.doubleSpinBox_3.valueChanged.connect(self._modeThreeChanged)
        self._ui.doubleSpinBox_4.valueChanged.connect(self._modeFourChanged)
        self._ui.doubleSpinBox_5.valueChanged.connect(self._modeFiveChanged)

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

    def _viewAll(self):
        if self._ui.sceneviewer_widget.getSceneviewer() is not None:
            self._ui.sceneviewer_widget.viewAll()

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

    def _resetClicked(self):
        leftNodes, rightNodes = self._getAverageLung()
        self._meshModel.applyMorphing(leftNodes, lung='left')
        self._meshModel.applyMorphing(rightNodes, lung='right')

    def _getAverageLung(self):
        return self._pcaModel.averageLung()

    def _morphItClicked(self):
        leftNodes, rightNodes = self._getMorphedLung()
        self._meshModel.applyMorphing(leftNodes, lung='left')
        self._meshModel.applyMorphing(rightNodes, lung='right')

    def _getMorphedLung(self):
        weights = [self._modeDict['modeOne'],
                   self._modeDict['modeTwo'],
                   self._modeDict['modeThree'],
                   self._modeDict['modeFour'],
                   self._modeDict['modeFive']
                   ]
        return self._pcaModel.morph(weights)

    def _modeOneChanged(self, value):
        self._modeDict['modeOne'] = value
        leftNodes, rightNodes = self._getMorphedLung()
        self._meshModel.applyMorphing(leftNodes, lung='left')
        self._meshModel.applyMorphing(rightNodes, lung='right')

    def _modeTwoChanged(self, value):
        self._modeDict['modeTwo'] = value
        leftNodes, rightNodes = self._getMorphedLung()
        self._meshModel.applyMorphing(leftNodes, lung='left')
        self._meshModel.applyMorphing(rightNodes, lung='right')

    def _modeThreeChanged(self, value):
        self._modeDict['modeThree'] = value
        leftNodes, rightNodes = self._getMorphedLung()
        self._meshModel.applyMorphing(leftNodes, lung='left')
        self._meshModel.applyMorphing(rightNodes, lung='right')

    def _modeFourChanged(self, value):
        self._modeDict['modeFour'] = value
        leftNodes, rightNodes = self._getMorphedLung()
        self._meshModel.applyMorphing(leftNodes, lung='left')
        self._meshModel.applyMorphing(rightNodes, lung='right')

    def _modeFiveChanged(self, value):
        self._modeDict['modeFive'] = value
        leftNodes, rightNodes = self._getMorphedLung()
        self._meshModel.applyMorphing(leftNodes, lung='left')
        self._meshModel.applyMorphing(rightNodes, lung='right')

