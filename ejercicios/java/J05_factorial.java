class Factorial {
    static long factorial(int n) {
        long res = 1;
        int i = 2;
        while (i <= n) {
            res = res * i;
            i++;
        }
        return res;
    }
}
