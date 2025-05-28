import re

# --- Análisis Léxico ---
def lexer(codigo):
    tokens = []
    patron = r'"[^"]*"|\d+|[a-zA-Z_]+|=|;'
    for match in re.finditer(patron, codigo):
        valor = match.group()
        if valor.isdigit():
            tokens.append(('NUMERO', valor))
        elif valor.startswith('"') and valor.endswith('"'):
            tokens.append(('CADENA', valor[1:-1]))
        elif valor == '=':
            tokens.append(('IGUAL', valor))
        elif valor == ';':
            tokens.append(('PUNTOYCOMA', valor))
        elif valor == 'crear':
            tokens.append(('CREAR', valor))
        elif valor == 'mostrar':
            tokens.append(('MOSTRAR', valor))
        else:
            tokens.append(('IDENT', valor))
    return tokens

# --- Análisis Sintáctico y Ejecución ---
def parser(tokens):
    i = 0
    variables = {}

    def token_actual():
        return tokens[i] if i < len(tokens) else ('EOF', '')

    def avanzar():
        nonlocal i
        i += 1

    while i < len(tokens):
        tipo, valor = token_actual()
        if tipo == 'CREAR':
            avanzar()
            nombre_var = token_actual()[1]
            avanzar()
            if token_actual()[0] != 'IGUAL': raise SyntaxError('Se esperaba "="')
            avanzar()
            tipo_val, valor_val = token_actual()
            if tipo_val not in ('NUMERO', 'CADENA'): raise SyntaxError('Valor inválido')
            variables[nombre_var] = valor_val
            avanzar()
            if token_actual()[0] != 'PUNTOYCOMA': raise SyntaxError('Falta ";"')
            avanzar()
        elif tipo == 'MOSTRAR':
            avanzar()
            nombre_var = token_actual()[1]
            avanzar()
            if token_actual()[0] != 'PUNTOYCOMA': raise SyntaxError('Falta ";"')
            avanzar()
            if nombre_var in variables:
                print(variables[nombre_var])
            else:
                raise NameError(f'Variable no definida: {nombre_var}')
        else:
            raise SyntaxError(f'Token inesperado: {valor}')

# --- Código fuente en SimpleLang ---
codigo = '''
crear nombre = "Juan";
crear edad = 25;
mostrar nombre;
mostrar edad;
'''

# --- Ejecutar compilador ---
tokens = lexer(codigo)
parser(tokens)
