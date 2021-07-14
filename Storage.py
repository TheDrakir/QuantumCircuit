from math import sqrt

from Quantum import Quantum
from LinearTransformation import LinearTransformation
from GateType import GateType
import json
import sys, os


class Storage:
    '''Stores values.'''

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

    def _create_constant(self, constant):
        if hasattr(constant, "name"):
            self._constants[constant.name] = constant
        return constant


strg = Storage()


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

INPUT_FILE_NAME = strg._create_constant(resource_path("to_back.json"))
GATE_FILE_NAME = strg._create_constant(resource_path("gates.json"))



# define special qubits
ZERO = strg._create_constant(Quantum([1, 0], "0"))
ONE = strg._create_constant(Quantum([0, 1], "1"))
PLUS = strg._create_constant(1/sqrt(2) * Quantum([1, 1], "+"))
MINUS = strg._create_constant(1/sqrt(2) * Quantum([1, -1], "-"))
PLUSI = strg._create_constant(1/sqrt(2) * Quantum([1, 1j], "+i"))
MINUSI = strg._create_constant(1/sqrt(2) * Quantum([1, -1j], "-i"))

# define special linear transformations
LT_X = strg._create_constant(LinearTransformation([[0, 1], [1, 0]], "LT_X"))
LT_Y = strg._create_constant(LinearTransformation([[0, -1j], [1j, 0]], "LT_Y"))
LT_Z = strg._create_constant(LinearTransformation([[1, 0], [0, -1]], "LT_Z"))
LT_H = strg._create_constant(
    1/sqrt(2) * LinearTransformation([[1, 1], [1, -1]], "LT_H"))
LT_CNOT = strg._create_constant(LinearTransformation(
    [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], "LT_CNOT"))
LT_CZ = strg._create_constant(LinearTransformation(
    [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, -1]], "LT_CZ"))

# define colors
WHITE = strg._create_constant((255, 255, 255))
DARK = strg._create_constant((50, 50, 50))
BLACK = strg._create_constant((0, 0, 0))
GREY = strg._create_constant((200, 200, 200))
RED = strg._create_constant((219, 42, 42))
ORANGE = strg._create_constant((219, 163, 42))
GREEN = strg._create_constant((151, 219, 42))
TEAL = strg._create_constant((42, 219, 160))
CYAN = strg._create_constant((42, 219, 219))
BLUE = strg._create_constant((42, 89, 219))
PURPLE = strg._create_constant((148, 42, 219))
PINK = strg._create_constant((219, 42, 154))

# define gate types




GATE_TYPES = []
with open(GATE_FILE_NAME, "r") as f:
    data = json.load(f)
    for name,value in data.items():
        m = value['matrix']
        array = []
        for row in m:
            l = []
            array.append(l)
            for v in row:
                l.append(complex(v))
        c = bool(value['control'])
        g = GateType(name, tuple(value['color']), LinearTransformation(array), control=c)
        s = strg._create_constant(g)
        GATE_TYPES.append(s)


# H = strg._create_constant(GateType('H', RED, LT_H))
# X = strg._create_constant(GateType('X', ORANGE, LT_X))
# Y = strg._create_constant(GateType('Y', GREEN, LT_Y))
# Z = strg._create_constant(GateType('Z', TEAL, LT_Z))
# CNOT = strg._create_constant(GateType('+', CYAN, LT_CNOT, control=True))
# CZ = strg._create_constant(GateType('CZ', PINK, LT_CZ, control=True))
# GATE_TYPES = [H, X, Y, Z, CNOT, CZ]





def gate_types_to_json():
    d = {}
    for gate_type in GATE_TYPES:
        array = []
        for row in gate_type.linear_transformation.array:
            l = []
            array.append(l)
            for v in row:
                l.append(str(v))
        d[gate_type.name] = {"color": list(gate_type.color),
                             "matrix": array,
                             "control": int(gate_type.control)}
        with open(GATE_FILE_NAME, "w") as f:
            json.dump(d, f, indent=4)

