import os
import sys
from analizador import analizar_codigo, AnalizadorSimplificadoCPP

def main():
    # Configurar la codificación de salida estándar a UTF-8
    sys.stdout.reconfigure(encoding='utf-8')

    # Leer el contenido de programa.cpp
    ruta_archivo_cpp = "programa.cpp"
    if not os.path.exists(ruta_archivo_cpp):
        print(f"Archivo '{ruta_archivo_cpp}' no encontrado.")
        return

    with open(ruta_archivo_cpp, 'r', encoding='utf-8') as f:
        codigo = f.read()

    # Analizar el código usando la función de analizador.py
    tokens = analizar_codigo(codigo)

    # Imprimir los tokens en formato de tabla
    print("{:<20} {:<30} {:<10}".format("Tipo", "Valor", "Línea"))
    print("-" * 60)
    for tipo_token, valor_token, numero_linea in tokens:
        print("{:<20} {:<30} {:<10}".format(tipo_token, valor_token, numero_linea))

    # Analizador Sintáctico
    analizador = AnalizadorSimplificadoCPP(tokens)
    try:
        analizador.analizar_programa()
        print("\n¡Análisis sintáctico completado con éxito!")
    except SyntaxError as e:
        print("\n¡El análisis sintáctico ha fallado!")  


if __name__ == "__main__":
    main()