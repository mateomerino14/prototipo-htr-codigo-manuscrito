class Vocales {
    static int contar(String s) {
        int c = 0;
        for (char x : s.toLowerCase().toCharArray()) {
            if ("aeiou".indexOf(x) != -1) {
                c++;
            }
        }
        return c;
    }
}
