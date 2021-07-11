from Quantum import Quantum
from LinearTransformation import LinearTransformation
from Base import Base
from Storage import *


class Circuit:
    def __init__(self, qBitCount, primitiveLinearTransformations):
        self.qBitCount = qBitCount
        self.dimension = 2**qBitCount
        self.primitiveLinearTransformations = primitiveLinearTransformations
        self.setLinearTransformations()

    def setLinearTransformations(self):
        self.linearTransformations = []
        for linearTransformation, qBitIndizes in self.primitiveLinearTransformations:
            self.linearTransformations += [linearTransformation.fillQbits(self.qBitCount, qBitIndizes)]

    def composedLinearTransformation(self):
        circuitLinearTransformation = LinearTransformation.identity(self.dimension)
        for linearTransformation in self.linearTransformations:
            circuitLinearTransformation = linearTransformation @ circuitLinearTransformation
        return circuitLinearTransformation
