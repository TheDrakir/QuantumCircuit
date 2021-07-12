SIGNIFICANT_DEZ = 4

def my_round(x, significant_dez = SIGNIFICANT_DEZ):
    return round(x, significant_dez)

def my_round_complex(x):
    return complex(my_round(x.real), my_round(x.imag))

def my_complex_to_str(x):
    x = my_round_complex(x)
    if x.imag == 0:
        return str(x.real)
    elif x.real == 0:
        return str(x.imag) + "j"
    else:
        return str(x)

def my_int_to_qubits(n, qubit_count):
    string = str(bin(n))[2:]
    while len(string) < qubit_count:
        string = "0" + string
    return string