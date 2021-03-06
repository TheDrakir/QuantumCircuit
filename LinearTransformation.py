from Quantum import Quantum
from MyMath import my_complex_to_str, my_int_to_qubits, my_complex_to_latex


class LinearTransformation:
    '''Defines a linear transformation from an n-qubit vectorspace to itself.'''

    def __init__(self, array, name = None):
        self.array = array
        self.name = name
        self.validate()
        self.set_qubit_count()
        

    def validate(self):
        for row in self.array:
            if len(row) != len(self):
                raise ValueError("Matrix is not a square Matrix.")
        i = 1
        while 2**i < len(self):
            i += 1
        if 2**i != len(self):
            raise ValueError("Size of input space is not a power of two.")
    
    def _is_unitary(self):
        # import must be here due to circular import stuff
        # TODO: restructure code
        from Base import OrthoNormalBase
        qubits = []
        for j in range(len(self.array)):
            qubits.append(Quantum([self.array[i][j] for i in range(len(self.array))]))
        ortho_normal_base = OrthoNormalBase(qubits)
        return ortho_normal_base.is_ortho_normal_base()


    def set_qubit_count(self):
        self.qubit_count = 0
        while 2**self.qubit_count < len(self):
            self.qubit_count += 1

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
            raise ValueError("Matrices have wrong shape.")
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

    def fill_qubits(self, n, indizes):
        if 2**n < len(self):
            raise ValueError("Linear transformation has length of more than 2**n already.")
        new_linear_transformation = LinearTransformation.zero(2**n)
        ind_map = []
        rev_ind_map = {}
        for ind in range(len(self)):
            string = my_int_to_qubits(ind, self.qubit_count)
            newInd = 0
            for exp in range(self.qubit_count):
                if string[-exp-1] == "1":
                    newInd += 2**indizes[exp]
            ind_map += [newInd]
            rev_ind_map[newInd] = ind
        new_ind_map = []
        for ind in range(len(new_linear_transformation)):
            string = my_int_to_qubits(ind, new_linear_transformation.qubit_count)
            for exp in range(len(string)):
                if len(string) - exp - 1 in indizes:
                    string = string[:exp] + "0" + string[exp + 1:]  
            new_ind_map.append(int(string, 2))
        for newJ in range(len(new_linear_transformation)):
            for i in range(len(self)):
                new_linear_transformation.array[ind_map[i] + new_ind_map[newJ]][newJ] = self.array[i][rev_ind_map[newJ - new_ind_map[newJ]]]
        return new_linear_transformation

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
                string += f"{my_complex_to_str(num)!s:<10} "
            string += end
        return string

    def probabilities(self):
        return [[(abs(value))**2 for value in row] for row in self.array]

    def latex(self):
        string = "\\begin{pmatrix}"
        for row in self.array:
            for element in row:
                string += my_complex_to_latex(element) + " & "
            string = string[:-2] + "\\\\ "
        string = string[:-3] + "\\end{pmatrix}"
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