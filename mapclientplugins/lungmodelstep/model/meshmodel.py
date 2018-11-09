import os

from opencmiss.zinc.graphics import Graphics


class MeshModel(object):

    def __init__(self, region1, region2, materialModule):
        self._path = self.getPluginPath()

        self._leftRegionName = region1.getName()
        self._rightRegionName = region2.getName()
        self._leftRegion = region1
        self._rightRegion = region2
        self._initializeLeftLung()
        self._initializeRightLung()

        self._materialModule = materialModule

        self._settings = {'displaySurfacesLeft': True,
                          'displaySurfacesRight': True,
                          'Breathing': False}
        self._generateMesh()

    def _getVisibility(self, graphicsName):
        return self._settings[graphicsName]

    def _setVisibility(self, graphicsName, show):
        self._settings[graphicsName] = show
        if graphicsName == 'displaySurfacesLeft':
            graphics = self._leftRegion.getScene().findGraphicsByName(graphicsName)
            graphics.setVisibilityFlag(show)
        elif graphicsName == 'displaySurfacesRight':
            graphics = self._rightRegion.getScene().findGraphicsByName(graphicsName)
            graphics.setVisibilityFlag(show)

    def _generateMesh(self):
        # left lung
        self._leftScene = self._leftRegion.getScene()
        fmLeft = self._leftRegion.getFieldmodule()
        fmLeft.beginChange()
        self._leftCoordinates = fmLeft.findFieldByName('coordinates')
        self._leftMagnitude = fmLeft.createFieldMagnitude(self._leftCoordinates)
        self._leftMagnitude.setName('leftmag')
        self._leftMagnitude.setManaged(True)
        fmLeft.endChange()

        # right lung
        self._rightScene = self._rightRegion.getScene()
        fmRight = self._rightRegion.getFieldmodule()
        fmRight.beginChange()
        self._rightCoordinates = fmRight.findFieldByName('coordinates')
        self._rightMagnitude = fmRight.createFieldMagnitude(self._rightCoordinates)
        self._rightMagnitude.setName('rightmag')
        self._rightMagnitude.setManaged(True)
        fmRight.endChange()

        self.__setupScene(self._leftRegion, self._rightRegion)

    def __setupScene(self, region1, region2):
        # left lung
        leftScene = self.getScene(region1)
        leftScene.beginChange()
        leftMaterialModule = self._materialModule
        leftLines = leftScene.createGraphicsLines()
        leftLines.setCoordinateField(self._leftCoordinates)
        black = leftMaterialModule.findMaterialByName('white')
        leftLines.setMaterial(black)

        leftSurfaces = leftScene.createGraphicsSurfaces()
        leftSurfaces.setCoordinateField(self._leftCoordinates)
        leftSurfaces.setRenderPolygonMode(Graphics.RENDER_POLYGON_MODE_SHADED)
        surfacesMaterial = self._materialModule.findMaterialByName('tissue')
        leftSurfaces.setMaterial(surfacesMaterial)
        leftSurfaces.setName('displaySurfacesLeft')
        leftSurfaces.setVisibilityFlag(self.isDisplaySurfaces('displaySurfacesLeft'))

        # right lung
        rightScene = self.getScene(region2)
        rightScene.beginChange()
        rightMaterialModule = self._materialModule
        rightLines = rightScene.createGraphicsLines()
        rightLines.setCoordinateField(self._rightCoordinates)
        black = rightMaterialModule.findMaterialByName('white')
        rightLines.setMaterial(black)

        rightSurfaces = rightScene.createGraphicsSurfaces()
        rightSurfaces.setCoordinateField(self._rightCoordinates)
        rightSurfaces.setRenderPolygonMode(Graphics.RENDER_POLYGON_MODE_SHADED)
        surfacesMaterial = self._materialModule.findMaterialByName('tissue')
        rightSurfaces.setMaterial(surfacesMaterial)
        rightSurfaces.setName('displaySurfacesRight')
        rightSurfaces.setVisibilityFlag(self.isDisplaySurfaces('displaySurfacesRight'))

        rightScene.endChange()

    def _initializeLeftLung(self):
        nodefile = r'left_average.exnode'
        elemfile = r'left_average.exelem'
        self._leftRegion.readFile(os.path.join('/', self._path, 'fields', nodefile))
        self._leftRegion.readFile(os.path.join('/', self._path, 'fields', elemfile))

    def _initializeRightLung(self):
        nodefile = r'right_average.exnode'
        elemfile = r'right_average.exelem'
        self._rightRegion.readFile(os.path.join('/', self._path, 'fields', nodefile))
        self._rightRegion.readFile(os.path.join('/', self._path, 'fields', elemfile))

    @staticmethod
    def getScene(region):
        return region.getScene()

    @staticmethod
    def getPluginPath():
        return '/'.join(__file__.split('/')[1:-2])

    def isDisplaySurfaces(self, surfaceName):
        return self._getVisibility(surfaceName)
    
    def setDisplaySurfaces(self, surfaceName, show):
        self._setVisibility(surfaceName, show)
 