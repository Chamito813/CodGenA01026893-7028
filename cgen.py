from globalTypes import *

output = []
declared_vars = set()
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
    label = f"{prefix}{label_counter}"
    label_counter += 1
    return label

def generate_once_and_store(node):
    generate_code(node)
    temp_reg = new_temp()
    emit(f"move {temp_reg}, $t0", f"Guardar resultado temporal en {temp_reg}")
    emit("subu $sp, $sp, 4", "Reservar espacio en pila")
    emit(f"sw {temp_reg}, 0($sp)", f"Push argumento desde {temp_reg}")
    return temp_reg

def new_temp():
    global temp_counter
    reg = f"$t{(temp_counter % 10)}"  # Puedes mejorar esto luego si usas más temporales
    temp_counter += 1
    return reg

def handle_stmt(node):
    if node.stmt == StmtKind.FunDeclK:
        emit_label(node.name)
        generate_code(node.child[1])
    elif node.stmt == StmtKind.VarDeclK:
        declared_vars.add(node.name)
    elif node.stmt == StmtKind.AssignK:
        generate_code(node.child[0])
        emit(f"sw $t0, {node.name}($gp)", f"Asignar a {node.name}")
    elif node.stmt == StmtKind.CompoundK:
        for child in node.child:
            if child:
                generate_code(child)
    elif node.stmt == StmtKind.IfK:
        generate_code(node.child[0])
        else_lbl = new_label("else")
        end_lbl = new_label("endif")
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
        emit("jr $ra", "Regresar de función")

def handle_expr(node):
    if node.exp == ExpKind.ConstK:
        emit(f"li $t0, {node.val}", f"Cargar constante {node.val}")
    elif node.exp == ExpKind.IdK:
        emit(f"lw $t0, {node.name}($gp)", f"Cargar variable {node.name}")
    elif node.exp == ExpKind.CallK:
        if node.name == "input":
            emit("li $v0, 5", "Leer entero")
            emit("syscall")
            emit("move $t0, $v0", "Guardar resultado de input")
        elif node.name == "output":
            generate_code(node.child[0])
            emit("move $a0, $t0", "Pasar argumento a $a0")
            emit("li $v0, 1", "Código de imprimir")
            emit("syscall")
        else:
            args = []
            arg = node.child[0]
            while arg:
                temp = generate_once_and_store(arg)
                args.append(temp)  # Lo guardas por si se quiere reutilizar
                arg = arg.sibling
            emit(f"jal {node.name}", f"Llamar función {node.name}")
            emit("move $t0, $v0", "Resultado a $t0")
            if args:
                emit(f"addu $sp, $sp, {len(args)*4}", "Limpiar pila")
    elif node.exp == ExpKind.OpK:
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
            emit("div $t1, $t0", "Dividir t1 entre t0")
            emit("mflo $t0", "Guardar cociente en $t0")
        elif op == TokenType.EE:
            emit("seq $t0, $t1, $t0", "Igualdad")
        elif op == TokenType.NE:
            emit("sne $t0, $t1, $t0", "Desigualdad")
        elif op == TokenType.LT:
            emit("slt $t0, $t1, $t0", "Menor que")
        elif op == TokenType.LE:
            emit("sle $t0, $t1, $t0", "Menor o igual")
        elif op == TokenType.GT:
            emit("sgt $t0, $t1, $t0", "Mayor que")
        elif op == TokenType.GE:
            emit("sge $t0, $t1, $t0", "Mayor o igual")

def generate_code(node):
    while node:
        if node.nodekind == NodeKind.StmtK:
            handle_stmt(node)
        elif node.nodekind == NodeKind.ExpK:
            handle_expr(node)
        node = node.sibling

def write_output_to_file(filename="output.s"):
    with open(filename, "w") as f:
        f.write(".data\n")
        for var in declared_vars:
            f.write(f"{var}: .word 0\n")
        f.write("\n.text\n")
        for line in output:
            f.write(line + "\n")
        f.write("\tli $v0, 10\n\tsyscall\n")

# Ejemplo de uso (ya con un AST listo):
# generate_code(ast_root)
# write_output_to_file("programa.s")