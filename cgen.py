from globalTypes import *

# --------------------------------------------------------------------------------
#              Generador de código MIPS (C- con funciones + j main al inicio)
# --------------------------------------------------------------------------------

output = []             # Lista donde acumulamos cada instrucción MIPS
declared_vars = set()   # Conjunto de nombres de variables globales
label_counter = 0       # Contador para generar etiquetas únicas

# Contexto para saber en qué función estamos y qué parámetros tiene
current_function = None
current_params = []

def emit(instr, comment=""):
    """ Agrega una instrucción (o instrucción + comentario) a 'output'. """
    if comment:
        output.append(f"\t{instr}\t# {comment}")
    else:
        output.append(f"\t{instr}")

def emit_label(label):
    """ Agrega una etiqueta MIPS (sin indentación). """
    output.append(f"{label}:")

def new_label(prefix="L"):
    """ Genera una etiqueta única con el prefijo dado. """
    global label_counter
    lbl = f"{prefix}{label_counter}"
    label_counter += 1
    return lbl

def generate_code(node):
    """
    Recorre el AST y emite instrucciones MIPS.
    - Soporta funciones (incluyendo 'main' e 'incr').
    - En 'main', no emitimos 'jr $ra' al final. En su lugar, cae al exit-syscall.
    """
    global current_function, current_params

    while node:
        # —————— Sentencias —————— #
        if node.nodekind == NodeKind.StmtK:

            # 1) Definición de función (FunDeclK)
            if node.stmt == StmtKind.FunDeclK:
                func_name = node.name

                # (1.a) Etiqueta de la función
                emit_label(func_name)

                # (1.b) Guardamos contexto actual para restaurarlo luego
                saved_function = current_function
                saved_params = current_params

                # (1.c) Establecemos el contexto de esta función
                current_function = func_name
                # Recopilar nombres de parámetros (child[0]) en una lista
                current_params = []
                param_node = node.child[0]
                while param_node:
                    current_params.append(param_node.name)
                    param_node = param_node.sibling

                # (1.d) Generar el cuerpo de la función (child[1])
                generate_code(node.child[1])

                # (1.e) Epílogo:
                #   • Si la función NO es 'main', hacemos 'jr $ra'.
                #   • Si es 'main', NO emitimos 'jr $ra'; cae al exit-syscall que pondremos más abajo.
                if func_name != "main":
                    emit("jr $ra", f"retornar de {func_name}")

                # (1.f) Restauramos el contexto anterior
                current_function = saved_function
                current_params = saved_params

            # 2) Declaración de variable global (VarDeclK)
            elif node.stmt == StmtKind.VarDeclK:
                declared_vars.add(node.name)

            # 3) Asignación: x = expr;
            elif node.stmt == StmtKind.AssignK:
                # (3.a) Asegurar que 'x' esté en declared_vars
                declared_vars.add(node.name)

                # (3.b) Generar la expresión (valor en $t0)
                generate_code(node.child[0])

                # (3.c) Escribir $t0 en la dirección de 'x'
                emit(f"la $t1, {node.name}", f"cargar dirección de {node.name} en $t1")
                emit(f"sw $t0, 0($t1)", f"almacenar $t0 → {node.name}")

            # 4) Compound { lista_de_sentencias }
            elif node.stmt == StmtKind.CompoundK:
                for ch in node.child:
                    if ch:
                        generate_code(ch)

            # 5) If (cond) then { ... } else { ... }
            elif node.stmt == StmtKind.IfK:
                # (5.a) Evaluar condición → $t0
                generate_code(node.child[0])
                else_lbl = new_label("else")
                end_lbl  = new_label("endif")

                # Si $t0 == 0, salta a else_lbl
                emit(f"beq $t0, $zero, {else_lbl}", "condición falsa → else")

                # then-branch
                generate_code(node.child[1])
                emit(f"j {end_lbl}", "saltar fin if")

                # etiqueta else:
                emit_label(else_lbl)
                if node.child[2]:
                    generate_code(node.child[2])

                # etiqueta endif:
                emit_label(end_lbl)

            # 6) While (cond) { ... }
            elif node.stmt == StmtKind.WhileK:
                start_lbl = new_label("while")
                end_lbl   = new_label("endwhile")

                emit_label(start_lbl)
                # (6.a) Evaluar condición
                generate_code(node.child[0])
                # (6.b) Si $t0 == 0, saltar a end_lbl
                emit(f"beq $t0, $zero, {end_lbl}", "condición falsa → fin while")
                # (6.c) Cuerpo del while
                generate_code(node.child[1])
                # (6.d) Volver a inicio para re-evaluar
                emit(f"j {start_lbl}", "volver a condición")
                emit_label(end_lbl)

            # 7) Return (ReturnK)
            elif node.stmt == StmtKind.ReturnK:
                # Si hay expresión de retorno, generarla y ponerla en $v0
                if node.child[0]:
                    generate_code(node.child[0])
                    emit("move $v0, $t0", "valor de retorno en $v0")
                # Si no es main, emitimos jr $ra; si es main, NO lo emitimos
                if current_function != "main":
                    emit("jr $ra", f"retornar de {current_function}")

        # —————— Expresiones —————— #
        elif node.nodekind == NodeKind.ExpK:

            # 1) Constante (ConstK)
            if node.exp == ExpKind.ConstK:
                emit(f"li $t0, {node.val}", f"const {node.val}")

            # 2) Identificador (IdK)
            elif node.exp == ExpKind.IdK:
                name = node.name
                # Si el identificador es parámetro de la función actual, viene en $a0
                if current_function and name in current_params:
                    emit("move $t0, $a0", f"param '{name}' → $t0")
                else:
                    # Sino, es variable global: aseguramos que exista en .data
                    declared_vars.add(name)
                    emit(f"la $t1, {name}", f"cargar dirección de {name} en $t1")
                    emit(f"lw $t0, 0($t1)", f"cargar {name} en $t0")

            # 3) Llamada a función (CallK)
            elif node.exp == ExpKind.CallK:
                func = node.name

                # Caso especial: output(<expr>)
                if func == "output":
                    if node.child[0]:
                        # Evaluar argumento → $t0
                        generate_code(node.child[0])
                        emit("move $a0, $t0", "pasar arg a $a0")
                    else:
                        emit("li $a0, 0", "output sin args → 0 en $a0")
                    emit("li $v0, 1", "syscall print_int")
                    emit("syscall")
                else:
                    # Llamado a función definida (ej. incr)
                    # (3.a) Si hay argumento, generarlo a $a0
                    if node.child[0]:
                        generate_code(node.child[0])
                        emit("move $a0, $t0", "pasar arg a $a0")
                    # (3.b) Saltar a la función
                    emit(f"jal {func}", f"llamar {func}")
                    # (3.c) Resultado queda en $v0 → moverlo a $t0
                    emit("move $t0, $v0", f"resultado de {func} → $t0")

            # 4) Operación binaria (OpK)
            elif node.exp == ExpKind.OpK:
                # (4.a) Evaluar hijo izquierdo → $t0
                generate_code(node.child[0])
                emit("move $t1, $t0", "guardar op izq en $t1")
                # (4.b) Evaluar hijo derecho → $t0
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

                # Comparaciones
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

def write_output_to_file(fn="output.s"):
    """
    Escribe el ensamblado completo en 'fn':
      1) Sección .data con cada variable global.
      2) ".text" y luego "j main" + ".globl main" antes de las instrucciones generadas.
      3) Al final, syscall 10 para garantizar salida si main no retornó.
    """
    with open(fn, "w") as f:
        # ===== Sección .data =====
        f.write(".data\n")
        for v in declared_vars:
            f.write(f"{v}: .word 0\n")

        # ===== Sección .text =====
        f.write("\n.text\n")
        # Insertamos un salto directo a main
        f.write("j main\n")
        # Ahora marcamos main como símbolo global
        f.write(".globl main\n")

        # Escribimos todas las instrucciones que se generaron
        for ln in output:
            f.write(ln + "\n")

        # Si main nunca retornó explícitamente, nos aseguramos de cerrar el programa
        f.write("\tli $v0, 10\t# exit por defecto\n")
        f.write("\tsyscall\n")
