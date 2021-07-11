from math import sqrt
import numpy as np

from Quantum import Quantum
from MyMath import myComplexToStr, myIntToQBits

class LinearTransformation:
    def __init__(self, array, name = None):
        self.array = array
        self.name = name
        self.validate()
        self.setQBitCount()

    def validate(self):
        for row in self.array:
            if len(row) != len(self):
                raise ValueError("Matrix is not a square Matrix.")
        i = 1
        while 2**i < len(self):
            i += 1
        if 2**i != len(self):
            raise ValueError("Size of input space is not a power of two.")

    def setQBitCount(self):
        self.qBitCount = 0
        while 2**self.qBitCount < len(self):
            self.qBitCount += 1

    def __len__(self):
        return len(self.array)

    def __rmul__(self, other):
        if isinstance(other, (int, complex, float)):
            return LinearTransformation([[element * other for element in row] for row in self.array])
        else:
            return NotImplemented
    
    def __pos__(self):
        return LinearTransformation([row.copy() for row in self])
    

    def __mul__(self, other):
        if isinstance(other, Quantum):
            vector = [None] * len(other)
            for i, row in enumerate(self.array):
                vector[i] = sum(row[j] * other.vector[j] for j in range(len(row)))
            return Quantum(vector)
        else:
            return NotImplemented

    def __matmul__(self, other):
        if len(self) != len(other):
            raise ValueError("Matricies have wrong shape.")
        newArray = []
        for i in range(len(self)):
            row = []
            for j in range(len(other)):
                value = 0
                for k in range(len(self)):
                    value += self.array[i][k] * other.array[k][j]
                row += [value]
            newArray += [row]
        return LinearTransformation(newArray)

    def fillQbits(self, n, indizes):
        if 2**n < len(self):
            raise ValueError("Linear transformation has length of more than 2**n already.")
        newLinearTransformation = LinearTransformation.zero(2**n)
        indMap = []
        revIndMap = {}
        for ind in range(len(self)):
            string = myIntToQBits(ind, self.qBitCount)
            newInd = 0
            for exp in range(self.qBitCount):
                if string[-exp-1] == "1":
                    newInd += 2**indizes[exp]
            indMap += [newInd]
            revIndMap[newInd] = ind
        newIndMap = []
        for ind in range(len(newLinearTransformation)):
            string = myIntToQBits(ind, newLinearTransformation.qBitCount)
            for exp in range(len(string)):
                if len(string) - exp - 1 in indizes:
                    string = string[:exp] + "0" + string[exp + 1:]
            newIndMap.append(int(string, 2))
        for newJ in range(len(newLinearTransformation)):
            for i in range(len(self)):
                newLinearTransformation.array[indMap[i] + newIndMap[newJ]][newJ] = self.array[i][revIndMap[newJ - newIndMap[newJ]]]
        return newLinearTransformation

    def __str__(self):
        string = ""
        for i, row in enumerate(self.array):
            if i == 0:
                start, end = "/", "\\\n"
            elif i == len(self) - 1:
                start, end = "\\", "/\n"
            else:
                start, end = "|", "|\n"
            string += start
            for num in row:
                string += f"{myComplexToStr(num)!s:<10} "
            string += end
        return string

    @staticmethod
    def zero(n):
        return LinearTransformation([[0] * n for _ in range(n)])

    @staticmethod
    def identity(n):
        id = LinearTransformation.zero(n)
        for i in range(n):
            id.array[i][i] = 1 
        return id