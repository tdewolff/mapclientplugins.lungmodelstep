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

        self._leftMesh = None
        self._rightMesh = None

        self._elemGroups = {'leftUpperLobe': (63, 64, 69, 70, 75, 76, 80, 81, 85, 86, 87, 89, 90, 91, 93, 94, 96, 97, 98, 99, 101, 106),
                            'leftLowerLobe': (65, 66, 67, 71, 72, 73, 77, 78, 82, 83, 102, 103, 104, 107, 108, 109),
                            'rightUpperLobe': (23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38),
                            'rightMiddleLobe': (1, 2, 7, 8, 13, 14, 18, 19, 39, 40, 45, 46),
                            'rightLowerLobe': (3, 4, 5, 6, 9, 10, 11, 12, 15, 16, 17, 20, 21, 22, 41, 42, 43, 44, 47, 48, 49, 50)}

        self._materialModule = materialModule

        # self._settings = {'displaySurfacesLeft': True, 'displaySurfacesRight': True}
        self._settings = {'leftUpperLobe': True, 'leftLowerLobe': True, 'rightUpperLobe': True, 'rightMiddleLobe': True,
                          'rightLowerLobe': True, 'displaySurfacesLeft': True, 'displaySurfacesRight': True}
        self._generateMesh()

        self._nodes = LungNodes()

    def _getVisibility(self, graphicsName):
        return self._settings[graphicsName]

    def _setVisibility(self, graphicsName, show):
        self._settings[graphicsName] = show
        if 'Left' in graphicsName:
            graphics = self._leftRegion.getScene().findGraphicsByName(graphicsName)
            graphics.setVisibilityFlag(show)
        if 'Right' in graphicsName:
            graphics = self._rightRegion.getScene().findGraphicsByName(graphicsName)
            graphics.setVisibilityFlag(show)

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

    def _generateMesh(self):
        # Left Lung:
        self._leftScene = self._leftRegion.getScene()
        fmLeft = self._leftRegion.getFieldmodule()
        fmLeft.beginChange()
        self._leftCoordinates = fmLeft.findFieldByName('coordinates')
        self._leftMagnitude = fmLeft.createFieldMagnitude(self._leftCoordinates)
        self._leftMagnitude.setName('leftmag')
        self._leftMagnitude.setManaged(True)
        """ Create upper and lower lobe groups """
        self._leftUpperLobe = self._creteLobeGroup(fmLeft, 'leftUpperLobe')
        self._leftlowerLobe = self._creteLobeGroup(fmLeft, 'leftLowerLobe')
        fmLeft.endChange()

        # right lung
        self._rightScene = self._rightRegion.getScene()
        fmRight = self._rightRegion.getFieldmodule()
        fmRight.beginChange()
        self._rightCoordinates = fmRight.findFieldByName('coordinates')
        self._rightMagnitude = fmRight.createFieldMagnitude(self._rightCoordinates)
        self._rightMagnitude.setName('rightmag')
        self._rightMagnitude.setManaged(True)
        """ Create upper and lower lobe groups """
        self._rightUpperLobe = self._creteLobeGroup(fmRight, 'rightUpperLobe')
        self._rightMiddleLobe = self._creteLobeGroup(fmRight, 'rightMiddleLobe')
        self._rightLowerLobe = self._creteLobeGroup(fmRight, 'rightLowerLobe')
        fmRight.endChange()

        self.__setupScene(self._leftRegion, self._rightRegion)

    def _creteLobeGroup(self, fm, name):
        mesh = fm.findMeshByDimension(2)
        group = self._createFieldGroup(fm, name)
        elemGroup = self._createElementGroup(group, mesh)
        meshGroup = elemGroup.getMeshGroup()
        self._addSubElements(group)
        el_iter = mesh.createElementiterator()
        element = el_iter.next()
        while element.isValid():
            if element.getIdentifier() in self._elemGroups[name]:
                meshGroup.addElement(element)
            element = el_iter.next()
        return group

    def _createFieldGroup(self, fm, name):
        field = fm.findFieldByName(name)
        if field.isValid():
            group = field.castGroup()
            assert group.isValid(), 'Existing non-group field called ' + name
        else:
            group = fm.createFieldGroup()
            group.setName(name)
            group.setManaged(True)
        return group

    def _createElementGroup(self, grp, mesh):
        elementGroup = grp.getFieldElementGroup(mesh)
        if not elementGroup.isValid():
            elementGroup = grp.createFieldElementGroup(mesh)
        return elementGroup

    def _addSubElements(self, grp):
        """

        :param grp:
        :return:
        """
        from opencmiss.zinc.field import FieldGroup

        grp.setSubelementHandlingMode(FieldGroup.SUBELEMENT_HANDLING_MODE_FULL)
        fm = grp.getFieldmodule()
        for dimension in range(1, 3):
            mesh = fm.findMeshByDimension(dimension)
            elementGroup = grp.getFieldElementGroup(mesh)
            if elementGroup.isValid():
                meshGroup = elementGroup.getMeshGroup()
                meshGroup.addElementsConditional(elementGroup)
        return None

    def __setupScene(self, leftregion, rightregion):
        """

        :param leftregion:
        :param rightregion:
        :return:
        """
        """ Left Lung"""
        leftScene = self._createScene(leftregion)
        leftScene.beginChange()
        self._createLineGraphics(leftScene, self._leftCoordinates, 'displayLinesLeft', 'white')
        self._surfaceLeft = self._createSurfaceGraphics(leftScene, self._leftCoordinates, 'displaySurfacesLeft', 'solidTissue')

        leftScene.endChange()

        """ Right Lung"""
        rightScene = self._createScene(rightregion)
        rightScene.beginChange()
        self._createLineGraphics(rightScene, self._rightCoordinates, 'displayLinesRight', 'white')
        self._surfaceRight = self._createSurfaceGraphics(rightScene, self._rightCoordinates, 'displaySurfacesRight', 'solidTissue')
        rightScene.endChange()

    def _createScene(self, region):
        """

        :param region:
        :return:
        """
        return self.getScene(region)

    def _createLineGraphics(self, scene, coordinates, name, color):
        """

        :param scene:
        :param coordinates:
        :param name:
        :param color:
        :return:
        """
        leftMaterialModule = self._materialModule
        leftLines = scene.createGraphicsLines()
        leftLines.setCoordinateField(coordinates)
        leftLines.setName(name)
        black = leftMaterialModule.findMaterialByName(color)
        leftLines.setMaterial(black)

    def _createSurfaceGraphics(self, scene, coordinates, name, color):
        """

        :param scene:
        :param coordinates:
        :param name:
        :param color:
        :return:
        """
        surface = scene.createGraphicsSurfaces()
        surface.setCoordinateField(coordinates)
        surface.setRenderPolygonMode(Graphics.RENDER_POLYGON_MODE_SHADED)
        surfacesMaterial = self._materialModule.findMaterialByName(color)
        surface.setMaterial(surfacesMaterial)
        surface.setName(name)
        surface.setVisibilityFlag(self.isDisplaySurfaces(name))
        return surface

    def setLeftUpperLobeGraphics(self):
        self._surfaceLeft.setSubgroupField(self._leftlowerLobe)

    def setLeftLowerLobeGraphics(self):
        self._surfaceLeft.setSubgroupField(self._leftUpperLobe)

    def setRightUpperLobeGraphics(self):
        self._surfaceRight.setSubgroupField(self._rightMiddleLobe)
        self._surfaceRight.setSubgroupField(self._rightLowerLobe)

    def setRightMiddleLobeGraphics(self):
        self._surfaceRight.setSubgroupField(self._rightUpperLobe)
        self._surfaceRight.setSubgroupField(self._rightLowerLobe)

    def setRighttLowerLobeGraphics(self):
        self._surfaceRight.setSubgroupField(self._rightUpperLobe)
        self._surfaceRight.setSubgroupField(self._rightMiddleLobe)

    @staticmethod
    def getScene(region):
        return region.getScene()

    @staticmethod
    def getPluginPath():
        return '/'.join(__file__.split('/')[1:-2])

    def isDisplaySurfaces(self, surfaceName):
        return self._getVisibility(surfaceName)

    def setDisplayObjects(self, surfaceName, show):
        self._setVisibility(surfaceName, show)

    def applyMorphing(self, nodeArray, lung=None):
        self._setNodeParameter(nodeArray, lung=lung)

    def _setNodeParameter(self, nodeArray, lung):
        fieldmodule = self._leftRegion.getFieldmodule() if lung == 'left' else self._rightRegion.getFieldmodule() if 'right' == lung else Exception(
            "Region invalid!")
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
        del fieldmodule;
        del cache;
        del node;
        del coordinates
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
