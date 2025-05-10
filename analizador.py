# Importa la librería 're' para trabajar con expresiones regulares.
import re

# Función principal para analizar el código de entrada.
def analizar_codigo(codigo):
    # Conjunto de palabras clave a identificar como tokens.
    palabra_clave = {'int', 'if', 'while', 'else', 'for', 'float', 'return', 'char', 'void', 'using', 'namespace'}
    
    # Lista de operadores comunes en lenguajes de programación.
    operadores = [r'\+\+', r'--', r'==', r'!=', r'<=', r'>=', r'&&', r'\|\|', r'<<', r'>>',
                  r'\+', r'-', r'\*', r'/', r'%', r'=', r'<', r'>']
    
    # Conjunto de delimitadores (símbolos que separan declaraciones o expresiones).
    delimitadores = {r';', r',', r'\(', r'\)', r'\{', r'\}', r'\[', r'\]'}
    
    # Definición de tipos de tokens con su correspondiente patrón de búsqueda en regex.
    tipo_token = [
        ('NUMERO', r'\d+'),  # Detecta números enteros.
        ('IDENTIFICADOR', r'[A-Za-z_]\w*'),  # Detecta identificadores (variables, funciones, etc.).
        
        # Detecta operadores. Se ordenan de mayor a menor longitud para evitar conflictos en la detección.
        ('OPERADOR', r'|'.join(sorted(operadores, key=lambda x: -len(x)))),
        
        # Detecta delimitadores.
        ('DELIMITADOR', r'|'.join(delimitadores)),
        
        # Detecta cadenas encerradas entre comillas dobles.
        ('CADENA', r'"[^"]*"'),
        
        # Detecta líneas de preprocesador como '#include'.
        ('PREPROCESADOR', r'#\s*\w+'),
        
        # Detecta espacios y tabulaciones que deben ser ignorados.
        ('OMITIR', r'[ \t]+'),
        
        # Detecta saltos de línea para llevar un control de la línea actual.
        ('NUEVA_LINEA', r'\n'),
        
        # Detecta cualquier cosa que no coincida con lo anterior (errores o caracteres desconocidos).
        ('NO_COINCIDE', r'.'),
    ]
    
    # Genera una expresión regular completa que une todos los patrones anteriores.
    regex_token = '|'.join(f'(?P<{nombre}>{patron})' for nombre, patron in tipo_token)
    
    # Compila la expresión regular para una búsqueda más rápida.
    obtener_token = re.compile(regex_token).match
    
    # Inicializa variables para el control de posición y línea.
    num_linea = 1
    posicion = inicio_linea = 0
    tokens = []

    # Inicia el proceso de detección de tokens en el código.
    coincidencia = obtener_token(codigo)
    while coincidencia:
        tipo = coincidencia.lastgroup  # Tipo de token detectado.
        valor = coincidencia.group()  # Texto del token detectado
        
        # Clasificación de tokens según su tipo.
        if tipo == 'NUMERO':
            tokens.append(('NUMERO', valor, num_linea))
        elif tipo == 'IDENTIFICADOR':
            if valor in palabra_clave:
                tokens.append(('PALABRA CLAVE', valor, num_linea))
            else:
                tokens.append(('IDENTIFICADOR', valor, num_linea))
        elif tipo == 'OPERADOR':
            tokens.append(('OPERADOR', valor, num_linea))
        elif tipo == 'DELIMITADOR':
            tokens.append(('DELIMITADOR', valor, num_linea))
        elif tipo == 'CADENA':
            tokens.append(('CADENA', valor, num_linea))
        elif tipo == 'PREPROCESADOR':
            tokens.append(('PREPROCESADOR', valor.strip(), num_linea))
        elif tipo == 'NUEVA_LINEA':
            inicio_linea = coincidencia.end()  # Actualiza el inicio de línea.
            num_linea += 1  # Incrementa el número de línea.
        elif tipo == 'OMITIR':
            pass  # Ignora espacios y tabulaciones.
        elif tipo == 'NO_COINCIDE':
            tokens.append(('DESCONOCIDO', valor, num_linea))  # Detecta tokens inválidos.
        
        # Actualiza la posición actual en el código.
        posicion = coincidencia.end()
        
        # Intenta obtener el siguiente token.
        coincidencia = obtener_token(codigo, posicion)
    
    # Devuelve la lista de tokens encontrados.
    return tokens

