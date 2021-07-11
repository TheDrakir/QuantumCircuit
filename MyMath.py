SIGNIFICANT_DEZ = 4

def myRound(x):
    return round(x, SIGNIFICANT_DEZ)

def myRoundComplex(x):
    return complex(myRound(x.real), myRound(x.imag))

def myComplexToStr(x):
    x = myRoundComplex(x)
    if x.imag == 0:
        return str(x.real)
    elif x.real == 0:
        return str(x.imag) + "j"
    else:
        return str(x)

def myIntToQBits(n, qBitCount):
    string = str(bin(n))[2:]
    while len(string) < qBitCount:
        string = "0" + string
    return string