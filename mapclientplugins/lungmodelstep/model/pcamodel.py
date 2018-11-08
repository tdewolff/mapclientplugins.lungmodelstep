from mapclientplugins.lungmodelstep.morphic.mesher import Mesh


class PCAModel(object):

    def __init__(self, model):
        self._pca_model = Mesh()
        self._pca_model.load(model)

    def _get_pca_model(self):
        return self._pca_model

    def _average_lung(self):
        self._pca_model.nodes['weights'].values[1:] = 0  # reset weights to zero
        self._pca_model.nodes['weights'].values[0] = 1  # adding average
        self._pca_model.update_pca_nodes()

    def _get_left_lung_nodes(self):
        return


