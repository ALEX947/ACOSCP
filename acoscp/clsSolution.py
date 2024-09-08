class clsSolution:
    def __init__(self, cols, invalidValue):
        self.resetSolution()
        self._cols = cols
        self._invalidValue = invalidValue

    def resetSolution(self):
        self._myList = []

    def getList(self):
        return self._myList

    def getSize(self):
        return len(self._myList)

    def addValue(self, value):
        if self.getSize() < self._cols:
            self._myList.append(value)
        else:
            print("Error clsSolution addValue. Tamanio excedido")

    def setList(self, list):
        self._myList = list

    def addValueAtPos(self, position, value):

        if 0 <= position < self.getSize():
            self._myList[position].append(value)
        else:
            print(f"Error clsSolution addValueAtPos. Posición {position} no existe.")

    def addColumn(self, column):
        if column not in self._myList:
            if self.getSize() < self._cols:
                self._myList.append(column)
            else:
                print("Error clsSolution addColumn. Tamanio excedido")
        else:
            print(f"Error clsSolution addColumn. Posición {column} ya existe.")

    def delColumn(self, column):
        if column in self._myList:
            position = self._myList.index(column)
            del self._myList[position]
        else:
            print(f"Error clsSolution delColumn. Posición {column} no existe.")

    def getValueAtPos(self, position):
        value = self._invalidValue
        if 0 <= position < self.getSize():
            value = self._myList[position]
        else:
            print(f"Error clsSolution getValueAtPos. Posición {position} no existe.")

        return value

    def setValueAtPos(self, position, newValue, checkValue=True):
        if 0 <= position < self.getSize():
            if checkValue:
                if 0 <= newValue < self._cols:
                    self._myList[position] = newValue

                else:
                    print(f"Error clsSolution setValueAtPos. {newValue} valor incorrecto.")
            else:
                self._myList[position] = newValue

        else:
            print(f"Error clsSolution setValueAtPos. Posición {position} no existe.")

    def isInside(self, element):
        response = False

        if len(self._myList) > 0:
            if element in self._myList:
                response = True
        else:
            print("Error clsSolution isInside, lista vacia.")

        return response

    def initList(self):
        for i in range(self._cols):
            self._myList.append(0)

    def initListList(self):
        for i in range(self._cols):
            self._myList.append([])

    def incValueAtPos(self, position):
        if 0 <= position < self.getSize():
            self._myList[position] += 1
        else:
            print(f"Error clsSolution incValueAtPos. Posición {position} no existe.")
