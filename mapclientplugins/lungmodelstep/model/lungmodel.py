from opencmiss.zinc.context import Context
from opencmiss.zinc.material import Material

from mapclientplugins.lungmodelstep.model.meshmodel import MeshModel


class LungModel(object):

    def __init__(self):
        self._context = Context("LungModelView")
        self._logger = self._context.getLogger()
        self._initialize()
        self._left_region = self.set_region('leftregion')
        self._right_region = self.set_region('rightlung')

        self._meshmodel = MeshModel(self._left_region, self._right_region, self._materialmodule)

    def get_context(self):
        return self._context

    def set_region(self, name):
        region = self._context.getDefaultRegion().createChild(name)
        return region

    def _initialize(self):
        tess = self._context.getTessellationmodule().getDefaultTessellation()
        tess.setRefinementFactors(12)
        # set up standard materials and glyphs so we can use them elsewhere
        self._materialmodule = self._context.getMaterialmodule()
        self._materialmodule.defineStandardMaterials()

        solid_blue = self._materialmodule.createMaterial()
        solid_blue.setName('solid_blue')
        solid_blue.setManaged(True)
        solid_blue.setAttributeReal3(Material.ATTRIBUTE_AMBIENT, [0.0, 0.2, 0.6])
        solid_blue.setAttributeReal3(Material.ATTRIBUTE_DIFFUSE, [0.0, 0.7, 1.0])
        solid_blue.setAttributeReal3(Material.ATTRIBUTE_EMISSION, [0.0, 0.0, 0.0])
        solid_blue.setAttributeReal3(Material.ATTRIBUTE_SPECULAR, [0.1, 0.1, 0.1])
        solid_blue.setAttributeReal(Material.ATTRIBUTE_SHININESS, 0.2)

        trans_blue = self._materialmodule.createMaterial()
        trans_blue.setName('trans_blue')
        trans_blue.setManaged(True)
        trans_blue.setAttributeReal3(Material.ATTRIBUTE_AMBIENT, [0.0, 0.2, 0.6])
        trans_blue.setAttributeReal3(Material.ATTRIBUTE_DIFFUSE, [0.0, 0.7, 1.0])
        trans_blue.setAttributeReal3(Material.ATTRIBUTE_EMISSION, [0.0, 0.0, 0.0])
        trans_blue.setAttributeReal3(Material.ATTRIBUTE_SPECULAR, [0.1, 0.1, 0.1])
        trans_blue.setAttributeReal(Material.ATTRIBUTE_ALPHA, 0.3)
        trans_blue.setAttributeReal(Material.ATTRIBUTE_SHININESS, 0.2)

        tissue = self._materialmodule.createMaterial()
        tissue.setName('tissue')
        tissue.setManaged(True)
        tissue.setAttributeReal3(Material.ATTRIBUTE_AMBIENT, [0.9, 0.7, 0.5])
        tissue.setAttributeReal3(Material.ATTRIBUTE_DIFFUSE, [0.9, 0.7, 0.5])
        tissue.setAttributeReal3(Material.ATTRIBUTE_EMISSION, [0.0, 0.0, 0.0])
        tissue.setAttributeReal3(Material.ATTRIBUTE_SPECULAR, [0.2, 0.2, 0.3])
        tissue.setAttributeReal(Material.ATTRIBUTE_ALPHA, 1.0)
        tissue.setAttributeReal(Material.ATTRIBUTE_SHININESS, 0.2)

        glyphmodule = self._context.getGlyphmodule()
        glyphmodule.defineStandardGlyphs()

    def get_scene(self):
        return self._left_region.getScene(), self._right_region.getScene()

