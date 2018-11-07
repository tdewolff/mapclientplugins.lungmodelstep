
"""
MAP Client Plugin Step
"""
import json
import os
from PySide import QtGui

from mapclient.mountpoints.workflowstep import WorkflowStepMountPoint
from mapclientplugins.lungmodelstep.configuredialog import ConfigureDialog
from mapclientplugins.lungmodelstep.view.lungmodelwidget import LungModelWidget

from mapclientplugins.lungmodelstep.model.pcamodel import PCAModel


class LungModelStep(WorkflowStepMountPoint):
    """
    Skeleton step which is intended to be a helpful starting point
    for new steps.
    """

    def __init__(self, location):
        super(LungModelStep, self).__init__('Lung Model', location)
        self._configured = False # A step cannot be executed until it has been configured.
        self._category = 'Morphometric'
        # Add any other initialisation code here:
        self._icon =  QtGui.QImage(':/lungmodelstep/images/morphometric.png')
        # Ports:
        self.addPort(('http://physiomeproject.org/workflow/1.0/rdf-schema#port',
                      'http://physiomeproject.org/workflow/1.0/rdf-schema#provides',
                      'mesh'))
        self.addPort(('http://physiomeproject.org/workflow/1.0/rdf-schema#port',
                      'http://physiomeproject.org/workflow/1.0/rdf-schema#uses',
                      'http://physiomeproject.org/workflow/1.0/rdf-schema#file_location'))
        # Port data:
        self._portData0 = None # mesh
        self._pca_model = None # pca_model
        # Config:
        self._config = {}
        self._config['identifier'] = ''
        self._view = None

    def execute(self):
        """
        Add your code here that will kick off the execution of the step.
        Make sure you call the _doneExecution() method when finished.  This method
        may be connected up to a button in a widget for example.
        """
        # Put your execute step code here before calling the '_doneExecution' method.

        all_settings = {}
        try:
            with open(self._get_settings_file_name()) as f:
                all_settings = json.loads(f.read())
        except EnvironmentError:
            pass

        average_mesh = PCAModel(self._pca_model)
        average_mesh._average_lung()

        self._view = LungModelWidget()
        if 'view' in all_settings:
            self._view.set_settings(all_settings['view'])

        self._view.register_done_callback(self._interactionDone)
        self._setCurrentWidget(self._view)

        print("Executing...")

    def _interactionDone(self):
        all_settings = {'view': self._view.get_settings()}
        settings_in_string_form = json.dumps(all_settings, default=lambda o: o.__dict__, sort_keys=True, indent=4)
        with open(self._get_settings_file_name(), 'w') as f:
            f.write(settings_in_string_form)

        self._view = None
        self._doneExecution()

    def _get_settings_file_name(self):
        return os.path.join(self._location, self._config['identifier'] + '.settings')

    def setPortData(self, index, dataIn):
        """
        Add your code here that will set the appropriate objects for this step.
        The index is the index of the port in the port list.  If there is only one
        uses port for this step then the index can be ignored.

        :param index: Index of the port to return.
        :param dataIn: The data to set for the port at the given index.
        """
        self._pca_model = dataIn # pca_model

    def getPortData(self, index):
        """
        Add your code here that will return the appropriate objects for this step.
        The index is the index of the port in the port list.  If there is only one
        provides port for this step then the index can be ignored.

        :param index: Index of the port to return.
        """
        return self._portData0 # mesh

    def configure(self):
        """
        This function will be called when the configure icon on the step is
        clicked.  It is appropriate to display a configuration dialog at this
        time.  If the conditions for the configuration of this step are complete
        then set:
            self._configured = True
        """
        dlg = ConfigureDialog(self._main_window)
        dlg.identifierOccursCount = self._identifierOccursCount
        dlg.setConfig(self._config)
        dlg.validate()
        dlg.setModal(True)

        if dlg.exec_():
            self._config = dlg.getConfig()

        self._configured = dlg.validate()
        self._configuredObserver()

    def getIdentifier(self):
        """
        The identifier is a string that must be unique within a workflow.
        """
        return self._config['identifier']

    def setIdentifier(self, identifier):
        """
        The framework will set the identifier for this step when it is loaded.
        """
        self._config['identifier'] = identifier

    def serialize(self):
        """
        Add code to serialize this step to string.  This method should
        implement the opposite of 'deserialize'.
        """
        return json.dumps(self._config, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def deserialize(self, string):
        """
        Add code to deserialize this step from string.  This method should
        implement the opposite of 'serialize'.

        :param string: JSON representation of the configuration in a string.
        """
        self._config.update(json.loads(string))

        d = ConfigureDialog()
        d.identifierOccursCount = self._identifierOccursCount
        d.setConfig(self._config)
        self._configured = d.validate()


