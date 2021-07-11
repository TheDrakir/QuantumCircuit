from math import sqrt

from Quantum import Quantum
from Storage import *


class Base:
    '''Defines a base of an n-dimensional qubit space.'''

    def __init__(self, vector, name = None):
        self.vector = vector
        self.name = name
        if not self.isBase:
            raise Exception("This is not a base.")

    # isBase rules out some but not all non-base objects
    def isBase(self):
        k = len(self.vector[0])
        if 2**k != len(self.vector):
            return False
        for base_element in self.vector:
            if len(base_element) != k:
                return False
        return True

    def __str__(self):
        string = ""
        for base_element in self.vector:
            string += str(base_element) + ", "
        return "(" + string[:-2] + ")"


class OrthoNormalBase(Base):
    '''Defines an orthonormal base.'''

    def is_ortho_normal_base(self):
        for i1, base_element1 in self.vector:
            if abs(base_element1) != 1:
                return False
            for i2, base_element2 in self.vector[i1+1:]:
                if base_element1 * base_element2 != 0:
                    return False
        return True

    @staticmethod
    def std_base(qBitCount):
        if qBitCount == 1:
            return OrthoNormalBase([ZERO, ONE])
        else:
            last = OrthoNormalBase.stdBase(qBitCount - 1)
            return OrthoNormalBase([ZERO @ element for element in last.vector]
                                   + [ONE @ element for element in last.vector])

    @staticmethod
    def bellBase():
        return Base([1/sqrt(2)*(ZERO @ ZERO + ONE @ ONE),
                     1/sqrt(2)*(ZERO @ ZERO - ONE @ ONE),
                     1/sqrt(2)*(ZERO @ ONE + ONE @ ZERO),
                     1/sqrt(2)*(ZERO @ ONE - ONE @ ZERO)])


