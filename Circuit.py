import json
from os import stat

from Quantum import Quantum
from LinearTransformation import LinearTransformation
from Base import Base
from Storage import *


# set file name of which input data will be read
INPUT_FILE_NAME = "to_back.json"


class Circuit:
    '''Defines a circuit of linear transformations of qubits.'''

    def __init__(self, qubit_count, primitive_linear_transformations):
        self.qubit_count = qubit_count
        self.dimension = 2**qubit_count
        self.primitive_linear_transformations = primitive_linear_transformations
        self.set_linear_transformations()

    def set_linear_transformations(self):
        self.linear_transformations = []
        for linear_transformation, qubit_indizes in self.primitive_linear_transformations:
            self.linear_transformations += [linear_transformation.fill_qubits(self.qubit_count, qubit_indizes)]

    def gate(self):
        circuitLinear_transformation = LinearTransformation.identity(self.dimension)
        for linear_transformation in self.linear_transformations:
            circuitLinear_transformation = linear_transformation @ circuitLinear_transformation
        return circuitLinear_transformation

    @staticmethod
    def deserialize_gates():
        # Das Auslesen aus der json-Datei funktioniert nur für 1-dimensionale gates.
        with open(INPUT_FILE_NAME, "r") as f:
            content = json.load(f)
            num_qubits = 3 #content["qubits"]
            primitive_linear_transformations = []
            for gate_type, coords in content["gates"].items():
                for coord in coords:
                    primitive_linear_transformations += [Circuit.gate_to_linear_transformation(gate_type, coord)]
        primitive_linear_transformations.sort(key = lambda x: x[1])
        primitive_linear_transformations = [x[0] for x in primitive_linear_transformations]
        return Circuit(num_qubits, primitive_linear_transformations)

    @staticmethod
    def gate_to_linear_transformation(gate_type, coord):
        qubits = coord[0]
        slot = coord[1]
        linear_transformation = strg[gate_type].linear_transformation
        return [(linear_transformation, qubits), slot]

    def __str__(self):
        string = str(self.qubit_count) + "\n"
        for linear_transformation in self.linear_transformations:
            string = string + str(linear_transformation) + "\n"
        return ""




# LT_INV_CX = Circuit(2, [(LT_H, [1]), (LT_CZ, [0, 1]), (LT_H, [1])]).gate()

# print(LT_CZ)
# print(LT_INV_CX)



P = Circuit.deserialize_gates()
print(P.gate())