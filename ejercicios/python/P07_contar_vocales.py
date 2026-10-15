def contar_vocales(s):
    c = 0
    for x in s.lower():
        if x in "aeiou":
            c += 1
    return c
