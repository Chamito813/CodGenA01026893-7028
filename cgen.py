#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# cgen.py
#
# Generador de código MIPS (MARS/QtSpim) para C- con:
#   - funciones (incluido main)
#   - if / else
#   - while
#   - asignaciones a variables globales
#   - llamada especial output(expr) para imprimir enteros (con "\n")
#   - return de funciones
#   - operadores aritméticos y comparaciones
#
# IMPORTANTE:
#   • En la función `recorrerNumeros`, salvamos/restauramos $ra en $s1 para
#     no perder la dirección de retorno a main cuando hacemos jal imprimirPar/imprimirImpar.
#
# Para usarlo junto con Parser.py y analyze.py:
#   1) main.py lee "prueba.c-", genera el AST y hace generate_code(syntaxTree).
#   2) Luego write_output_to_file("prueba.s") vuelca todo el MIPS.

from globalTypes import *

# ----------------------------------------
# Variables globales del generador
# ----------------------------------------
output = []             # Lista de líneas de MIPS generadas
declared_vars = set()   # Conjunto de variables globales (para .data)
label_counter = 0       # Contador para etiquetas únicas (“while0”, “else1”, etc.)

current_function = None # Nombre de la función actual
current_params = []     # Listado de parámetros de la función actual

# ----------------------------------------
# Auxiliares para emitir instrucciones
# ----------------------------------------
def emit(instr, comment=""):
    """
    Agrega una instrucción MIPS a `output`. Si `comment` no está vacío,
    se añade tras un '#'.
    """
    if comment:
        output.append(f"\t{instr}\t# {comment}")
    else:
        output.append(f"\t{instr}")

def emit_label(label):
    """Agrega una etiqueta (sin indentación) a `output`."""
    output.append(f"{label}:")

def new_label(prefix="L"):
    """Genera una etiqueta única con el prefijo dado."""
    global label_counter
    lbl = f"{prefix}{label_counter}"
    label_counter += 1
    return lbl

