from globalTypes import *

output = []              # Lista de instrucciones MIPS
declared_vars = set()    # Variables globales detectadas
label_counter = 0        # Para generar etiquetas únicas

def emit(instr, comment=""):
    if comment:
        output.append(f"\t{instr}\t# {comment}")
    else:
        output.append(f"\t{instr}")

def emit_label(label):
    output.append(f"{label}:")

def new_label(prefix="L"):
    global label_counter
    lbl = f"{prefix}{label_counter}"
    label_counter += 1
    return lbl

def generate_code(node):
    """ Recorre recursivamente los nodos del AST y emite MIPS. """
    while node:
        # —— Sentencias ——
        if node.nodekind == NodeKind.StmtK:
            if node.stmt == StmtKind.FunDeclK:
                # Prologue de función
                emit_label(node.name)
                emit("la $gp, global_data", "Inicializar $gp a sección .data")
                # Cuerpo
                generate_code(node.child[1])

            elif node.stmt == StmtKind.VarDeclK:
                declared_vars.add(node.name)

            elif node.stmt == StmtKind.AssignK:
                # x = expr;
                generate_code(node.child[0])
                emit(f"sw $t0, {node.name}($gp)", f"Asignar a {node.name}")

            elif node.stmt == StmtKind.CompoundK:
                for ch in node.child:
                    if ch: generate_code(ch)

            elif node.stmt == StmtKind.IfK:
                # if (cond) then … else …
                generate_code(node.child[0])
                else_lbl = new_label("else")
                end_lbl  = new_label("endif")
                emit(f"beq $t0, $zero, {else_lbl}", "Saltar si condición es falsa")
                generate_code(node.child[1])
                emit(f"j {end_lbl}", "Saltar al final del if")
                emit_label(else_lbl)
                if node.child[2]:
                    generate_code(node.child[2])
                emit_label(end_lbl)

            elif node.stmt == StmtKind.ReturnK:
                generate_code(node.child[0])
                emit("move $v0, $t0", "Retornar valor")
                emit("jr $ra",    "Regresar de función")

        # —— Expresiones ——
        elif node.nodekind == NodeKind.ExpK:
            if node.exp == ExpKind.ConstK:
                emit(f"li $t0, {node.val}", f"Cargar constante {node.val}")

            elif node.exp == ExpKind.IdK:
                emit(f"lw $t0, {node.name}($gp)", f"Cargar variable {node.name}")

            elif node.exp == ExpKind.CallK:
                # Llamadas predefinidas
                if node.name == "input":
                    emit("li $v0, 5",   "Leer entero")
                    emit("syscall")
                    emit("move $t0, $v0", "Guardar resultado de input")
                elif node.name == "output":
                    # Si viene un argumento, lo calculamos; si no, imprimimos 0.
                    if node.child[0]:
                        generate_code(node.child[0])
                        emit("move $a0, $t0", "Pasar arg. a $a0")
                    else:
                        emit("li $a0, 0", "Output sin args → pasar 0")
                    emit("li $v0, 1", "Imprimir entero")
                    emit("syscall")
                else:
                    # Otras llamadas: push de args y jal
                    args = []
                    arg = node.child[0]
                    while arg:
                        generate_code(arg)
                        emit("subu $sp, $sp, 4",        "Reservar espacio en pila")
                        emit("sw $t0, 0($sp)",           "Push argumento")
                        args.append(arg)
                        arg = arg.sibling
                    emit(f"jal {node.name}", f"Llamar función {node.name}")
                    emit("move $t0, $v0", "Resultado en $t0")
                    if args:
                        emit(f"addu $sp, $sp, {4*len(args)}", "Limpiar pila")

            elif node.exp == ExpKind.OpK:
                # Operación binaria
                generate_code(node.child[0])
                emit("move $t1, $t0", "Guardar operando izquierdo")
                generate_code(node.child[1])
                op = node.op
                if op == TokenType.PLUS:
                    emit("add $t0, $t1, $t0", "Suma")
                elif op == TokenType.MINUS:
                    emit("sub $t0, $t1, $t0", "Resta")
                elif op == TokenType.TIMES:
                    emit("mul $t0, $t1, $t0", "Multiplicación")
                elif op == TokenType.OVER:
                    emit("div $t1, $t0", "División entera")
                    emit("mflo $t0",    "Guardar cociente")
                # … aquí puedes agregar SLT, SEQ, etc. si lo necesitas …

        node = node.sibling


def write_output_to_file(fn="output.s"):
    with open(fn, "w") as f:
        # Sección de datos
        f.write(".data\n")
        f.write("global_data:\n")
        for v in declared_vars:
            f.write(f"{v}: .word 0\n")
        # Código
        f.write("\n.text\n")
        for ln in output:
            f.write(ln + "\n")
        # Salida del programa
        f.write("\tli $v0, 10\n")
        f.write("\tsyscall\n")
