class Promedio {
    static double promedio(int[] notas) {
        int suma = 0;
        for (int i = 0; i < notas.length; i++) {
            suma += notas[i];
        }
        return (double) suma / notas.length;
    }
}
