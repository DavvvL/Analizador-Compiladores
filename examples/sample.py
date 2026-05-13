# Ejemplo de código para el analizador
# Este archivo demuestra las construcciones soportadas

x = 10
y = 3.14
nombre = "Hola Mundo"

def suma(a, b):
    resultado = a + b
    return resultado

def es_mayor(x, y):
    if x > y:
        print("x es mayor")
        return True
    else:
        print("y es mayor o igual")
        return False

z = suma(x, 5)
print(z)

while x > 0:
    x = x - 1

if es_mayor(z, y):
    print("Resultado correcto")
