import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

import sys
from PySide import QtGui
from mapclientplugins.lungmodelstep.view.lungmodelwidget import LungModelWidget
from mapclientplugins.lungmodelstep.model.lungmodel import LungModel
from mapclientplugins.lungmodelstep.model.pcamodel import PCAModel

def done():
    None

app = QtGui.QApplication(sys.argv)
pcaModel = PCAModel('lung_pmodel')
model = LungModel()

# Check errors
num = model._logger.getNumberOfMessages()
print num
for i in range(0, num):
    print model._logger.getMessageTextAtIndex(i)

view = LungModelWidget(model, pcaModel)
view.registerDoneCallback(done)
view.show()
sys.exit(app.exec_())
