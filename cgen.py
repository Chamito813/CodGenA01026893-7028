from globalTypes import *

# --------------------------------------------------
# Generador de código MIPS (simplificado para C-)
# --------------------------------------------------

output = []             # Lista de instrucciones MIPS
declared_vars = set()   # Conjunto de nombres de variables globales
label_counter = 0       # Contador para generar etiquetas únicas

def emit(instr, comment=""):
    """Agrega una instrucción (o instrucción + comentario) a la lista output."""
    if comment:
        output.append(f"\t{instr}\t# {comment}")
    else:
        output.append(f"\t{instr}")

def emit_label(label):
    """Agrega una etiqueta MIPS (sin indentación)."""
    output.append(f"{label}:")

def new_label(prefix="L"):
    """Genera una etiqueta única con un prefijo opcional."""
    global label_counter
    lbl = f"{prefix}{label_counter}"
    label_counter += 1
    return lbl

def generate_code(node):
    """
    Recorre el AST y emite instrucciones MIPS.
    Asume que existe una función principal llamada 'main'.
    """
    while node:
        # —————— Sentencias —————— #
        if node.nodekind == NodeKind.StmtK:

            # 1) Declaración de función (solo usamos main)
            if node.stmt == StmtKind.FunDeclK:
                if node.name == "main":
                    emit_label("main")
                    # Recorremos el cuerpo de main (compound_stmt)
                    generate_code(node.child[1])

            # 2) Declaración de variable (viene de int r; o int i;)
            elif node.stmt == StmtKind.VarDeclK:
                # Aseguramos que aparezca en .data
                declared_vars.add(node.name)

            # 3) Asignación:   x = expr;
            elif node.stmt == StmtKind.AssignK:
                # (a) Aseguramos que x esté en declared_vars
                declared_vars.add(node.name)

                # (b) Generamos la expresión, dejando el resultado en $t0
                generate_code(node.child[0])

                # (c) Guardamos $t0 en la dirección de x
                emit(f"la $t1, {node.name}", f"Cargar dirección de {node.name} en $t1")
                emit(f"sw $t0, 0($t1)", f"Almacenar $t0 → {node.name}")

            # 4) Compound { ... }
            elif node.stmt == StmtKind.CompoundK:
                for ch in node.child:
                    if ch:
                        generate_code(ch)

            # 5) If (cond) then { ... } else { ... }
            elif node.stmt == StmtKind.IfK:
                # (a) Evaluar condición (resultado en $t0)
                generate_code(node.child[0])

                else_lbl = new_label("else")
                end_lbl  = new_label("endif")

                # Si $t0 == 0, saltar a else
                emit(f"beq $t0, $zero, {else_lbl}", "Condición falsa → else")

                # then-branch
                generate_code(node.child[1])
                emit(f"j {end_lbl}", "Saltar al fin del if")

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
                # Evaluar condición
                generate_code(node.child[0])
                # Si $t0 == 0, salir del while
                emit(f"beq $t0, $zero, {end_lbl}", "Condición falsa → fin while")
                # Cuerpo del while
                generate_code(node.child[1])
                # Volver al inicio para re-evaluar
                emit(f"j {start_lbl}", "Volver a condición")
                emit_label(end_lbl)

            # 7) Return (en main, termina el programa)
            elif node.stmt == StmtKind.ReturnK:
                if node.child[0]:
                    generate_code(node.child[0])
                    emit("move $v0, $t0", "Valor de retorno en $v0")
                # Terminamos con syscall 10
                emit("li $v0, 10", "exit")
                emit("syscall")

        # —————— Expresiones —————— #
        elif node.nodekind == NodeKind.ExpK:

            # 1) Constante
            if node.exp == ExpKind.ConstK:
                emit(f"li $t0, {node.val}", f"Cargar constante {node.val} en $t0")

            # 2) Identificador (lectura)
            elif node.exp == ExpKind.IdK:
                # (a) Aseguramos que la variable esté en .data
                declared_vars.add(node.name)
                # (b) Cargar su valor en $t0
                emit(f"la $t1, {node.name}", f"Cargar dirección de {node.name} en $t1")
                emit(f"lw $t0, 0($t1)", f"Cargar $t0 ← {node.name}")

            # 3) Llamada a función (solo manejamos output)
            elif node.exp == ExpKind.CallK:
                if node.name == "output":
                    # Si hay argumento, lo calculamos primero
                    if node.child[0]:
                        generate_code(node.child[0])
                        emit("move $a0, $t0", "Pasar argumento a $a0")
                    else:
                        emit("li $a0, 0", "Output sin args → 0 en $a0")
                    emit("li $v0, 1", "syscall print_int")
                    emit("syscall")

            # 4) Operación binaria
            elif node.exp == ExpKind.OpK:
                # calculamos recursivamente operando izquierdo
                generate_code(node.child[0])
                emit("move $t1, $t0", "Guardar operando izquierdo en $t1")
                # luego calculamos derecho
                generate_code(node.child[1])
                op = node.op

                if   op == TokenType.PLUS:
                    emit("add $t0, $t1, $t0", "Suma")
                elif op == TokenType.MINUS:
                    emit("sub $t0, $t1, $t0", "Resta")
                elif op == TokenType.TIMES:
                    emit("mul $t0, $t1, $t0", "Multiplicación")
                elif op == TokenType.OVER:
                    emit("div $t1, $t0", "División entera")
                    emit("mflo $t0",    "Resultado en $t0")

                # Comparaciones
                elif op == TokenType.LT:
                    emit("slt $t0, $t1, $t0", "i < j ?")
                elif op == TokenType.LE:
                    emit("sle $t0, $t1, $t0", "i <= j ?")
                elif op == TokenType.GT:
                    emit("sgt $t0, $t1, $t0", "i > j ?")
                elif op == TokenType.GE:
                    emit("sge $t0, $t1, $t0", "i >= j ?")
                elif op == TokenType.EE:
                    emit("seq $t0, $t1, $t0", "i == j ?")
                elif op == TokenType.NE:
                    emit("sne $t0, $t1, $t0", "i != j ?")

        # Avanzamos al siguiente hermano
        node = node.sibling

def write_output_to_file(fn="output.s"):
    """
    Escribe el ensamblado final en 'fn':
      1) Sección .data con cada variable global detectada.
      2) .globl main y .text antes de las instrucciones.
      3) Al final, syscall 10 para asegurar salida.
    """
    with open(fn, "w") as f:
        # ===== Sección de datos =====
        f.write(".data\n")
        for v in declared_vars:
            f.write(f"{v}: .word 0\n")

        # ===== Sección de texto (punto de entrada) =====
        f.write("\n.globl main\n")
        f.write(".text\n")
        for ln in output:
            f.write(ln + "\n")

        # Si main termina sin un return explícito, nos aseguramos de salir
        f.write("\tli $v0, 10\t# exit por defecto\n")
        f.write("\tsyscall\n")
