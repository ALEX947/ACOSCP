import clsSolution as Solution


class clsSCPInfo:
    def __init__(self, invalidValue, infiniteValue):
        self._rows = 0
        self._cols = 0

        self._instanceDir = ""
        self._instanceName = ""
        self._myFile = None

        self._invalidValue = invalidValue
        self._infiniteValue = infiniteValue

        self._costList = None
        self._colList = None
        self._rowList = None

    def setInstanceDir(self, instanceDir):
        self._instanceDir = instanceDir

    def setInstanceName(self, instanceName):
        self._instanceName = instanceName

    def getFilename(self):
        return self._instanceDir + self._instanceName

    def getNbrOfCols(self):
        return self._cols

    def getNbrOfRows(self):
        return self._rows

    def readInstance(self):

        try:
            self._myFile = open(self.getFilename(), "r")

            line = self._myFile.readline()
            self._rows, self._cols = line.strip().split(" ")
            self._rows = int(self._rows)
            self._cols = int(self._cols)

            # Lista de costos
            self._costList = Solution.clsSolution(self._cols, self._invalidValue)

            # Lista de columnas y las filas que cubre
            self._colList = Solution.clsSolution(self._cols, self._invalidValue)

            # Lista de filas y las columnas que cubre
            self._rowList = Solution.clsSolution(self._rows, self._invalidValue)

            line = self._myFile.readline().strip().split(" ")

            while len(line) > 1:
                for i in range(len(line)):
                    self._costList.addValue(int(line[i]))

                line = self._myFile.readline().strip().split(" ")

            [self._rowList.addValue([]) for j in range(self._rows)]
            [self._colList.addValue([]) for j in range(self._cols)]

            nbrOfCoverings = int(line[0]) # Cantidad de columnas cubiertas por la linea i
            row = 0
            counter = 0
            
            while counter < nbrOfCoverings:
                line = self._myFile.readline().strip().split(" ")

                for j in range(len(line)):
                    self._rowList.addValueAtPos(row, int(line[j]) - 1)  # Col-1 porque en el archivo las col empiezan en 1
                    self._colList.addValueAtPos(int(line[j]) - 1, row)

                counter += len(line)

                if counter == nbrOfCoverings: # Se leyó la cantidad nbrOfCoverings de columnas
                    if row < self._rows - 1: # Aún no se leyeron las self._rows filas
                        line = self._myFile.readline().strip().split(" ")
                        nbrOfCoverings = int(line[0])
                        counter = 0
                        row += 1
                    else:
                        break
                        
            print(f"Instancia {self._instanceName} leida correctamente")

        except IOError:
            print("Error clsSCPInfo openFile. No existe el archivo")
            exit()

    def getColumnCost(self, position):
        cost = self._infiniteValue

        if 0 <= position < self._costList.getSize():
            cost = self._costList.getValueAtPos(position)
        else:
            print("Error clsSCPInfo getColumnCost, Posicion invalida")

        return cost

    def getIndexByPath(self, path):
        index_path_sol = []

        if len(path) > 0:
            [index_path_sol.append(path.index(path[i])) for i in range(len(path))]
        else:
            print("Error clsSCPInfo getIndexByPath. Path is null")

        return index_path_sol

    def getColumnCostV2(self, index):
        cost_list = []

        if len(index) > 0:
            [cost_list.append(self.getColumnCost(index[i])) for i in range(len(index))]
        else:
            print("Error clsSCPInfo getColumnCost. Index is null")

        return cost_list

    def getNbrOfRowsCovered(self, position):
        counter = self._invalidValue

        if 0 <= position < self._colList.getSize():
            counter = len(self._colList.getValueAtPos(position))

        else:
            print("Error clsSCPInfo getColumnCost, Posicion invalida")

        return counter

    def getRowsCovered(self, position):
        """Obtiene la lista de filas que cubre una columna. The

        Args:
                position (int): posición de la columna. The

        Returns:
                list: lista de filas cubiertas por la columna en position.
        """
        rowsCoveredList = []

        if 0 <= position < self._colList.getSize():
            rowsCoveredList = self._colList.getValueAtPos(position)
        else:
            print(f"Error clsSCPInfo getRowsCovered {position} posicion invalida")

        return rowsCoveredList

    # Recibe una lista de columnas del path de una hormiga.
    def getRowsCovered_V3(self, list_cols):
        rowsCoveredList = []
        size = len(list_cols)
        # Si el path no es nulo
        if size > 0:
            # Añadimos todas las filas cubiertas por cada columna del path a la lista, y se devuelve una lista de lista
            for i in range(size):
                rowsCoveredList.append(self.getRowsCovered(list_cols[i]))
        else:
            print("Error clsSCPInfo. Path null")

        return rowsCoveredList

    def getColumnCovered(self, position):
        """Obtiene la lista de columnas que cubren una determinada fila.

        Args:
                position (int): posición de la fila.x

        Returns:
                list: lista de columnas que cubren la fila en position.
        """
        temp = []
        if 0 <= position < self._rowList.getSize():
            temp = self._rowList.getValueAtPos(position)
        else:
            print("Error clsSCPInfo getColumnCovered len")
        return temp
