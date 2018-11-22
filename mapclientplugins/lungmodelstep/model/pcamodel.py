import numpy as np
from mapclientplugins.lungmodelstep.morphic.mesher import Mesh
from mapclientplugins.lungmodelstep.fields.nodes import Nodes
from mapclientplugins.lungmodelstep.fields.elements import Elements


class PCAModel(object):

    def __init__(self, pcaModelData):
        self._pcaModel = Mesh()
        self._pcaModel.load(pcaModelData)

        self._nodes = Nodes()
        self._elements = Elements()

    def _getPCAModel(self):
        return self._pcaModel

    def averageLung(self):
        self._pcaModel.nodes['weights'].values[1:] = 0
        self._pcaModel.nodes['weights'].values[0] = 1
        self._pcaModel.update_pca_nodes()
        leftNodes, rightNodes = self._getLeftLungNodes(), self._getRightLungNodes()
        return leftNodes, rightNodes

    def morph(self, weights):
        self._pcaModel.nodes['weights'].values[1:] = 0
        self._pcaModel.nodes['weights'].values[0] = 1
        for modeScore in range(len(weights)):
            self._pcaModel.nodes['weights'].values[modeScore + 1] = weights[modeScore]
            self._pcaModel.update_pca_nodes()
        leftNodes, rightNodes = self._getLeftLungNodes(), self._getRightLungNodes()
        return leftNodes, rightNodes

    def _getLeftLungNodes(self):
        nodeValues = list()
        nodes = self._nodes.setNode(lung='left')
        for nodeNumber in nodes:
            node = self._pcaModel.nodes[nodeNumber]
            nodeValues.append(node.values)
        return np.asarray(nodeValues, dtype=np.float64)

    def _getRightLungNodes(self):
        nodeValues = list()
        nodes = self._nodes.setNode(lung='right')
        for nodeNumber in nodes:
            node = self._pcaModel.nodes[nodeNumber]
            nodeValues.append(node.values)
        return np.asarray(nodeValues, dtype=np.float64)

    def _getLeftNodeIndex(self):
        return self._nodes.setNode(lung='left')

    def _getRightNodeIndex(self):
        return self._nodes.setNode(lung='right')
