from math import floor

SIGNIFICANT_DEZ = 3
EPSILON = 0.00001

def my_round(x, significant_dez = SIGNIFICANT_DEZ):
    return round(x, significant_dez)

def my_round_complex(x, d = SIGNIFICANT_DEZ):
    return complex(my_round(x.real, d), my_round(x.imag, d))

def my_complex_to_str(x):
    real = str(int(x.real)) if int(x.real)==x.real else None
    imag = str(int(x.imag)) if int(x.imag)==x.imag else None
    x = my_round_complex(x)
    if not real:
        real = str(x.real)
    if not imag:
        imag = str(x.imag)
    if imag == '0':
        return real
    elif real == '0':
        return imag + "i"
    else:
        if x.imag > 0:
            return real + "+" + imag+ "i"
        else:
            return real+ "-" + imag + "i"

def my_complex_to_latex(x):
    real = str(int(x.real)) if int(x.real)==x.real else None
    imag = str(int(x.imag)) if int(x.imag)==x.imag else None
    if not real:
        real = str(x.real)
    if not imag:
        imag = str(x.imag)
    real = check_latex(real)
    imag = check_latex(imag)
    if imag == '0':
        return real
    elif real == '0':
        return imag + "\\i"
    else:
        if x.imag > 0:
            return real + "+" + imag+ "\\i"
        else:
            return real+ "-" + imag + "\\i"

def check_latex(x):
    x = float(x)
    if x - EPSILON < floor(x + 0.5) < x + EPSILON:
        return str(floor(x + 0.5))
    string = ""
    if x < 0:
        string = "-"
    y = 1 / x
    if x**2 - EPSILON < floor(x**2 + 0.5) < x**2 + EPSILON:
        n = floor(x**2 + 0.5)
        string += "\\sqrt{" + str(n) + "}"
        return string
    if y**2 - EPSILON < floor(y**2 + 0.5) < y**2 + EPSILON:
        n = floor(y**2 + 0.5)
        string += "\\frac{1}{\\sqrt{" + str(n) + "}}"
        return string
    return str(my_round(x))




def my_int_to_qubits(n, qubit_count):
    string = str(bin(n))[2:]
    while len(string) < qubit_count:
        string = "0" + string
    return string