# ----------------------------------------
# generate_code: recorre el AST y llena `output`
# ----------------------------------------
def generate_code(node):
    global current_function, current_params

    while node:
        # ——— Sentencias ——— #
        if node.nodekind == NodeKind.StmtK:

            # 1) Declaración de función (FunDeclK)
            if node.stmt == StmtKind.FunDeclK:
                func_name = node.name

                # (1.a) Etiqueta de la función
                emit_label(func_name)

                # (1.b) Guardar contexto actual
                saved_function = current_function
                saved_params   = current_params

                # (1.c) Establecer nuevo contexto
                current_function = func_name
                current_params = []
                param_node = node.child[0]
                while param_node:
                    current_params.append(param_node.name)
                    param_node = param_node.sibling

                # — Prolog especial de `recorrerNumeros`: —
                #    • Guardamos 'n' (parámetro 0 en $a0) en $s0.
                #    • Además, salvamos $ra en $s1 para no perder retornar a main.
                if func_name == "recorrerNumeros" and len(current_params) >= 1:
                    emit("move $s0, $a0", "guardar n ($a0) → $s0 en recNum")
                    emit("move $s1, $ra", "salvar $ra original → $s1 (para volver a main)")

                # (1.d) Generar el cuerpo de la función
                generate_code(node.child[1])

                # (1.e) Epílogo:
                #    • Si es `recorrerNumeros`, restauramos $ra desde $s1 antes de retornar.
                #    • Si NO es main, hacemos jr $ra.
                if func_name == "recorrerNumeros":
                    emit("move $ra, $s1", "restaurar $ra desde $s1 para volver a main")
                    emit("jr $ra", "retornar de recorrerNumeros")
                elif func_name != "main":
                    emit("jr $ra", f"retornar de {func_name}")

                # (1.f) Restaurar contexto previo
                current_function = saved_function
                current_params = saved_params

            # 2) Declaración de variable global (VarDeclK)
            elif node.stmt == StmtKind.VarDeclK:
                declared_vars.add(node.name)

            # 3) Asignación: x = expr;
            elif node.stmt == StmtKind.AssignK:
                declared_vars.add(node.name)
                # Evaluar la expresión → $t0
                generate_code(node.child[0])
                # Guardar $t0 en la variable global x
                emit(f"la $t1, {node.name}", f"cargar dirección de {node.name}")
                emit(f"sw $t0, 0($t1)", f"almacenar $t0 → {node.name}")

            # 4) Compound { ... }
            elif node.stmt == StmtKind.CompoundK:
                for ch in node.child:
                    if ch:
                        generate_code(ch)

            # 5) If (cond) { then } else { else }
            elif node.stmt == StmtKind.IfK:
                else_lbl = new_label("else")
                end_lbl  = new_label("endif")

                # (5.a) Evaluar condición → $t0
                generate_code(node.child[0])
                # (5.b) Si $t0 == 0, saltar a else_lbl
                emit(f"beq $t0, $zero, {else_lbl}", "condición falsa → else")

                # (5.c) Rama THEN
                generate_code(node.child[1])
                # (5.d) Saltar al final
                emit(f"j {end_lbl}", "saltar fin if")

                # (5.e) Rama ELSE (si existe)
                emit_label(else_lbl)
                if node.child[2]:
                    generate_code(node.child[2])
                # (5.f) Fin del IF
                emit_label(end_lbl)

            # 6) While (cond) { body }
            elif node.stmt == StmtKind.WhileK:
                start_lbl = new_label("while")
                end_lbl   = new_label("endwhile")

                # (6.a) Etiqueta inicio
                emit_label(start_lbl)

                # (6.b) Evaluar condición → $t0
                #       Si la condición involucra “n” (parámetro 0), se lee de $s0.
                generate_code(node.child[0])
                # (6.c) Si $t0 == 0, saltar a end_lbl
                emit(f"beq $t0, $zero, {end_lbl}", "condición falsa → fin while")

                # (6.d) Cuerpo del while
                generate_code(node.child[1])
                # (6.e) Volver a inicio (para re-evaluar cond)
                emit(f"j {start_lbl}", "volver a condición")

                # (6.f) Etiqueta fin while
                emit_label(end_lbl)

            # 7) Return (return expr;)
            elif node.stmt == StmtKind.ReturnK:
                if node.child[0]:
                    # Evaluar expr → $t0
                    generate_code(node.child[0])
                    # Mover $t0 → $v0 (valor de retorno)
                    emit("move $v0, $t0", "valor de retorno en $v0")
                # Si no es main, retornar con jr $ra
                if current_function != "main":
                    emit("jr $ra", f"retornar de {current_function}")

        # — Expresiones — #
        elif node.nodekind == NodeKind.ExpK:

            # 1) Constante entera (ConstK)
            if node.exp == ExpKind.ConstK:
                emit(f"li $t0, {node.val}", f"const {node.val}")

            # 2) Identificador (IdK)
            elif node.exp == ExpKind.IdK:
                name = node.name
                # Si estamos en `recorrerNumeros` y es parámetro 0, leemos `$t0 ← $s0`
                if current_function == "recorrerNumeros" and name in current_params:
                    idx = current_params.index(name)
                    if idx == 0:
                        emit("move $t0, $s0", f"param '{name}' (en $s0) → $t0")
                    else:
                        raise Exception("Sólo se espera 1 parámetro en recorrerNumeros.")
                # Si es parámetro 0 de otra función, lo leemos de `$a0`
                elif current_function and name in current_params:
                    idx = current_params.index(name)
                    if idx == 0:
                        emit("move $t0, $a0", f"param '{name}' (en $a0) → $t0")
                    else:
                        raise Exception("Sólo soportamos 1 parámetro por función en este ejemplo.")
                else:
                    # Sino, variable global
                    declared_vars.add(name)
                    emit(f"la $t1, {name}", f"cargar dirección de {name}")
                    emit(f"lw $t0, 0($t1)", f"cargar {name} en $t0")

            # 3) Llamada a función (CallK)
            elif node.exp == ExpKind.CallK:
                func = node.name

                # Caso especial: output(expr)
                if func == "output":
                    # (a) Evaluar argumento (si existe) → $t0
                    if node.child[0]:
                        generate_code(node.child[0])
                    else:
                        # Si llamaron a output() sin argumentos:
                        emit("li $t0, 0", "output sin args → 0")

                    # (b) print_int
                    emit("move $a0, $t0", "pasar valor a $a0 para print_int")
                    emit("li   $v0, 1", "syscall print_int")
                    emit("syscall")

                    # (c) print_string "\n"
                    emit("la   $a0, newline", "cargar dirección de \"\\n\"")
                    emit("li   $v0, 4", "syscall print_string")
                    emit("syscall")

                    # (d) Por consistencia, dejamos $t0 = 0
                    emit("li   $t0, 0", "output devuelve 0")

                else:
                    # Llamada normal a función (apenas 1 arg, por simplicidad)
                    if node.child[0]:
                        generate_code(node.child[0])
                        emit("move $a0, $t0", "pasar argumento a $a0")
                    emit(f"jal {func}", f"llamar {func}")
                    # Tras el jal, $v0 lleva el resultado
                    emit("move $t0, $v0", f"resultado de {func} → $t0")

            # 4) Operación binaria (OpK)
            elif node.exp == ExpKind.OpK:
                # (a) Evaluar hijo izquierdo → $t0
                generate_code(node.child[0])
                emit("move $t1, $t0", "guardar op izq en $t1")
                # (b) Evaluar hijo derecho → $t0
                generate_code(node.child[1])

                op = node.op
                if   op == TokenType.PLUS:
                    emit("add $t0, $t1, $t0", "suma")
                elif op == TokenType.MINUS:
                    emit("sub $t0, $t1, $t0", "resta")
                elif op == TokenType.TIMES:
                    emit("mul $t0, $t1, $t0", "multiplicación")
                elif op == TokenType.OVER:
                    emit("div $t1, $t0", "división entera")
                    emit("mflo $t0",    "parte entera → $t0")
                # Comparaciones:
                elif op == TokenType.LT:
                    emit("slt $t0, $t1, $t0", "menor que")
                elif op == TokenType.LE:
                    emit("sle $t0, $t1, $t0", "menor o igual")
                elif op == TokenType.GT:
                    emit("sgt $t0, $t1, $t0", "mayor que")
                elif op == TokenType.GE:
                    emit("sge $t0, $t1, $t0", "mayor o igual")
                elif op == TokenType.EE:
                    emit("seq $t0, $t1, $t0", "igual")
                elif op == TokenType.NE:
                    emit("sne $t0, $t1, $t0", "distinto")

        # Avanzar al siguiente hermano
        node = node.sibling

# ----------------------------------------
# write_output_to_file: vuelca el MIPS en un .s
# ----------------------------------------
def write_output_to_file(fn="output.s"):
    """
    1) .data:
       • newline: .asciiz "\n"
       • cada variable global en `declared_vars` como `.word 0`
    2) .text:
       • j main
       • .globl main
       • todas las instrucciones de `output[]`
       • li $v0,10; syscall (exit) al final
    """
    with open(fn, "w") as f:
        # — Sección .data —
        f.write(".data\n")
        f.write("newline: .asciiz \"\\n\"\n")
        for var in declared_vars:
            f.write(f"{var}: .word 0\n")
        f.write("\n")

        # — Sección .text —
        f.write(".text\n")
        f.write("j main\n")
        f.write(".globl main\n\n")

        # Escribimos cada instrucción acumulada en `output`
        for ln in output:
            f.write(ln + "\n")

        # Syscall exit por defecto (en caso de que main no haga return)
        f.write("\tli $v0, 10\t# exit por defecto\n")
        f.write("\tsyscall\n")
