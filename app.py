import re

def lexer(codigo):
    tokens = []
    patron = r'"[^"]*"|\d+|[a-zA-Z_]+|==|!=|<=|>=|[+\-*/<>=;{}()]'
    for match in re.finditer(patron, codigo):
        valor = match.group()
        if valor.isdigit():
            tokens.append(('NUMERO', valor))
        elif valor.startswith('"'):
            tokens.append(('CADENA', valor[1:-1]))
        elif valor in ('crear', 'mostrar', 'si', 'sino', 'mientras'):
            tokens.append((valor.upper(), valor))
        elif valor in ('+', '-', '*', '/', '=', '==', '!=', '<', '>', '<=', '>='):
            tokens.append(('OPERADOR', valor))
        elif valor in ('{', '}', '(', ')', ';'):
            tokens.append((valor, valor))
        else:
            tokens.append(('IDENT', valor))
    return tokens

def parser(tokens):
    i = 0
    variables = {}

    def actual(): return tokens[i] if i < len(tokens) else ('EOF', '')
    def avanzar(): nonlocal i; i += 1
    def esperar(tipo):
        if actual()[0] == tipo:
            valor = actual()[1]
            avanzar()
            return valor
        else:
            raise SyntaxError(f'Se esperaba {tipo}, se obtuvo {actual()}')

    def obtener_valor():
        tipo, valor = actual()
        if tipo == 'NUMERO':
            avanzar(); return int(valor)
        elif tipo == 'CADENA':
            avanzar(); return valor
        elif tipo == 'IDENT':
            avanzar(); return variables.get(valor, 0)
        else:
            raise SyntaxError(f'Valor inválido: {valor}')

    def evaluar_expresion():
        val = obtener_valor()
        while actual()[0] == 'OPERADOR' and actual()[1] in ('+', '-', '*', '/'):
            op = actual()[1]; avanzar()
            val2 = obtener_valor()
            val = eval(f"{val} {op} {val2}")
        return val

    def evaluar_condicion():
        izq = obtener_valor()
        op = actual()[1]; avanzar()
        der = obtener_valor()
        return eval(f"{izq} {op} {der}")

    def ejecutar_bloque():
        instrucciones = []
        esperar('{')
        inicio = i
        profundidad = 1
        while profundidad > 0:
            tipo, _ = actual()
            if tipo == '{':
                profundidad += 1
            elif tipo == '}':
                profundidad -= 1
            if profundidad > 0:
                instrucciones.append(tokens[i])
            avanzar()
        return instrucciones

    def ejecutar_sentencia_local(tokens_locales):
        nonlocal i, tokens
        i_backup = i
        tokens_backup = tokens
        i = 0
        tokens = tokens_locales
        while i < len(tokens):
            ejecutar_sentencia()
        tokens = tokens_backup
        i = i_backup

    def ejecutar_sentencia():
        tipo, _ = actual()
        if tipo == 'CREAR':
            avanzar()
            var = esperar('IDENT')
            esperar('OPERADOR')
            val = evaluar_expresion()
            variables[var] = val
            esperar(';')
        elif tipo == 'MOSTRAR':
            avanzar()
            val = obtener_valor()
            print(val)
            esperar(';')
        elif tipo == 'SI':
            avanzar()
            esperar('(')
            condicion = evaluar_condicion()
            esperar(')')
            bloque_si = ejecutar_bloque()
            bloque_sino = []
            if actual()[0] == 'SINO':
                avanzar()
                bloque_sino = ejecutar_bloque()
            if condicion:
                ejecutar_sentencia_local(bloque_si)
            else:
                ejecutar_sentencia_local(bloque_sino)
        elif tipo == 'MIENTRAS':
            avanzar()
            esperar('(')
            condicion_inicio = i
            condicion_tokens = []
            while actual()[0] != ')':
                condicion_tokens.append(tokens[i])
                avanzar()
            esperar(')')
            cuerpo = ejecutar_bloque()
            while True:
                sub_i = 0
                def obtener_cond():
                    nonlocal sub_i
                    def a(): return condicion_tokens[sub_i] if sub_i < len(condicion_tokens) else ('EOF', '')
                    def av(): nonlocal sub_i; sub_i += 1
                    def val():
                        t, v = a()
                        if t == 'NUMERO': av(); return int(v)
                        elif t == 'IDENT': av(); return variables.get(v, 0)
                        else: raise Exception(f"Condición inválida: {v}")
                    izq = val()
                    op = a()[1]; av()
                    der = val()
                    return eval(f"{izq} {op} {der}")
                if obtener_cond():
                    ejecutar_sentencia_local(cuerpo)
                else:
                    break
        else:
            raise SyntaxError(f'Sentencia no reconocida: {actual()}')

    while i < len(tokens):
        ejecutar_sentencia()

# Ejecutar compilador
with open("programa.tueny", "r", encoding="utf-8") as archivo:
    codigo = archivo.read()

tokens = lexer(codigo)
parser(tokens)
