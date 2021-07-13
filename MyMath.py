SIGNIFICANT_DEZ = 3

def my_round(x, significant_dez = SIGNIFICANT_DEZ):
    return round(x, significant_dez)

def my_round_complex(x):
    return complex(my_round(x.real), my_round(x.imag))

def my_complex_to_str(x):
    real = str(int(x.real)) if int(x.real)==x.real else None
    imag = str(int(x.imag)) if int(x.imag)==x.imag else None
    if imag:
        if imag == '1':
            imag = ''
        elif imag == '-1':
            imag = '-'
    x = my_round_complex(x)
    if real is None:
        real = str(x.real)
    if imag is None:
        imag = str(x.imag)
    if imag == '0':
        return real
    elif real == '0':
        return imag + "i"
    else:
        if x.imag > 0:
            return real + "+" + imag + "i"
        else:
            return real + "-" + imag[1:] + "i"

def my_int_to_qubits(n, qubit_count):
    string = str(bin(n))[2:]
    while len(string) < qubit_count:
        string = "0" + string
    return string