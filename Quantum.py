from math import acos, sin, pi, sqrt
from MyMath import my_round, my_complex_to_str, my_int_to_qubits
from cmath import phase


class Quantum:
    '''Defines an n qubits.'''

    def __init__(self, vector, name = None):
        self.vector = [complex(element) for element in vector]
        self.name = name
        self.setQBitCount()

    def setQBitCount(self):
        self.qBitCount = 0
        while 2**self.qBitCount < len(self):
            self.qBitCount += 1

    def __len__(self):
        return len(self.vector)

    def __getitem__(self, key):
        return self.vector[key]

    def __setitem__(self, key, value):
        self.vector[key] = value

    def __invert__(self):
        return Quantum([element.conjugate() for element in self.vector])

    def __rmul__(self, other):
        if isinstance(other, (int, complex, float)):
            return Quantum([element * other for element in self.vector])
        else:
            return NotImplemented

    def __add__(self, other):
        if len(self) == len(other):
            return Quantum([element + otherElement for element, otherElement in zip(self.vector, other.vector)])

    def __sub__(self, other):
        if len(self) == len(other):
            return Quantum([element - otherElement for element, otherElement in zip(self.vector, other.vector)])

    def __mul__(self, other):
        if isinstance(other, Quantum):
            return sum([conjElement * otherElement for conjElement, otherElement in zip((~self).vector, other.vector)])
        elif isinstance(other, (int, complex, float)):
            return other * self
        else:
            return NotImplemented
    
    def __neg__(self):
        return Quantum([-element for element in self.vector])
    
    def __pos__(self):
        return Quantum(self.vector[:])
        
    def __matmul__(self, other):
        prodVector = []
        for i in range(len(self) * len(other)):
            prodVector.append(self.vector[i // len(other)] * other.vector[i % len(other)])
        return Quantum(prodVector)
    
    def __abs__(self):
        return sqrt(abs(self * self))

    def probability(self, baseElement):
        return abs(self * baseElement)**2

    def normed(self):
        try:
            return 1 / abs(self) * self
        except:
            raise Exception("Cannot norm vector.")

    @staticmethod
    def initFromBase(vector, base):
        stdQuantum = Quantum([0]*len(vector))
        for element, baseElement in zip(vector, base.vector):
            stdQuantum += element * baseElement
        return stdQuantum

    @staticmethod
    def initFromSingleQubits(vector):
        singleQuantum = Quantum(vector[0])
        for qubit in vector[1:]:
            singleQuantum = Quantum(qubit) @ singleQuantum
        return singleQuantum

    def __str__(self):
        string = ""
        for i, scalar in enumerate(self.vector):
            if scalar != 0:
                string += my_complex_to_str(scalar) + " |" + my_int_to_qubits(i, self.qBitCount) + "〉+ "
        if len(string) < 2:
            return ""
        return string[:-2]

    def polarCoords(self):
        if len(self.vector) != 2:
            raise Exception("This is not a single QBit.")
        if self.vector[0] == 0:
            theta = pi
            phi = phase(self.vector[1])
        else:
            self = (abs(self.vector[0]) / self.vector[0]) * self
            theta = 2 * acos(self.vector[0].real)
            if self.vector[1] == 0:
                phi = 0
            else:
                phi = phase(self.vector[1] / sin(theta / 2))
        return my_round(theta), my_round(phi)