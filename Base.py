from math import sqrt

from Quantum import Quantum
from Storage import *

class Base:
    def __init__(self, vector, name = None):
        self.vector = vector
        self.name = name
        if not self.isBase:
            raise Exception("This is not a base.")

    #isBase rules out some but not all non-base objects
    def isBase(self):
        k = len(self.vector[0])
        if 2**k != len(self.vector):
            return False
        for baseElement in self.vector:
            if len(baseElement) != k:
                return False
        return True

    def __str__(self):
        string = ""
        for baseElement in self.vector:
            string += str(baseElement) + ", "
        return "(" + string[:-2] + ")"

class OrthoNormalBase(Base):
    def isOrthoNormalBase(self):
        for i1, baseElement1 in self.vector:
            if abs(baseElement1) != 1:
                return False
            for i2, baseElement2 in self.vector[i1+1:]:
                if baseElement1 * baseElement2 != 0:
                    return False
        return True

    @staticmethod
    def stdBase(qBitCount):
        if qBitCount == 1:
            return OrthoNormalBase([ZERO, ONE])
        else:
            last = OrthoNormalBase.stdBase(qBitCount - 1)
            return OrthoNormalBase([ZERO @ element for element in last.vector] + [ONE @ element for element in last.vector])

    @staticmethod
    def bellBase():
        return Base([1/sqrt(2)*(ZERO @ ZERO + ONE @ ONE), 1/sqrt(2)*(ZERO @ ZERO - ONE @ ONE), 1/sqrt(2)*(ZERO @ ONE + ONE @ ZERO), 1/sqrt(2)*(ZERO @ ONE - ONE @ ZERO)])


