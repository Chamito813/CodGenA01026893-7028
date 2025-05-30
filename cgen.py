from globalTypes import *

output = []
# Lista ordenada de variables globales, para asignar offsets
declared_vars = []
var_offsets = {}
label_counter = 0
temp_counter = 0

def emit(instr, comment=""):
    if comment:
        output.append(f"\t{instr}\t# {comment}")
    else:
        output.append(f"\t{instr}")

def emit_label(label):
    output.append(f"{label}:")

def new_label(prefix="L"):
    global label_counter
    lab = f"{prefix}{label_counter}"
    label_counter += 1
    return lab

def new_temp():
    global temp_counter
    r = f"$t{temp_counter % 10}"
    temp_counter += 1
    return r

def handle_stmt(node):
    if node.stmt == StmtKind.FunDeclK:
        emit_label(node.name)
        if node.name == "main":
            emit("la $gp, global_data", "Inicializar $gp a global_data")
        generate_code(node.child[1])

    elif node.stmt == StmtKind.VarDeclK:
        if node.name not in var_offsets:
            offset = len(declared_vars) * 4
            declared_vars.append(node.name)
            var_offsets[node.name] = offset

    elif node.stmt == StmtKind.AssignK:
        generate_code(node.child[0])
        off = var_offsets[node.name]
        emit(f"sw $t0, {off}($gp)", f"Asignar a {node.name}")

    elif node.stmt == StmtKind.CompoundK:
        for c in node.child:
            if c:
                generate_code(c)

    elif node.stmt == StmtKind.IfK:
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

    elif node.stmt == StmtKind.WhileK:
        start_lbl = new_label("while")
        end_lbl   = new_label("endwhile")
        emit_label(start_lbl)
        generate_code(node.child[0])  # condición
        emit(f"beq $t0, $zero, {end_lbl}", "Salir while si condición es falsa")
        generate_code(node.child[1])  # cuerpo
        emit(f"j {start_lbl}", "Volver al inicio del while")
        emit_label(end_lbl)

    elif node.stmt == StmtKind.ReturnK:
        generate_code(node.child[0])
        emit("move $v0, $t0", "Retornar valor")
        emit("jr $ra", "Regresar de función")

def handle_expr(node):
    # constantes
    if node.exp == ExpKind.ConstK:
        emit(f"li $t0, {node.val}", f"Cargar constante {node.val}")

    # variables globales
    elif node.exp == ExpKind.IdK:
        off = var_offsets[node.name]
        emit(f"lw $t0, {off}($gp)", f"Cargar variable {node.name}")

    # llamadas
    elif node.exp == ExpKind.CallK:
        if node.name == "input":
            emit("li $v0, 5", "Leer entero")
            emit("syscall")
            emit("move $t0, $v0", "Guardar resultado de input")
        elif node.name == "output":
            if node.child[0]:
                generate_code(node.child[0])
                emit("move $a0, $t0", "Pasar argumento a $a0")
            else:
                emit("li $a0, 0", "Output sin args → pasar 0")
            emit("li $v0, 1", "Imprimir entero")
            emit("syscall")
        else:
            # argumentos en pila
            args = []
            c = node.child[0]
            while c:
                generate_code(c)
                emit("subu $sp, $sp, 4", "Reservar espacio")
                emit("sw $t0, 0($sp)", "Push arg")
                args.append(c)
                c = c.sibling
            emit(f"jal {node.name}", f"Llamar {node.name}")
            emit("move $t0, $v0", "Resultado")
            if args:
                emit(f"addu $sp, $sp, {4*len(args)}", "Limpiar pila")

    # operaciones binarias
    elif node.exp == ExpKind.OpK:
        generate_code(node.child[0])
        emit("move $t1, $t0", "Guardar izq")
        generate_code(node.child[1])
        op = node.op
        if op == TokenType.PLUS:
            emit("add $t0, $t1, $t0", "Suma")
        elif op == TokenType.MINUS:
            emit("sub $t0, $t1, $t0", "Resta")
        elif op == TokenType.TIMES:
            emit("mul $t0, $t1, $t0", "Multiplicación")
        elif op == TokenType.OVER:
            emit("div $t1, $t0", "Dividir")
            emit("mflo $t0", "Guardar cociente")
        elif op == TokenType.EE:
            emit("seq $t0, $t1, $t0", "Igualdad")
        elif op == TokenType.NE:
            emit("sne $t0, $t1, $t0", "Desigualdad")
        elif op == TokenType.LT:
            emit("slt $t0, $t1, $t0", "Menor que")
        elif op == TokenType.LE:
            emit("sle $t0, $t1, $t0", "≤")
        elif op == TokenType.GT:
            emit("sgt $t0, $t1, $t0", "Mayor que")
        elif op == TokenType.GE:
            emit("sge $t0, $t1, $t0", "≥")

def generate_code(node):
    while node:
        if node.nodekind == NodeKind.StmtK:
            handle_stmt(node)
        else:
            handle_expr(node)
        node = node.sibling

def write_output_to_file(filename="output.s"):
    with open(filename, "w") as f:
        # sección de datos
        f.write(".data\n")
        f.write("global_data:\n")
        for var in declared_vars:
            f.write(f"  {var}: .word 0\n")
        # sección de código
        f.write("\n.text\n")
        for line in output:
            f.write(line + "\n")
        f.write("\tli $v0, 10\t# exit\n")
        f.write("\tsyscall\n")
