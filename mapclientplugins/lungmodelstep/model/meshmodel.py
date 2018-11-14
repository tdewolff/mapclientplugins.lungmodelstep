import os

from scaffoldmaker.utils.zinc_utils import *

from opencmiss.zinc.graphics import Graphics
from opencmiss.zinc.field import Field
from opencmiss.utils.maths import vectorops
from opencmiss.zinc.status import OK as ZINC_OK

from mapclientplugins.lungmodelstep.fields.nodes import Nodes as LungNodes


class MeshModel(object):

    def __init__(self, leftregion, rightregion, materialModule):
        self._path = self.getPluginPath()

        self._leftRegionName = leftregion.getName()
        self._rightRegionName = rightregion.getName()
        self._leftRegion = leftregion
        self._rightRegion = rightregion
        self._initializeLeftLung()
        self._initializeRightLung()

        self._materialModule = materialModule

        self._settings = {'displaySurfacesLeft': True, 'displaySurfacesRight': True, 'Breathing': False}
        self._generateMesh()

        self._nodes = LungNodes()

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

    def __setupScene(self, leftregion, rightregion):
        # left lung
        leftScene = self.getScene(leftregion)
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
        rightScene = self.getScene(rightregion)
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

    def applyMorphing(self, nodeArray, lung=None):
        self._setNodeParameter(nodeArray, lung=lung)

    def _setNodeParameter(self, nodeArray, lung):
        fieldmodule = self._leftRegion.getFieldmodule() if lung == 'left' else self._rightRegion.getFieldmodule() if 'right' == lung else Exception("Region invalid!")
        if lung == 'left' and nodeArray.shape[0] != 99:
            raise Exception("Lung and node array do not match!")
        elif lung == 'right' and nodeArray.shape[0] != 126:
            raise Exception("Lung and node array do not match!")

        nodes = self._getLeftNodeField() if lung == 'left' else self._getRightNodeField()
        cache = fieldmodule.createFieldcache()
        coordinates = getOrCreateCoordinateField(fieldmodule)
        nodeIndex = self._getLeftNodeIndex() if lung == 'left' else self._getRightNodeIndex()

        fieldmodule.beginChange()
        node_iter = nodes.createNodeiterator()
        node = node_iter.next()

        for n in range(nodeArray.shape[0]):

            if "." not in nodeIndex[n]:
                nodeID = int(nodeIndex[n])
                nodeVersion = 1
            else:
                nodeID = int(nodeIndex[n].split('.')[0])
                nodeVersion = int(nodeIndex[n].split('.')[1])

            if node.getIdentifier() == nodeID:
                pass
            else:
                node = node_iter.next()

            cache.setNode(node)
            resultList = list()
            """ setting the node xyz coordinates """
            rx = coordinates.setNodeParameters(cache, 1, Node.VALUE_LABEL_VALUE, nodeVersion, nodeArray[n, 0, 0])
            ry = coordinates.setNodeParameters(cache, 2, Node.VALUE_LABEL_VALUE, nodeVersion, nodeArray[n, 1, 0])
            rz = coordinates.setNodeParameters(cache, 3, Node.VALUE_LABEL_VALUE, nodeVersion, nodeArray[n, 2, 0])
            """ setting the nodal x derivatives """
            rxds1 = coordinates.setNodeParameters(cache, 1, Node.VALUE_LABEL_D_DS1, nodeVersion, nodeArray[n, 0, 1])
            rxds2 = coordinates.setNodeParameters(cache, 1, Node.VALUE_LABEL_D_DS2, nodeVersion, nodeArray[n, 0, 2])
            rxds12 = coordinates.setNodeParameters(cache, 1, Node.VALUE_LABEL_D2_DS1DS2, nodeVersion,
                                                   nodeArray[n, 0, 3])
            """ setting the nodal y derivatives """
            ryds1 = coordinates.setNodeParameters(cache, 2, Node.VALUE_LABEL_D_DS1, nodeVersion, nodeArray[n, 1, 1])
            ryds2 = coordinates.setNodeParameters(cache, 2, Node.VALUE_LABEL_D_DS2, nodeVersion, nodeArray[n, 1, 2])
            ryds12 = coordinates.setNodeParameters(cache, 2, Node.VALUE_LABEL_D2_DS1DS2, nodeVersion,
                                                   nodeArray[n, 1, 3])
            """ setting the nodal z derivatives """
            rzds1 = coordinates.setNodeParameters(cache, 3, Node.VALUE_LABEL_D_DS1, nodeVersion, nodeArray[n, 2, 1])
            rzds2 = coordinates.setNodeParameters(cache, 3, Node.VALUE_LABEL_D_DS2, nodeVersion, nodeArray[n, 2, 2])
            rzds12 = coordinates.setNodeParameters(cache, 3, Node.VALUE_LABEL_D2_DS1DS2, nodeVersion,
                                                   nodeArray[n, 2, 3])
            resultList.append(rx);
            resultList.append(ry);
            resultList.append(rz);
            resultList.append(rxds1);
            resultList.append(rxds2);
            resultList.append(rxds12);
            resultList.append(ryds1);
            resultList.append(ryds2);
            resultList.append(ryds12);
            resultList.append(rzds1);
            resultList.append(rzds2);
            resultList.append(rzds12);

            for result in resultList:
                if result == ZINC_OK:
                    pass
                else:
                    print("ZINC NOT OK!")
                    print("NODE: {}".format(nodeID))
                    break

        fieldmodule.endChange()
        return None

    def _getLeftNodeField(self):
        fieldmodule = self._leftRegion.getFieldmodule()
        nodes = fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        return nodes

    def _getRightNodeField(self):
        fieldmodule = self._rightRegion.getFieldmodule()
        nodes = fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        return nodes

    def _getLeftNodeIndex(self):
        return self._nodes.setNode(lung='left')

    def _getRightNodeIndex(self):
        return self._nodes.setNode(lung='right')
