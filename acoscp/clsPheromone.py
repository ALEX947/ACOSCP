import clsSolution as Solution


class clsPheromone(Solution.clsSolution):
    def __init__(self, initialValue, cols, invalidValue):
        Solution.clsSolution.__init__(self, cols, invalidValue)

        # se le asigna un valor de feremona a cada camino
        self._initialValue = initialValue

        self.initialize()

    def initialize(self):
        [self._myList.append(self._initialValue) for i in range(self._cols)]
