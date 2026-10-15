class Rectangulo {
    private double base;
    private double altura;

    Rectangulo(double base, double altura) {
        this.base = base;
        this.altura = altura;
    }

    double area() {
        return base * altura;
    }
}
