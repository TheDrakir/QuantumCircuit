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

    def gate(self):
        circuitLinearTransformation = LinearTransformation.identity(self.dimension)
        for linearTransformation in self.linearTransformations:
            circuitLinearTransformation = linearTransformation @ circuitLinearTransformation
        return circuitLinearTransformation


cZ = Circuit(2, [(H, [0]), (CNOT, [0, 1]), (H, [0])]).gate()
INV_CX = Circuit(2, [(H, [1]), (cZ, [0, 1]), (H, [1])]).gate()

print(cZ)
print(INV_CX)