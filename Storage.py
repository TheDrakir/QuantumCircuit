from math import sqrt

from Quantum import Quantum
from LinearTransformation import LinearTransformation



class Storage:    
    def __init__(self):
        self._constants = {}
        self._variables = {}

    def __getitem__(self, key):
        if key in self._constants:
            return self._constants[key]
        else:
            return self._variables[key]

    def __setitem__(self, key, value):
        self._variables[key] = value

    def remove(self, key):
        if key in self._variables:
            del self._variables[key]

    def createConstant(self, constant):
        self._constants[constant.name] = constant
        return constant


strg = Storage()

ZERO = strg.createConstant(Quantum([1, 0], "0"))
ONE = strg.createConstant(Quantum([0, 1], "1"))
PLUS = strg.createConstant(1/sqrt(2) * Quantum([1, 1], "+"))
MINUS = strg.createConstant(1/sqrt(2) * Quantum([1, -1], "-"))
PLUSI = strg.createConstant(1/sqrt(2) * Quantum([1, 1j], "+i"))
MINUSI = strg.createConstant(1/sqrt(2) * Quantum([1, -1j], "-i"))

X = strg.createConstant(LinearTransformation([[0, 1], [1, 0]], "X()"))
Y = strg.createConstant(LinearTransformation([[0, -1j], [1j, 0]], "Y()"))
Z = strg.createConstant(LinearTransformation([[1, 0], [0, -1]], "Z()"))
H = strg.createConstant(1/sqrt(2) * LinearTransformation([[1, 1], [1, -1]], "H()"))
CNOT = strg.createConstant(LinearTransformation([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], "CNOT()"))