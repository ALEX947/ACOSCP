import functools
import math
import operator
import random
import time
import numpy as np
import pandas as pd

from clsAnt import clsAnt
from clsAntColony import clsAntColony
from clsPheromone import clsPheromone
from clsSCPInfo import clsSCPInfo
from clsSolution import clsSolution


class clsACOSCP:

    def __init__(self):

        self._alpha = 0
        self._beta = 0
        self._rho = 0
        self._initialValue = 0.0
        self._Q0 = 0.0

        self._iters = 0
        self._ants = 0

        self._instanceName = ""
        self._resultDir = ""
        self._instanceDir = ""

        self._invalidValue = -1  # valor invalido de posiciones
        self._infiniteValue = 100000

        self._objSCPInfo = clsSCPInfo(self._invalidValue, self._infiniteValue)
        self._objAntColony = None
        self._objPheromone = None

        self._bestOF = self._infiniteValue
        self._currOF = self._infiniteValue
        self._currPos = self._invalidValue

        self._startTime = 0
        self._percentage = 20

        self._objBestSolutions = clsSolution(50, self._infiniteValue)

        self._counterEqualSol = 0
        self._tempCurrOF = 0

    def setAlpha(self, alpha):
        self._alpha = alpha

    def getAlpha(self):
        return self._alpha

    def setBeta(self, beta):
        self._beta = beta

    def getBeta(self):
        return self._beta

    def setRho(self, rho):
        self._rho = rho

    def getRho(self):
        return self._rho

    def setQ0(self, Q0):
        self._Q0 = Q0

    def getQ0(self):
        return self._Q0

    def setInitialValue(self, initialValue):
        self._initialValue = initialValue

    def getInitialValue(self):
        return self._initialValue

    def setNbrOfAnts(self, nbrOfAnts):
        self._nbrOfAnts = nbrOfAnts

    def getNbrOfAnts(self):
        return self._nbrOfAnts

    def setNbrOfIters(self, iters):
        self._iters = iters

    def getNbrOfIters(self):
        return self._iters

    def setBestOFValue(self, newValue):
        self._bestOF = newValue

    def getBestOFValue(self):
        return self._bestOF

    def setResultDir(self, resultDir):
        self._resultDir = resultDir

    def getResultDir(self):
        return self._resultDir

    def setInstanceDir(self, instanceDir):
        self._instanceDir = instanceDir
        self._objSCPInfo.setInstanceDir(instanceDir)

    def getInstanceDir(self):
        return self._instanceDir

    def getFilename(self):
        return self._instanceDir + self._instanceName

    def setInstanceName(self, instanceName):
        self._instanceName = instanceName

        self._objSCPInfo.setInstanceName(instanceName)

    def getInstanceName(self):
        return self._instanceName

    def setTime(self, startTime):
        self._startTime = startTime

    def getTime(self):
        return self._startTime

    def readInstance(self):
        self._objSCPInfo.readInstance()

    def flatList(self, temp_list, dim):
        """Reduce la dimensión de una lista de lista a una lista simple (de filas únicas)

        Examples
        --------
        >>> list = [[1,2,3,4], [5,1,2]]

        >>> new_list = [1,2,3,4,5,1,2]

        Parameters
        ----------
        temp_list: list
        ---
            Lista de columnas (path de la hormiga).
        dim: int [0, n]
            Dimensión de la lista

        Returns
        ----------
        list : list
        ---
            Retorna una lista simple, con la dimensión reducida a uno.

        Notes
        ----------
        Si dim = 1 => devuelve la lista sin hacer nada
        Si dim > 1 => devuelve la lista de lista convertida en una lista simple.
        Es decir reduce la dimensión a 1.
        """

        if dim == 1:
            return temp_list
        else:
            return functools.reduce(operator.iconcat, temp_list, [])

    def getFlatPath(self, list_cols):
        """Reduce la dimensión de una lista de lista (filas cubiertas por el
        path de una hormiga), a una lista simple (de filas únicas)
        Parameters
        ----------
        list_cols: list
        ---
            Lista de columnas (path de la hormiga).

        Returns
        ----------
        flat_path : list
        ---
            Devuelve la lista de filas únicas que son cubiertas por un path de una hormiga
        """

        flat_path = []
        if len(list_cols) > 0:
            dim = 2
            temp = self._objSCPInfo.getRowsCovered_V3(list_cols)
            flat_path = np.unique(self.flatList(temp, dim))
        else:
            print("Error clsACOSCP. Len list_cols is null")
        return flat_path

    def getPercentDiffCurrOf(self, curr_A, curr_B):
        """Devuelve el porcentaje en el que nos pasamos de la solución anterior
        Parameters
        ----------
        curr_A: int [0, n]
        ---
            Solución anterior.
        curr_B: int [0, n]
        ---
            Solución nueva

        Returns
        ----------
        float : >= 0
        ---
            Devuelve el % de la diferencia entre la solución anterior
            y la solución nueva.
        """
        return math.fabs(curr_A - curr_B) * 100 / curr_B

    def setPercent(self):
        """Setea self._percentage a la mitad de su valor.
        Note
        ----
            Se utiliza cada vez que se encuentra una nueva solución factible menor que un tanto por ciento.
            Según la diferencia que haya entre la solución anterior y la actual.
        """

        if self._percentage > 1:
            self._percentage = self._percentage / 2

    def getCostIndexOutsidePath(self, colums_inside_solution):
        """Obtiene la lista de columnas que no están en la solución actual de la hormiga.

        Parameters
        ----------
        columns_inside_solution : list
        ---
            Path de columnas de la hormiga original.

        Returns
        -------
        list_order : list
        ---
            Se devuelve una lista de índices ordenada (vecindario, columnas que quedan fuera de la
            solución) de menor a mayor coste.

        Notes
        -------
        Se ordena la lista únicamente por índices, no se ordena la lista de vecinos original.
        """

        # Obtenemos el vencindario, que es simplemente un array de 0 hasta el número de columnas del problema
        neighborhood = np.arange(self._objSCPInfo.getNbrOfCols())

        # Obtenemos el vecindario de columnas que quedan fuera de la solución
        neighborhood_outside_solutions = list(
            set(neighborhood) - set(colums_inside_solution)
        )

        list_index = self._objSCPInfo.getIndexByPath(neighborhood_outside_solutions)
        list_cost = self._objSCPInfo.getColumnCostV2(list_index)

        # Ordenamos las columnas de menor a mayor costo (sólo ordenamos por índices)
        list_order = sorted(list_index, key=lambda k: list_cost[k])

        return list_order

    def getNewCurrOF(self, position, index, new_colums_solution):
        """Obtiene un nuevo valor de currOF, y setea ese valor en la hormiga.

        Parameters
        ----------
        position : int [0, number_of_ants]
        ----------------------------------
            Posición de la hormiga a la que se le calculara el OF segun su path.
        index : list
        ------------
            Lista de índices de las columnas intercambiadas.
        new_colums_solution : list
        -------------------------
            Lista con las columnas nuevas a intercabiar en el path de la hormiga

        Return
        ------
            new_currOf : Nuevo valor de la funcion objetivo

        """

        new_currOf = 0

        if 0 <= position < self.getNbrOfAnts() + 2:
            if len(index) > 0 and len(new_colums_solution) > 0:

                self._objAntColony.calculateOFValue(
                    position, index, new_colums_solution
                )

                # obtenemos el nuevo valor de currOF
                new_currOf = self._objAntColony.getOFValue(position)
            else:
                print("Error clsACOSCP. Index or path are null")
        else:
            print("Error clsACOSCP. Invalid position getnewcurrOF")

        return new_currOf

    def getFeasibility(
        self, currOF, position, index, colums_inside_solution, new_colums_solution
    ):
        """Verifica si una solución es factible o no.

        Parameters
        ----------
        currOf   : int [0, n]
        ---
            Valor de la solución de la hormiga actual.
        position : int [0, number_of_ants]
        ---
            Posición de la hormiga, para eliminar columnas que sean redundantes
        index    : list
        ---
            Lista de índices de las columnas que fueron intercambiadas en la solución original.
        columns_inside_solution : list
        ---
            Path de columnas de la hormiga original.
        new_colums_solution : list
            Path de columnas nuevo (con los intercambios de columnas realizados)

        Returns
        -------
        flag : [True, False]
        ---
            Retorna flag = True, si la solución es factible.
            Retorna flag = False, si la solución no es factible.

        Notes
        -------
        Se obtiene la lista de filas que son cubiertas por el path nuevo y el path viejo. Como se devuelve
        una lista de lista, entonces se hace un flat, y se obtiene dos listas que contiene elementos únicos
        (filas cubiertas por ambos path). Si la cantidad de filas cubiertas por el nuevo path, es igual
        a la cantidad de filas cubiertas por el path original (según la cantidad de filas del problema,
        entonces la solución es factible, sino, no lo es).
        """

        flag = False

        # Obtengo en una lista simple de 1 dimensión todas las filas cubiertas por el nuevo path (Que contiene las nuevas columnas agregadas)
        flat_new_path = self.getFlatPath(new_colums_solution)

        # Obtengo en una lista simple de 1 dimensión todas las filas cubiertas por el path original (antes de reemplazar las columnas)
        flat_old_path = self.getFlatPath(colums_inside_solution)

        if len(new_colums_solution) > 0 and len(colums_inside_solution) > 0:

            # Como obtengo una lista única de todas las filas cubiertas por las columnas de
            # los path nuevo y viejo, directamente se pregunta por el len de ambos path
            if len(flat_old_path) == len(flat_new_path):

                # Si son iguales, quiere decir que es factible y que cubre todas las filas.
                # Luego calculamos el neuvo CurrOf para el nuevo path
                new_currOf = self.getNewCurrOF(position, index, new_colums_solution)

                if new_currOf != 0:

                    flag = True

                    # Si el currOF del nuevo path No es mejor al currOF local, entonces
                    # restauramos los valores de los costos originales de las columnas que fueron
                    # intercambiadas.
                    if not (new_currOf < currOF):
                        # Restaura las columnas
                        self.getNewCurrOF(position, index, colums_inside_solution)
        else:
            print("Error clsACOSCP. Los paths están vacíos")

        return flag

    def sortedIndexList(self, list, order):
        """Ordena una lista de números, de acuerdo a sus índices.

        Parameters
        ----------
        list : list
        ---
            Lista de números a ordenar
        order : [True, False].
        ---
            Si order = True, entonces se ordena de manera descendente.
            Si order = False, entonces se ordena de manera ascendente.

        Returns
        -------
        listord : list
        ---
        Devuelve una lista ordenada de índices, dada la lista de números.
        """
        listord = []

        if len(list) > 0:
            index = np.arange(len(list))
            listord = sorted(index, key=lambda k: list[k], reverse=order)
        else:
            print("Error clsACOSCP sortedIndexList. Lista vacia.")

        return listord

    def deleteRedudant(self, position):
        """Elimina las columnas redundantes de una solución (de una determinada hormiga).

        Parameters
        ----------
        position : int [0, number_of_ants]
        ---
            Posición de la hormiga, para eliminar columnas que sean redundantes

        Notes
        -------
        Cada vez que se elimina una columna del path de la hormiga, se verifica que la solución
        dada por el nuevo path, siga siendo factible. Si no es factible, entonces se prueba con la
        siguiente columna del path, y así sucesivamente, hasta iterar sobre todas las columnas.
        """

        # Calculamos la freceuncia del path de la mejor hormiga (dada por position)
        self._objAntColony.calculateFrecPosition(position)

        # Obtenemos la frecuencia de filas que son cubiertas por columnas
        # por ej, 4 [2 4 6 7] significa que hay 4 columnas (2,4,6,7) que cubren dicha fila
        rows = self._objAntColony.getFrecPosition(position)

        # ordenamos la frecuencia de filas por índices (no tocamos la lista rows original)
        list_order = self.sortedIndexList(rows, True)

        # Obtenemos la frecuencia de cada columna. Es decir cuantas veces aparece la columna en list_order
        colum, counter_cols = np.unique(
            self.flatList(self._objAntColony.getObjColsFrecPathPositon(position), 2),
            return_counts=True,
        )

        # Ordenamos de manera descendente
        list_order_columns = self.sortedIndexList(counter_cols, False)

        path = self._objAntColony.getPathPosition(position)

        for i in range(len(colum)):

            if colum[i] in path and self.canDeleColumns(colum[i], position):

                del path[path.index(colum[i])]

                self._objAntColony.getAntObject(position).setPath(path)

    def canDeleColumns(self, col, position):
        """Determina si una columna puede ser eliminada del path y este siga siendo factible.

        Parameters
        ----------

        col : int [0, cant_cols]
        ---------
            Posicion de la columna a eliminar.
        position : int [0, number_of_ants]
        --------------
            Posicion de la hormiga a la que se le hara la comprobacion.

        Return
        ------
            True si se puede eliminar la columna del path sin que deje de ser factible, False en caso contrario.

        """

        flag = False
        colum = []
        colum.append(col)

        complement = list(
            set(self._objAntColony.getPathPosition(position)) - set(colum)
        )
        temp = np.unique(
            self.flatList(self._objSCPInfo.getRowsCovered_V3(complement), 2)
        )

        if len(temp) == self._objSCPInfo.getNbrOfRows():
            flag = True

        return flag

    def applyLocalSearch_V1(self, position):
        """Busca mejorar la solución de una determinada hormiga, realizando una búsqueda local.
        Para ello, se ordenan las columnas de la solución de menor a mayor (coste) y luego se
        calcula, cuáles es el vecindario a explorar (es decir, las columnas, que quedan fuera
        de la solución). Una vez que se detetermina el vecindario, se procede a realizar intercambios
        de columnas (se sacan aleatoriamente k-columnas de la solución actual, y se las reemplazan
        por k-columnas del vecindario). Luego, se establece si la nueva solución es factible.

        Si la solución no es factbile con un determinado k, entonces se intenta hacer factible esa
        solución j-veces, si en las j-veces no se obtuvo factibilidad, entonces incrementa el valor
        de k.

        Si la solución es factible, entonces se compara con la solución de la hormiga dada
        por (position), y luego, si la solución difere de un cierto % del valor, entonces se actualiza
        el path y se sigue explorando y aplicando la búsqueda local sobre el nuevo path.

        Parameters
        ----------
        position : int [0, number_of_ants].
        ---
            Posición de la hormiga para realiar una búsqueda local a partir de su path y
            así poder mejorar la solución.

        Notes
        -----
        El % en cada iteración se decrementa en la mitad, para que solo haya intercambios de columnas
        cuando la solución sea cada vez mejor.
        """

        self.deleteRedudant(position)

        # obtengo el mejor valor de currOF hasta el momento (dado por la mejor hormiga)
        currOF = self._objAntColony.getOFValue(position)

        # seteo k = 1, para el número de intercambio de columnas
        k = 1

        # Obtengo las columnas que están dentro de la solución dada por la mejor hormiga
        colums_inside_solution = self._objAntColony.getPathPosition(position)

        # Obtengo el vecindario de soluciones, aquellas columnas que quedan fuera de la solución (dada por la mejor hormiga)
        list_order = self.getCostIndexOutsidePath(colums_inside_solution)

        # Creo una lista temporal que va a contener las columnas intercambiadas
        new_colums_solution = []
        new_currOF = 0.0
        index = []
        flag = True
        j = 0
        size_path = len(colums_inside_solution)

        # Vamos a realizar: size_path/3 intercambios de columnas
        while k < (size_path / 3):
            # Intercambiamos las n-columnas. Se usa el método random.sample para obtener muestras aleatorias únicas dentro de las
            # columnas que están en la solución, como las que están fuera de la solución.
            # El método exchangeColumns recibe como parámetro,
            #   1) el path de la mejor solución,
            #   2) las columnas a intercambiar de la solución original,
            #   3) y las columnas a intercambiar que están fuera de la solución.

            new_colums_solution, index = self._objAntColony.exchangeColumns(
                colums_inside_solution,
                random.sample(colums_inside_solution, k),
                random.sample(list_order[0 : int(len(list_order) / 3)], k),
            )

            # si la solución es factible
            if self.getFeasibility(
                currOF, position, index, colums_inside_solution, new_colums_solution
            ):

                # obtenemos el nuevo currOF de la nueva solución
                new_currOF = self._objAntColony.getOFValue(position)

                # Preguntamos cuál es el % de diferencia entre currOF y la nueva solución
                # si la diferencia es mínima (en este caso del 20% o 40%) entonces actualizamos
                # el path, y continuámos intercambiando columnas a partir de este path.
                if self.getPercentDiffCurrOf(currOF, new_currOF) <= self._percentage:

                    self.setPercent()
                    colums_inside_solution = new_colums_solution
                    list_order = self.getCostIndexOutsidePath(colums_inside_solution)

            else:

                flag = True
                j = 0

                # Intenta int(len(list_order)/2) veces volver fatible el nuevo path, si no lo logra
                # deja el viejo path factible
                while flag and j < int(len(list_order) / 2):
                    new_colums_solution, index = self._objAntColony.exchangeColumns(
                        colums_inside_solution,
                        random.sample(colums_inside_solution, k),
                        random.sample(list_order[0 : int(len(list_order) / 3)], k),
                    )

                    if self.getFeasibility(
                        currOF,
                        position,
                        index,
                        colums_inside_solution,
                        new_colums_solution,
                    ):

                        new_currOF = self._objAntColony.getOFValue(position)

                        if (
                            self.getPercentDiffCurrOf(currOF, new_currOF)
                            <= self._percentage
                        ):

                            self.setPercent()
                            colums_inside_solution = new_colums_solution
                            list_order = self.getCostIndexOutsidePath(
                                colums_inside_solution
                            )

                        flag = False
                    j += 1
            k += 1

    def isInfoLoaded(self):
        response = False

        if (
            self.getAlpha() > 0
            and self.getBeta() > 0
            and self.getRho() > 0
            and self.getInitialValue() > 0
            and self.getQ0() > 0
            and self.getNbrOfIters() > 0
            and self.getNbrOfAnts() > 0
            and self.getInstanceDir() != ""
            and self.getFilename() != ""
            and self.getResultDir() != ""
        ):
            response = True

        return response

    def solveProblem(self):

        if self.isInfoLoaded():

            self._objPheromone = clsPheromone(
                self._initialValue, self._objSCPInfo.getNbrOfCols(), self._invalidValue
            )

            self._objAntColony = clsAntColony(
                self.getNbrOfAnts(),
                self.getAlpha(),
                self.getBeta(),
                self.getRho(),
                self.getQ0(),
                self._objSCPInfo,
                self._objPheromone,
                self._invalidValue,
                self._infiniteValue,
            )
            # instancio la colonia

            nbrOfSteps = self._objSCPInfo.getNbrOfCols()

            for iter in range(self.getNbrOfIters()):

                print(f"ACO Iter {iter+1} of {self._iters}")
                self._tempCurrOF = self.getBestOFValue()

                self.setTime(time.time())

                for step in range(nbrOfSteps):
                    if step == 0:
                        self._objAntColony.startPaths()
                        # debo generar inicio de camino de las hormigas

                    [
                        self._objAntColony.selectNextNeighbor(k)
                        for k in range(self.getNbrOfAnts())
                    ]

                self._currOF = self._infiniteValue
                self._currPos = self._invalidValue

                for k in range(self.getNbrOfAnts()):
                    self._objAntColony.calculateOFValue(k)
                    currOF = self._objAntColony.getOFValue(k)

                    if currOF < self._currOF:
                        self._currOF = currOF
                        self._currPos = k

                self.applyLocalSearch_V1(self._currPos)
                # aplico LS a la mejor hormiga de la iteracion

                self._objAntColony.updatePheromone(self._currPos)

                for i in range(int(self._objAntColony.getNbrOfAnts() / 2)):
                    self._objAntColony.updatePheromone(i)
                # actualiza pheromone la mejor hormiga

                currOF = self._objAntColony.getOFValue(self._currPos)

                if currOF < self.getBestOFValue():
                    self._tempCurrOF = currOF
                    self._counterEqualSol = 0

                    self.setBestOFValue(currOF)
                    self._objAntColony.updateBestAnt(self._currPos)

                if self._tempCurrOF == self.getBestOFValue():

                    self._counterEqualSol += 1

                    if self._counterEqualSol > 10:
                        # metodo para salir del estancamiento
                        self._counterEqualSol = 0
                        self._tempCurrOF = 0
                        self.getOutStagnation(self._currPos)

                self.saveSolution()

                self._objAntColony.restartInformation()

            if self._objBestSolutions.getSize() > 0:
                print("Lista de mejores soluciones")
                for x in range(self._objBestSolutions.getSize()):
                    print(
                        f"Solution {x} = {np.array(self._objBestSolutions.getValueAtPos(x))}"
                    )

        else:
            print(
                "Error clsACOCSP solveProblem, Algún parámetro no se cargó correctamente"
            )

    def saveSolution(self):
        """Guarda los mejores resultados por corrida.

        Notes
        -----
        Se guandan los path de las soluciones que esten a un 10% de la solucion optima (opSol*1.1)
        en un archivo csv llamado optimalSol.

        Guarda los path en una estructura para utilizar en el metodo getOutStagnation(position)
        para salir de un estancamiento
        """

        try:
            solutions = pd.read_csv(self.getInstanceDir() + "optimalSol.csv", sep=";")
            instance = int("".join([s for s in self.getInstanceName() if s.isdigit()]))

            optimalOF = solutions[solutions["Problem"] == instance].to_numpy()[0][1]
            currOF = self._objAntColony.getOFValue(self._currPos)
            difOptimalOF = ((currOF - optimalOF) * 100) / optimalOF

            print(
                f"CurrentOF: {currOF} | BestOF: {self.getBestOFValue()} | Optimal {optimalOF} | difOptimal: {difOptimalOF}"
            )

            if difOptimalOF <= 10:
                ruta = str(
                    self.getResultDir() + "sol" + self.getInstanceName() + ".csv"
                )

                self._objBestSolutions.addValue(
                    self._objAntColony.getPathPosition(self._currPos)
                )

                data = [
                    sorted(self._objAntColony.getPathPosition(self._currPos)),
                    [round(currOF, 3)],
                    [round(difOptimalOF, 3)],
                    [time.time() - self.getTime()],
                ]
                
                df = pd.DataFrame(data)
                df.to_csv(ruta, mode="a", sep=";", header=False, index=False)

                print(f"Solución añadida al archivo de resultados")

        except IOError:
            print("Error clsACOCSP saveSolution.")

    def getOutStagnation(self, position):
        """Busca salir del estancamiento de un óptimo local de la búsqueda.

        Parameters
        ----------
        position : int [0, number_of_ants].
        ---
            Posición de la hormiga para luego setear su path,
            y así poder salir del estancamiento.

        Notes
        -----
        Sí solo hay hasta el momento un solo path en la lista de mejores soluciones, entonces el método
        genera una nueva solución a partir de ese path partido a la mitad y tomando elementos aleatorios.
        """

        if self._objBestSolutions.getSize() != 0:
            newAnt = clsAnt(
                self._alpha,
                self._beta,
                self._rho,
                self._Q0,
                self._objSCPInfo,
                self._objPheromone,
                self._infiniteValue,
                self._invalidValue,
            )

            if self._objBestSolutions.getSize() == 1:

                newAnt.setPath(self._objBestSolutions.getValueAtPos(0))
                newAnt.calculateFrec()

                # Obtenemos la frecuencia de cada columna. Es decir cuantas veces aparece la columna en list_order
                colum, counter_cols = np.unique(
                    self.flatList(newAnt.getObjColsFrecPath(), 2), return_counts=True
                )

                # Ordenamos de manera descendente
                list_order_columns = self.sortedIndexList(counter_cols, True)
                new_path = [colum[list_order_columns[i]] for i in range(len(colum))]

                # divido a la mitad el path de la hormiga y luego eligo k=len(new_path)/2 columnas aleatorias
                # para construir un nuevo path (obtener una nueva solución)
                new_path = random.sample(new_path, k=int(len(new_path) / 2))

                # Seteamos el nuevo path a la nueva hormiga
                newAnt.setPath(new_path)
                # Recalculamos cuáles son las filas cubiertas por este nuevo path
                newAnt.recalculateRowsCovered()

                # Iteramos hasta que el path(solución), de una solución factible, es decir, que el path,
                # cubra todas las filas
                while not newAnt.pathIsBuilt():
                    newAnt.selectNextNeighbor()

                # Calculamos el valor de currOF,
                newAnt.calculateOFValue()

                print(f"Saliendo del estancamiento, currOF: {newAnt.getOFValue()}")

            else:
                uniqueCols = []

                allCols = self._objBestSolutions.getList()
                allCols, counter_cols = np.unique(
                    self.flatList(allCols, 2), return_counts=True
                )

                [
                    uniqueCols.append(allCols[t])
                    for t in range(len(allCols))
                    if counter_cols[t] == 1
                ]

                newAnt.setPath(uniqueCols)
                newAnt.recalculateRowsCovered()

                while not newAnt.pathIsBuilt():
                    newAnt.selectNextNeighbor()

            self._objAntColony.setPaths(newAnt.getPathList(), position)
