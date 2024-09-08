import numpy as np
import math
import random

import clsSolution as Solution


class clsAnt:
    def __init__(
        self,
        alpha,
        beta,
        rho,
        Q0,
        objSCPInfo,
        objPheromone,
        infiniteValue,
        invalidValue,
    ):
        self._alpha = alpha
        self._beta = beta
        self._rho = rho  # Rho, el arraste de evaporación de la feromóna
        self._Q0 = Q0  # parámetro de aprendizaje, q < q0, y q es una variable aleatoria distribuida uniforme en [0,1]

        self._objSCPInfo = objSCPInfo
        self._objPheromone = objPheromone

        self._infiniteValue = infiniteValue
        self._invalidValue = invalidValue

        self.setOFValue(self._infiniteValue)

        self._objAntPath = Solution.clsSolution(
            self._objSCPInfo.getNbrOfCols(), self._invalidValue
        )
        self._objAntPath_temp = Solution.clsSolution(
            self._objSCPInfo.getNbrOfCols(), self._invalidValue
        )

        self._objHeuristicInfo = Solution.clsSolution(
            self._objSCPInfo.getNbrOfCols(), self._invalidValue
        )

        self._objCoverList = Solution.clsSolution(
            self._objSCPInfo.getNbrOfCols(), self._invalidValue
        )

        # lista simple de Frecuencias de filas
        self._objCoverFrecList = Solution.clsSolution(
            self._objSCPInfo.getNbrOfRows(), self._invalidValue
        )
        self._objCoverFrecList.initList()

        # Lista de listas de frecuencias de columnas que cubren una fila del path
        self._objColsFrecPath = Solution.clsSolution(
            self._objSCPInfo.getNbrOfRows(), self._invalidValue
        )
        # Inicializa una lista de lista
        self._objColsFrecPath.initListList()

        self._indexList = []
        self._probabilityList = []
        self.initializeCoverList()

        # inicializo la lista
        self.updateHeuristicInfo(False)

    def getAlpha(self):
        return self._alpha

    def getBeta(self):
        return self._beta

    def getQ0(self):
        return self._Q0

    def getRho(self):
        return self._rho

    def getOFValue(self):
        return self._OFValue

    def setOFValue(self, newValue):
        self._OFValue = newValue

    def getFrecList(self):
        return self._objCoverFrecList._myList

    def getPathList(self):
        return self._objAntPath._myList

    def getObjColsFrecPath(self):
        return self._objColsFrecPath._myList

    def setPath(self, path):
        self._objAntPath.setList(path)

    def calculateOFValue(self):
        size = self._objAntPath.getSize()
        num1 = np.sum(
            [
                self._objSCPInfo.getColumnCost(self._objAntPath.getValueAtPos(j))
                for j in range(size)
            ]
        )

        self.setOFValue(num1)

    def settingValuesNewPath(self, index_list, path):
        """Setea el valor de las columnas que fueron reemplazadas por el nuevo costo de las columnas introducidas

        Args:
            index_list (list): lista de índices de las columnas que fueron intercambiadas
            path (list): path
        """
        for i in range(len(index_list)):
            self._objAntPath.setValueAtPos(index_list[i], path[index_list[i]], True)

    def initializeCoverList(self):
        nbrOfRows = self._objSCPInfo.getNbrOfRows()

        if self.getOFValue() == self._infiniteValue:
            # Lista binaria.
            [self._objCoverList.addValue(0) for i in range(nbrOfRows)]
        else:

            [self._objCoverList.setValueAtPos(j, 0) for j in range(nbrOfRows)]

    # si restart = True, debo actualizar lista y dejarla lista para que la hormiga elija columnas
    def updateHeuristicInfo(self, restart):
        """Actualiza información heurística.txt

        Args:
            restart (Boolean): si = true, entonces debo actualizar la lista y dejarla para que la hormiga elija las columnas.
        """
        rowsCoveredList = []
        nbrOfCols = self._objSCPInfo.getNbrOfCols()
        if not restart:

            if (
                self.getOFValue() == self._infiniteValue
                and self._objHeuristicInfo.getSize() == 0
            ):
                # estoy al inicio y debo calcular para todos
                [
                    self._objHeuristicInfo.addValue(
                        (self._objSCPInfo.getNbrOfRowsCovered(j) + 0.0)
                        / self._objSCPInfo.getColumnCost(j)
                    )
                    for j in range(nbrOfCols)
                ]

            else:
                # calculo en base a la solucion parcial
                counter1 = 0
                for j in range(nbrOfCols):
                    if self._objAntPath.isInside(j):
                        self._objHeuristicInfo.setValueAtPos(
                            j, self._invalidValue, False
                        )

                    else:
                        # si la columna no esta en la solucion en construccion
                        rowsCoveredList = self._objSCPInfo.getRowsCovered(j)
                        columnCost = self._objSCPInfo.getColumnCost(j)

                        counter1 = np.sum(
                            [
                                self._objCoverList.getValueAtPos(t)
                                for t in rowsCoveredList
                            ]
                        )
                        rowsNotCovered = len(rowsCoveredList) - counter1
                        self._objHeuristicInfo.setValueAtPos(
                            j, (rowsNotCovered + 0.0) / columnCost
                        )
                        counter1 = 0

        else:
            # entra en nueva iteracion y debo calcular para todos. Esto se puede calcular una vez y queda fijo
            [
                self._objHeuristicInfo.setValueAtPos(
                    j,
                    (self._objSCPInfo.getNbrOfRowsCovered(j) + 0.0)
                    / self._objSCPInfo.getColumnCost(j),
                )
                for j in range(nbrOfCols)
            ]

    def updatePheromone(self):
        """Actualiza feromona."""
        ratio = 0.0
        for j in range(self._objPheromone.getSize()):
            # % de aprendizaje
            # si el camio fue utilizado por una hormiga
            if self._objAntPath.isInside(j):
                # actualizamos el ratio de aprendizaje como el valor / entre costo del camino por cada hormiga
                ratio = 1.0 / self.getOFValue()

            # si no fue utilizado el camino por una hormiga, devuelvo directamente (1-ro)*tao
            # (el ro es, (1-ro)*Tao + sum delta*pxy)
            # entonces devolvemos getRo*currentValue + ratio
            currValue = self._objPheromone.getValueAtPos(j)
            # Ro es la evaporación de las feromónas
            self._objPheromone.setValueAtPos(j, self.getRho() * currValue + ratio)
            ratio = 0.0

    # con la lista de cover, si no encuentro 0 es xq cubri todo
    def pathIsBuilt(self):
        """Verifica si el path es factible. Si no encuentro 0, es porque se cubrieron todas las filas.

        Returns:
            Boolean: True si la solución es factible, false en c.o.c
        """
        response = False
        if not self._objCoverList.isInside(0):
            response = True

        return response

    def resetNeighbors(self):
        self._indexList = []
        self._probabilityList = []

    def selectNeighbors(self):
        """Selecciona un vecino para construir el path."""
        # obtenemos el número de columnas
        nbrOfCols = self._objSCPInfo.getNbrOfCols()
        sumP = 0.0

        for j in range(nbrOfCols):

            value = self._objHeuristicInfo.getValueAtPos(j)
            if value != self._invalidValue:

                product = math.pow(
                    self._objPheromone.getValueAtPos(j), self.getAlpha()
                ) * math.pow(value, self.getBeta())

                self._probabilityList.append(product)
                self._indexList.append(j)

                sumP += product
        if sumP > 0:
            size = len(self._probabilityList)
            t = [(self._probabilityList[i] + 0.0) / sumP for i in range(size)]

            self._probabilityList = t
        else:
            print("Error clsAnt selectNeighbors, no hay vecinos disponibles")

    def sortProbabilities(self):
        size = len(self._probabilityList)

        for i in range(size - 1):
            maxP = i
            for j in range(i + 1, size):
                if self._probabilityList[j] > self._probabilityList[maxP]:
                    maxP = j
            auxP = self._probabilityList[i]
            auxI = self._indexList[i]

            self._probabilityList[i] = self._probabilityList[maxP]
            self._indexList[i] = self._indexList[maxP]

            self._probabilityList[maxP] = auxP
            self._indexList[maxP] = auxI

    def selectNextNeighbor(self):

        if not self.pathIsBuilt():
            self.resetNeighbors()
            self.selectNeighbors()
            self.sortProbabilities()

            probAtRandom = random.random()
            neighbor = self._invalidValue

            if probAtRandom <= self.getQ0():
                if self._probabilityList[0] > 0:

                    self.addElementToPath(self._indexList[0])
            else:
                probAtRandom = random.random()

                sumP = 0.0
                size = len(self._probabilityList)
                i = 0

                while i < size and sumP < probAtRandom:
                    sumP += self._probabilityList[i]
                    i += 1

                if sumP >= probAtRandom:
                    neighbor = self._indexList[i - 1]

                    self.addElementToPath(neighbor)

                else:
                    print("Erro clsAnt selectNextNeighbor, no se puede terminar el camino")

    def getPathElement(self, position):
        return self._objAntPath.getValueAtPos(position)

    def addElementToPath(self, element):
        self._objAntPath.addValue(element)

        self.updateHeuristicInfo(False)

        # aca debo marcar las filas que cubre la columna
        rowsCoveredList = self._objSCPInfo.getRowsCovered(element)

        [self._objCoverList.setValueAtPos(t, 1) for t in rowsCoveredList]

    def recalculateRowsCovered(self):
        """Recalcula las filas cubiertas por el path de la hormiga.

        Notes
        -----
        Recalcula las filas cubiertas por el path actual de la hormiga, y
        """

        self.updateHeuristicInfo(False)

        for x in range(self._objAntPath.getSize()):

            # aca debo marcar las filas que cubre la columna
            rowsCoveredList = self._objSCPInfo.getRowsCovered(
                self._objAntPath.getValueAtPos(x)
            )

            [self._objCoverList.setValueAtPos(t, 1) for t in rowsCoveredList]

    # Calcula la frecuencia de filas.
    def calculateFrec(self):
        """Calcula la frecuencia de filas."""

        # GetPathList obtiene las columnas del path, y luego nos fijamos cuáles son las filas que cubren
        # Entonces calculamos la frecuencia de filas y columnas
        for k in self.getPathList():
            for j in self._objSCPInfo.getRowsCovered(k):
                # Frecuencia de filas
                self._objCoverFrecList.incValueAtPos(j)
                # Aquí obtenemos la frecuencia de una fila y su correspondiente columna
                self._objColsFrecPath.addValueAtPos(j, k)

    def startPath(self):

        # esto se hace la primera vez
        nbrOfCols = self._objSCPInfo.getNbrOfCols()
        column = random.randint(0, nbrOfCols - 1)

        self.addElementToPath(column)

    def getPathSize(self):
        size = self._objAntPath.getSize()
        return size

    def resetPath(self):
        self._objAntPath.resetSolution()

    def restartInformation(self):
        self.resetPath()

        self.initializeCoverList()

        self.updateHeuristicInfo(True)

        self.resetNeighbors()