# ------ ANALIZADOR SINTÁCTICO -------
class AnalizadorSimplificadoCPP:
    def __init__(self, tokens):
        self.tokens = tokens  # Lista de tokens del analizador léxico
        self.indice_token_actual = 0
        self.token_actual = tokens[0] if tokens else None

    def avanzar(self):
        """Avanza al siguiente token."""
        self.indice_token_actual += 1
        if self.indice_token_actual < len(self.tokens):
            self.token_actual = self.tokens[self.indice_token_actual]
        else:
            self.token_actual = None

    def esperar(self, tipo_token, valor_token=None):
        """Espera un tipo de token específico (y opcionalmente un valor)."""
        if self.token_actual and self.token_actual[0] == tipo_token:
            if valor_token is None or self.token_actual[1] == valor_token:
                self.avanzar()
            else:
                self.error(f"Se esperaba '{valor_token}', pero se encontró '{self.token_actual[1]}'")
        else:
            esperado = f"{tipo_token}" + (f" '{valor_token}'" if valor_token else "")
            encontrado = f"'{self.token_actual[1]}'" if self.token_actual else "EOF"
            self.error(f"Se esperaba {esperado}, pero se encontró {encontrado}")

    def error(self, mensaje):
        """Imprime un mensaje de error y lanza una excepción."""
        linea = self.token_actual[2] if self.token_actual else "desconocida"
        print(f"\nError de sintaxis en la línea {linea}: {mensaje}")
        raise SyntaxError(mensaje)

    def analizar_programa(self):
        """Analiza todo el programa."""
        while self.token_actual:
            self.analizar_sentencia()

    def analizar_sentencia(self):
        """Analiza una sentencia."""
        if self.token_actual[0] == "PREPROCESADOR":
            self.analizar_preprocesador()
        elif self.token_actual[0] == "PALABRA CLAVE":
            if self.token_actual[1] in {"int", "float", "char", "void"}:
                self.analizar_declaracion()
            elif self.token_actual[1] == "if":
                self.analizar_sentencia_control()
            elif self.token_actual[1] == "while":
                self.analizar_bucle_while()
            elif self.token_actual[1] == "for":
                self.analizar_bucle_for()
            elif self.token_actual[1] == "return":
                self.analizar_sentencia_retorno()
            elif self.token_actual[1] == "using":
                self.analizar_uso_espacio_nombres()
            else:
                self.error(f"Palabra clave inesperada '{self.token_actual[1]}'")
        elif self.token_actual[0] == "IDENTIFICADOR":
            self.analizar_expresion()
            self.esperar("DELIMITADOR", ";")
        elif self.token_actual[0] == "DELIMITADOR" and self.token_actual[1] == "{":
            self.analizar_bloque()
        else:
            self.error("Token inesperado")

    def analizar_declaracion(self):
        """Analiza una declaración de variable o función."""
        self.esperar("PALABRA CLAVE")  # Tipo (int, float, etc.)
        self.esperar("IDENTIFICADOR")  # Nombre de variable/función
        
        # Verifica si es una declaración de función o de variable
        if self.token_actual and self.token_actual[0] == "DELIMITADOR" and self.token_actual[1] == "(":
            # Declaración de función - reutiliza la lógica de analizar_funcion
            self.esperar("DELIMITADOR", "(")
            
            # Opcionalmente analiza los parámetros
            if self.token_actual and self.token_actual[0] != "DELIMITADOR":
                self.analizar_parametros()
            
            # Espera ')' para el final de la lista de parámetros
            self.esperar("DELIMITADOR", ")")
            
            # Espera el cuerpo de la función (bloque)
            self.analizar_bloque()
        else:
            # Declaración de variable
            if self.token_actual and self.token_actual[0] == "OPERADOR" and self.token_actual[1] == "=":
                self.avanzar()  # '='
                self.analizar_expresion()
            self.esperar("DELIMITADOR", ";")

    def analizar_expresion(self):
        """Analiza una expresión."""
        self.analizar_valor()
        if self.token_actual and self.token_actual[0] == "OPERADOR":
            self.avanzar()  # Operador
            self.analizar_valor()

    def analizar_valor(self):
        """Analiza un valor (identificador, número o cadena)."""
        if self.token_actual[0] in {"IDENTIFICADOR", "NUMERO", "CADENA"}:
            self.avanzar()
        else:
            self.error("Se esperaba un valor (identificador, número o cadena)")

    def analizar_sentencia_control(self):
        """Analiza una sentencia de control if-else."""
        self.esperar("PALABRA CLAVE", "if")
        self.esperar("DELIMITADOR", "(")
        self.analizar_expresion()
        self.esperar("DELIMITADOR", ")")
        self.analizar_bloque()
        if self.token_actual and self.token_actual[0] == "PALABRA CLAVE" and self.token_actual[1] == "else":
            self.avanzar()
            self.analizar_bloque()

    def analizar_bucle_while(self):
        """Analiza un bucle while."""
        self.esperar("PALABRA CLAVE", "while")
        self.esperar("DELIMITADOR", "(")
        self.analizar_expresion()
        self.esperar("DELIMITADOR", ")")
        self.analizar_bloque()

    def analizar_bucle_for(self):
        """Analiza un bucle for."""
        self.esperar("PALABRA CLAVE", "for")
        self.esperar("DELIMITADOR", "(")
        self.analizar_declaracion()
        self.analizar_expresion()
        self.esperar("DELIMITADOR", ";")
        self.analizar_expresion()
        self.esperar("DELIMITADOR", ")")
        self.analizar_bloque()

    def analizar_bloque(self):
        """Analiza un bloque de código encerrado entre llaves."""
        self.esperar("DELIMITADOR", "{")
        while self.token_actual and self.token_actual[1] != "}":
            self.analizar_sentencia()
        self.esperar("DELIMITADOR", "}")

    def analizar_sentencia_retorno(self):
        """Analiza una sentencia de retorno."""
        self.esperar("PALABRA CLAVE", "return")
        self.analizar_valor()
        self.esperar("DELIMITADOR", ";")

    def analizar_uso_espacio_nombres(self):
        """Analiza una sentencia de uso de espacio de nombres."""
        self.esperar("PALABRA CLAVE", "using")
        self.esperar("PALABRA CLAVE", "namespace")
        self.esperar("IDENTIFICADOR")
        self.esperar("DELIMITADOR", ";")

    def analizar_preprocesador(self):
        """Analiza una directiva de preprocesador (#include) con una estructura detallada."""
        # Espera #include
        self.esperar("PREPROCESADOR", "#include")

        if self.token_actual and self.token_actual[0] == "OPERADOR":
            if self.token_actual[1] == "<":  # Cabecera del sistema
                self.avanzar()  # Consume '<'
                self.esperar("IDENTIFICADOR")  # Espera el nombre de la cabecera (por ejemplo, iostream)
                self.esperar("OPERADOR", ">")  # Espera el cierre '>'
            elif self.token_actual[1] == "\"":  # Cabecera del usuario
                self.avanzar()  # Consume '"'
                self.esperar("IDENTIFICADOR")  # Espera el nombre de la cabecera (por ejemplo, mi_cabecera)
                if self.token_actual and self.token_actual[0] == "DELIMITADOR" and self.token_actual[1] == ".":
                    self.avanzar()  # Consume '.'
                    self.esperar("IDENTIFICADOR")  # Espera la extensión del archivo (por ejemplo, h)
                self.esperar("DELIMITADOR", "\"")  # Espera el cierre '"'
            else:
                self.error("Se esperaba '<' o '\"' después de #include")
        else:
            self.error("Se esperaba '<' o '\"' después de #include")

    def analizar_funcion(self):
        """Analiza una declaración de función (por ejemplo, int main() {})."""
        self.esperar("PALABRA CLAVE")  # Espera el tipo de retorno (por ejemplo, "int", "void", etc.)
        self.esperar("IDENTIFICADOR")  # Espera el nombre de la función (por ejemplo, "main")

        # Espera '(' para el inicio de la lista de parámetros
        self.esperar("DELIMITADOR", "(")

        # Opcionalmente analiza los parámetros
        if self.token_actual and self.token_actual[0] != "DELIMITADOR":
            self.analizar_parametros()

        # Espera ')' para el final de la lista de parámetros
        self.esperar("DELIMITADOR", ")")

        # Espera el cuerpo de la función (bloque)
        self.analizar_bloque()

    def analizar_parametros(self):
        """Analiza la lista de parámetros de una función."""
        self.analizar_parametro()  # Analiza el primer parámetro
        while self.token_actual and self.token_actual[0] == "DELIMITADOR" and self.token_actual[1] == ",":
            self.avanzar()  # Consume ','
            self.analizar_parametro()  # Analiza el siguiente parámetro

    def analizar_parametro(self):
        """Analiza un único parámetro en la lista de parámetros."""
        self.esperar("PALABRA CLAVE")  # Espera el tipo del parámetro (por ejemplo, "int", "float")
        self.esperar("IDENTIFICADOR")  # Espera el nombre del parámetro (por ejemplo, "x", "y")