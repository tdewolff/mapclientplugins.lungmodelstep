import os

from opencmiss.zinc.graphics import Graphics


class MeshModel(object):

    def __init__(self, region1, region2, material_module):
        self._path = self.get_plugin_path()

        self._left_region_name = region1.getName()
        self._right_region_name = region2.getName()
        self._left_region = region1
        self._right_region = region2
        self._initialize_left_lung()
        self._initialize_right_lung()

        self._materialmodule = material_module

        self._settings = {'Left': True,
                          'Right': True,
                          'Breathing': False}
        self._generate_mesh()

    def _get_visibility(self, graphics_name):
        return self._settings[graphics_name]

    def _set_visibility(self, graphics_name, show):
        self._settings[graphics_name] = show
        if graphics_name == 'Left':
            graphics = self._left_region.getScene().findGraphicsByName(graphics_name)
        elif graphics_name == 'Right':
            graphics = self._right_region.getScene().findGraphicsByName(graphics_name)
        graphics.setVisibilityFlag(show)

    def _generate_mesh(self):
        # left lung
        self._left_scene = self._left_region.getScene()
        fm_left = self._left_region.getFieldmodule()
        fm_left.beginChange()
        self._left_coordinates = fm_left.findFieldByName('coordinates')
        self._left_magnitude = fm_left.createFieldMagnitude(self._left_coordinates)
        self._left_magnitude.setName('leftmag')
        self._left_magnitude.setManaged(True)
        fm_left.endChange()

        # right lung
        self._right_scene = self._right_region.getScene()
        fm_right = self._right_region.getFieldmodule()
        fm_right.beginChange()
        self._right_coordinates = fm_right.findFieldByName('coordinates')
        self._right_magnitude = fm_right.createFieldMagnitude(self._right_coordinates)
        self._right_magnitude.setName('rightmag')
        self._right_magnitude.setManaged(True)
        fm_right.endChange()

        self._setup_scene(self._left_region, self._right_region)

    def _setup_scene(self, region1, region2):
        # left lung
        left_scene = self.get_scene(region1)
        left_scene.beginChange()
        left_material_module = self._materialmodule
        left_lines = left_scene.createGraphicsLines()
        left_lines.setCoordinateField(self._left_coordinates)
        left_black = left_material_module.findMaterialByName('white')
        left_lines.setMaterial(left_black)

        surfaces = left_scene.createGraphicsSurfaces()
        surfaces.setCoordinateField(self._left_coordinates)
        surfaces.setRenderPolygonMode(Graphics.RENDER_POLYGON_MODE_SHADED)
        surfacesMaterial = self._materialmodule.findMaterialByName('tissue')
        surfaces.setMaterial(surfacesMaterial)
        surfaces.setName('displaySurfaces')
        # surfaces.setVisibilityFlag(self.isDisplaySurfaces())

        # right lung
        right_scene = self.get_scene(region2)
        right_scene.beginChange()
        material_module = self._materialmodule
        lines = right_scene.createGraphicsLines()
        lines.setCoordinateField(self._right_coordinates)
        black = material_module.findMaterialByName('white')
        lines.setMaterial(black)

        surfaces = right_scene.createGraphicsSurfaces()
        surfaces.setCoordinateField(self._right_coordinates)
        surfaces.setRenderPolygonMode(Graphics.RENDER_POLYGON_MODE_SHADED)
        surfacesMaterial = self._materialmodule.findMaterialByName('tissue')
        surfaces.setMaterial(surfacesMaterial)
        surfaces.setName('displaySurfaces')

        right_scene.endChange()

    def _initialize_left_lung(self):
        nodefile = r'left_average.exnode'
        elemfile = r'left_average.exelem'
        self._left_region.readFile(os.path.join('/', self._path, 'fields', nodefile))
        self._left_region.readFile(os.path.join('/', self._path, 'fields', elemfile))

    def _initialize_right_lung(self):
        nodefile = r'right_average.exnode'
        elemfile = r'right_average.exelem'
        self._right_region.readFile(os.path.join('/', self._path, 'fields', nodefile))
        self._right_region.readFile(os.path.join('/', self._path, 'fields', elemfile))

    @staticmethod
    def get_scene(region):
        return region.getScene()

    @staticmethod
    def get_plugin_path():
        return '/'.join(__file__.split('/')[1:-2])