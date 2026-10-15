def promedio(notas):
    suma = 0
    for nota in notas:
        suma += nota
    return suma / len(notas)
