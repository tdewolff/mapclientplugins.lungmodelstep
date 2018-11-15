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
            'modeSix': 0.0,
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
        self._ui.exit_pushButton.clicked.connect(self._doneClicked)
        self._ui.reset_pushButton.clicked.connect(self._resetClicked)
        """ Left lung """
        self._ui.leftlungUpper_checkBox.clicked.connect(self._leftLungUpperClicked)
        self._ui.leftlungLower_checkBox.clicked.connect(self._leftLungLowerClicked)
        """ Right lung """
        self._ui.rightlungUpper_checkBox.clicked.connect(self._rightLungUpperClicked)
        self._ui.rightlungMiddle_checkBox.clicked.connect(self._rightLungMiddleClicked)
        self._ui.rightlungLower_checkBox.clicked.connect(self._rightLungLowerClicked)
        """ Modes """
        self._ui.modeOne_doubleSpinBox.valueChanged.connect(self._modeOneChanged)
        self._ui.modeTwo_doubleSpinBox.valueChanged.connect(self._modeTwoChanged)
        self._ui.modeThree_doubleSpinBox.valueChanged.connect(self._modeThreeChanged)
        self._ui.modeFour_doubleSpinBox.valueChanged.connect(self._modeFourChanged)
        self._ui.modeFive_doubleSpinBox.valueChanged.connect(self._modeFiveChanged)
        self._ui.modeSix_doubleSpinBox.valueChanged.connect(self._modeSixeChanged)

    def _doneClicked(self):
        self._doneCallback()

    def _initialUiState(self):
        self._ui.leftlungUpper_checkBox.setChecked(True)
        self._ui.leftlungLower_checkBox.setChecked(True)
        self._ui.rightlungUpper_checkBox.setChecked(True)
        self._ui.rightlungMiddle_checkBox.setChecked(True)
        self._ui.rightlungLower_checkBox.setChecked(True)

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

    def _leftLungUpperClicked(self):
        # num = self._model._logger.getNumberOfMessages()
        # print num
        # for i in range(0, num):
        #     print self._model._logger.getMessageTextAtIndex(i)
        self._meshModel.setDisplaySurfaces('displaySurfacesLeft', self._ui.leftlungUpper_checkBox.isChecked())
        self._meshModel.setDisplaySurfaces('displayLinesLeft', self._ui.leftlungUpper_checkBox.isChecked())

    def _leftLungLowerClicked(self):
        self._meshModel.setDisplaySurfaces('displaySurfacesLeft', self._ui.leftlungLower_checkBox.isChecked())

    def _rightLungUpperClicked(self):
        self._meshModel.setDisplaySurfaces('displaySurfacesRight', self._ui.rightlungUpper_checkBox.isChecked())

    def _rightLungMiddleClicked(self):
        self._meshModel.setDisplaySurfaces('displaySurfacesRight', self._ui.rightlungMiddle_checkBox.isChecked())

    def _rightLungLowerClicked(self):
        self._meshModel.setDisplaySurfaces('displaySurfacesRight', self._ui.rightlungLower_checkBox.isChecked())

    def _resetClicked(self):
        self._resetSpinBoxValues()
        self._applyMorphing()
        # leftNodes, rightNodes = self._getAverageLung()
        # self._meshModel.applyMorphing(leftNodes, lung='left')
        # self._meshModel.applyMorphing(rightNodes, lung='right')

    def _getAverageLung(self):
        return self._pcaModel.averageLung()

    def _getMorphedLung(self):
        weights = [self._modeDict['modeOne'],
                   self._modeDict['modeTwo'],
                   self._modeDict['modeThree'],
                   self._modeDict['modeFour'],
                   self._modeDict['modeFive'],
                   self._modeDict['modeSix']
                   ]
        return self._pcaModel.morph(weights)

    def _modeOneChanged(self, value):
        self._changeMode('modeOne', value)

    def _modeTwoChanged(self, value):
        self._changeMode('modeTwo', value)

    def _modeThreeChanged(self, value):
        self._changeMode('modeThree', value)

    def _modeFourChanged(self, value):
        self._changeMode('modeFour', value)

    def _modeFiveChanged(self, value):
        self._changeMode('modeFive', value)

    def _modeSixeChanged(self, value):
        self._changeMode('modeSix', value)

    def _changeMode(self, mode, value):
        self._modeDict[mode] = value
        self._applyMorphing()

    def _resetSpinBoxValues(self):
        self._ui.modeOne_doubleSpinBox.setValue(0.0)
        self._ui.modeTwo_doubleSpinBox.setValue(0.0)
        self._ui.modeThree_doubleSpinBox.setValue(0.0)
        self._ui.modeFour_doubleSpinBox.setValue(0.0)
        self._ui.modeFive_doubleSpinBox.setValue(0.0)
        self._ui.modeSix_doubleSpinBox.setValue(0.0)
        return

    def _applyMorphing(self):
        leftNodes, rightNodes = self._getMorphedLung()
        self._meshModel.applyMorphing(leftNodes, lung='left')
        self._meshModel.applyMorphing(rightNodes, lung='right')




