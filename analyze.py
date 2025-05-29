from globalTypes import *
from symtab import *

# Agrega esto al principio de tu archivo analyze.py o semantico.py
global_program_lines = {}
programText = ""

Error = False
location = 0
current_function = None

# counter for variable memory locations
location = 0;

# Procedure traverse is a generic recursive 
# syntax tree traversal routine:
# it applies preProc in preorder and postProc 
# in postorder to tree pointed to by t

def traverse(t, preProc, postProc):
    if (t != None):
        preProc(t)
        for i in range(MAXCHILDREN):
            traverse(t.child[i],preProc,postProc)
        postProc(t)
        traverse(t.sibling,preProc,postProc)

# nullProc is a do-nothing procedure to generate preorder-only or
# postorder-only traversals from traverse
def nullProc(t):
    None
    
def countParams(param_node):
    count = 0
    while param_node:
        count += 1
        param_node = param_node.sibling
    return count

# Procedure insertNode inserts identifiers stored in t into 
# the symbol table 
def insertNode(t):
    global location
    if t.nodekind == NodeKind.StmtK:
        if t.stmt == StmtKind.VarDeclK:
            attr = SymbolAttributes(
                name=t.name,
                kind="variable",
                type_=t.type,
                lineno=t.lineno,
                scope="global",  # en el futuro se puede ajustar por scopes reales
                is_array=(t.val == -1),
                location=location
            )
            st_insert(t.name, attr)
            location += 1
        elif t.stmt == StmtKind.FunDeclK:
            # Insertar cada parámetro individualmente en la tabla
            param_list = []
            param_node = t.child[0]
            while param_node is not None:
                param_attr = SymbolAttributes(
                    name=param_node.name,
                    kind="param",
                    type_=param_node.type,
                    lineno=param_node.lineno,
                    scope=t.name,
                    is_array=(param_node.val == -1),
                    location=location
                )
                param_list.append(param_attr)
                st_insert(param_node.name, param_attr)
                location += 1
                param_node = param_node.sibling
            attr = SymbolAttributes(
                name=t.name,
                kind="function",
                type_=t.type,
                lineno=t.lineno,
                scope="global",
                params=param_list
            )
            st_insert(t.name, attr)
    elif t.nodekind == NodeKind.ExpK:
        if t.exp == ExpKind.IdK:
            found = st_lookup(t.name)
            if found:
                st_insert(t.name, SymbolAttributes(
                    name=t.name,
                    kind=found.kind,
                    type_=found.type,
                    lineno=t.lineno,
                    scope=found.scope,
                    is_array=found.is_array,
                    location=found.location
                ))
        elif t.exp == ExpKind.CallK:
            info = st_lookup(t.name)
            if not info and t.name in ("input", "output"):
                # Declarar funciones built-in si se usan y aún no están en la tabla
                if t.name == "input":
                    attr = SymbolAttributes(
                        name="input",
                        kind="function",
                        type_=TokenType.INT,  # retorna entero
                        lineno=t.lineno,
                        scope="global",
                        params=[]
                    )
                elif t.name == "output":
                    param_attr = SymbolAttributes(
                        name="arg",  # nombre simbólico para el parámetro
                        kind="param",
                        type_=TokenType.INT,
                        lineno=t.lineno,
                        scope="output",
                        is_array=False,
                        location=-1
                    )
                    attr = SymbolAttributes(
                        name="output",
                        kind="function",
                        type_=TokenType.VOID,
                        lineno=t.lineno,
                        scope="global",
                        params=[param_attr]
                    )
                st_insert(t.name, attr)

# Function buildSymtab constructs the symbol 
# table by preorder traversal of the syntax tree
def buildSymtab(syntaxTree, imprime):
    traverse(syntaxTree, insertNode, nullProc)
    if (imprime):
        print()
        print("Symbol table:")
        printSymTab()

def cargarPrograma(codigo):
    global programText
    programText = codigo

def find_token_position(line, token_string):
    if not token_string:
        return 0
    pos = line.find(token_string)
    return pos if pos != -1 else 0

def typeError(t, message):
    global Error
    Error = True
    print(f"Línea {t.lineno}: {message}")

    # Imprimir la línea de código con flecha
    lines = programText.splitlines()
    if 1 <= t.lineno <= len(lines):
        line = lines[t.lineno - 1]
        print(line)
        pointer_position = find_token_position(line, t.name if hasattr(t, "name") else "")
        print(" " * pointer_position + "^")

# Procedure checkNode performs type checking at a single tree node
def checkNode(t):
    global current_function
    if t.nodekind == NodeKind.ExpK:
        if t.exp == ExpKind.OpK:
            if ((t.child[0].type != ExpType.Integer) or (t.child[1].type != ExpType.Integer)):
                typeError(t, "Operator applied to non-integer")
            if t.op in {TokenType.EE, TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE, TokenType.NE}:
                t.type = ExpType.Boolean
            else:
                t.type = ExpType.Integer
        elif t.exp == ExpKind.ConstK:
            t.type = ExpType.Integer
        elif t.exp == ExpKind.IdK:
            info = st_lookup(t.name)
            if info:
                t.type = ExpType.Integer if info.type == TokenType.INT else ExpType.Void
            else:
                typeError(t, f"Use of undeclared identifier '{t.name}'")
                t.type = ExpType.Void
        elif t.exp == ExpKind.CallK:
            info = st_lookup(t.name)
            if not info:
                typeError(t, f"Call to undeclared function '{t.name}'")
            elif info.kind != "function":
                typeError(t, f"Identifier '{t.name}' is not a function")
            else:
                t.type = ExpType.Integer if info.type == TokenType.INT else ExpType.Void
                # Validar argumentos
                expected = info.params
                given = []
                arg = t.child[0]
                while arg:
                    given.append(arg)
                    arg = arg.sibling
                if len(expected) != len(given):
                    typeError(t, f"Function '{t.name}' expects {len(expected)} args, got {len(given)}")
    elif t.nodekind == NodeKind.StmtK:
        if t.stmt == StmtKind.IfK:
            if t.child[0] and t.child[0].type not in {ExpType.Integer, ExpType.Boolean}:
                typeError(t.child[0], "Condition must be of type integer or boolean")
        elif t.stmt == StmtKind.AssignK:
            if t.child[0] and t.child[0].type != ExpType.Integer:
                typeError(t.child[0], "Assignment to non-integer")
        elif t.stmt == StmtKind.ReturnK:
            if current_function:
                if t.child[0]:
                    if current_function.type == TokenType.VOID:
                        typeError(t, f"Function '{current_function.name}' is void but returns a value")
                else:
                    if current_function.type == TokenType.INT:
                        typeError(t, f"Function '{current_function.name}' must return a value")

# Procedure typeCheck performs type checking 
# by a postorder syntax tree traversal
def typeCheck(syntaxTree, program=None):
    global programText
    if program:
        programText = program
    traverse(syntaxTree, nullProc, checkNode)
