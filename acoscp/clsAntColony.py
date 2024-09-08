import numpy as np

from multipledispatch import dispatch

from clsAnt import clsAnt


class clsAntColony:
    def __init__(
        self,
        nbrOfAnts,
        alpha,
        beta,
        rho,
        Q0,
        objSCPInfo,
        objPheromone,
        invalidValue,
        infiniteValue,
    ):
        self._nbrOfAnts = nbrOfAnts
        self._alpha = alpha
        self._beta = beta
        self._rho = rho
        self._Q0 = Q0

        self._bestPos = nbrOfAnts
        self._auxPos = nbrOfAnts + 1

        self._invalidValue = invalidValue
        self._infiniteValue = infiniteValue

        self._objSCPInfo = objSCPInfo
        self._objPheromone = objPheromone
        self._tempPath = []

        self.initializeInfo()

    def initializeInfo(self):
        self._myList = [
            clsAnt(
                self.getAlpha(),
                self.getBeta(),
                self.getRho(),
                self.getQ0(),
                self._objSCPInfo,
                self._objPheromone,
                self._infiniteValue,
                self._invalidValue,
            )
            for i in range(self._nbrOfAnts + 2)
        ]

    def getAlpha(self):
        return self._alpha

    def getBeta(self):
        return self._beta

    def getRho(self):
        return self._rho

    def getNbrOfAnts(self):
        return self._nbrOfAnts

    def getQ0(self):
        return self._Q0

    def getAntObject(self, index):
        return self._myList[index]

    def updatePheromone(self, k):
        if 0 <= k < self.getNbrOfAnts():
            self._myList[k].updatePheromone()
        else:
            print("Error clsAntColony updatePheromone, posicion invalida")

    def exchangeColumns(
        self, path_original_sol, columns_inside_sol, columns_outside_sol
    ):
        # guardo una copia del path de la solución original (columnas de la mejor solución obtenida por la mejor hormiga)
        temp_path_sol = list(np.copy(path_original_sol))

        # guardo los indices en dónde se encuentran las columnas a intercambiar (dado por columns_inside_sol que pertenece a la mejor solución)
        index_path_sol = []
        [
            index_path_sol.append(temp_path_sol.index(columns_inside_sol[i]))
            for i in range(len(columns_inside_sol))
        ]

        # seteo los nuevos valores, reemplazo el valor en dónde están los índices de la solución a intercambiar por
        # los valores de las columnas que están fuera de la solución
        for i in range(len(columns_inside_sol)):
            temp_path_sol[index_path_sol[i]] = columns_outside_sol[i]

        return temp_path_sol, index_path_sol

    @dispatch(int)
    def calculateOFValue(self, position):
        if 0 <= position < self.getNbrOfAnts() + 2:
            self._myList[position].calculateOFValue()
        else:
            print("Error clsAntColony calculateOFValue, posicion invalida")

    @dispatch(int, list, list)
    def calculateOFValue(self, k, index, path):
        """CalculA el OFvalue de acuerdo a la posición de la mejor hormiga.

        Args:
            k (int): posición de la mejor hormiga
            index (list): índices de las columnas que fueron reemplazadas
            path (list): el nuevo path
        """

        if 0 <= k < self.getNbrOfAnts() + 2:
            # seteo los costos de las nuevas columnas del path nuevo
            self._myList[k].settingValuesNewPath(index, path)
            # calculo el currOF
            self._myList[k].calculateOFValue()
        else:
            print("Error clsAntColony calculateOFValue, posicion invalida")

    def getOFValue(self, k):
        value = self._infiniteValue

        if 0 <= k < self.getNbrOfAnts() + 2:
            value = self._myList[k].getOFValue()
        else:
            print("Error clsAntColony getOFValue, posicion invalida")

        return value

    def updateBestAnt(self, k):
        """Actualiza la solución de la hormiga k con la mejor solución obtenida

        Args:
            k (int): hormiga k
        """
        if 0 <= k < self.getNbrOfAnts():
            self._myList[self._bestPos].resetPath()

            size = self._myList[k].getPathSize()
            [
                self._myList[self._bestPos].addElementToPath(
                    self._myList[k].getPathElement(i)
                )
                for i in range(size)
            ]

            self.calculateOFValue(self._bestPos)

        else:
            print("Error clsAntColony updateBestAnt, posicion invalida")

    def selectNextNeighbor(self, k):
        if 0 <= k < self.getNbrOfAnts():
            self._myList[k].selectNextNeighbor()
        else:
            print("Error clsAntColony updateBestAnt, posicion invalida")

    def restartInformation(self):
        [self._myList[k].restartInformation() for k in range(self.getNbrOfAnts())]

    def startPaths(self):
        [self._myList[k].startPath() for k in range(self.getNbrOfAnts())]

    def getPathPosition(self, position):
        return [
            self._myList[position].getPathElement(j)
            for j in range(self._myList[position].getPathSize())
        ]

    def getFrecPosition(self, position):
        return self._myList[position].getFrecList()

    def calculateFrecPosition(self, position):
        return self._myList[position].calculateFrec()

    def setPaths(self, path, position):
        return self._myList[position].setPath(path)

    def getObjColsFrecPathPositon(self, position):
        return self._myList[position].getObjColsFrecPath()
