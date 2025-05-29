from globalTypes import *
from scanner import *

token = None # holds current token
tokenString = None # holds the token string value 
Error = False
#lineno = 1
SintaxTree = None
imprimeScanner = False
programText = ""

#FUNCIÓN GENERADA POR CHATGPT PARA AHORRAR TIEMPO
def tokenExpectedString(tokenType):
    if tokenType == TokenType.SEMI:
        return "';'"
    elif tokenType == TokenType.OKEY:
        return "'{'"
    elif tokenType == TokenType.CKEY:
        return "'}'"
    elif tokenType == TokenType.OPAR:
        return "'('"
    elif tokenType == TokenType.CPAR:
        return "')'"
    elif tokenType == TokenType.ASSIGN:
        return "'='"
    else:
        return tokenType.name

# Función para mostrar los errores de la forma en que yo quería
def syntaxError(message, error_lineno=None, column=None):
    global Error, lineno, programText
    Error = True
    
    if error_lineno is None:
        error_lineno = lineno

    print(f">>> Syntax error at line {error_lineno}: {message}")
    
    lines = programText.splitlines()
    if 1 <= error_lineno <= len(lines):
        line = lines[error_lineno - 1]
        print(line)
        if column is not None and 0 <= column < len(line):
            print(" " * column + "^")
        else:
            print(" " * len(line) + "^")

def advance():
    global token, tokenString, lineno
    token, tokenString, lineno = getToken(imprimeScanner)
    while token == TokenType.COMMENT:
        token, tokenString, lineno = getToken(imprimeScanner)

def match(expected):
    global token, tokenString, lineno
    if (token == expected):
        advance()
    else:
        expected_string = tokenExpectedString(expected)
        
        if expected in {TokenType.SEMI, TokenType.OKEY, TokenType.CKEY}:
            syntaxError(f"Expected {expected_string}", error_lineno=lineno - 1)
        else:
            syntaxError(f"Expected {expected_string}")
        
        while token not in {expected, TokenType.SEMI, TokenType.OKEY, TokenType.CKEY, TokenType.ENDFILE, TokenType.CPAR}:
            advance()
        
        if token == expected:
            advance()

#Empezamos las funciones de la gramática en EBFN
def declaration_list():
    t = declaration()
    p = t
    while token != TokenType.ENDFILE:
        q = declaration()
        if q is not None:
            if t is None:
                t = p = q
            else:
                p.sibling = q
                p = q
    return t

def declaration():
    global token, tokenString
    t = None
    if token in {TokenType.INT, TokenType.VOID}:
        saved_token = token
        match(token)
        if token == TokenType.ID:
            saved_name = tokenString
            match(TokenType.ID)
            if token == TokenType.OPAR:
                t = fun_declaration(saved_token, saved_name)
            else:
                t = var_declaration(saved_token, saved_name)
        else:
            syntaxError("Expected identifier after type-specifier\n")
            advance()
    else:
        syntaxError("Expected type-specifier (int or void)\n")
        advance()
    return t

def var_declaration(var_type=None, var_name=None):
    global token, tokenString, lineno

    t = newStmtNode(StmtKind.VarDeclK)
    if t is not None:
        t.type = var_type
        t.name = var_name
        if token == TokenType.ASSIGN:
            syntaxError("Initialization during declaration is not allowed in C-\n")
            while token != TokenType.SEMI and token != TokenType.ENDFILE:
                advance()
            match(TokenType.SEMI)
            return t
        if token == TokenType.OBRA:
            match(TokenType.OBRA)
            if token == TokenType.NUM:
                t.val = int(tokenString)
                match(TokenType.NUM)
                match(TokenType.CBRA)
            else:
                syntaxError("Expected number inside array declaration")
                advance()
        match(TokenType.SEMI)
    return t

def fun_declaration(fun_type, fun_name):
    t = newStmtNode(StmtKind.FunDeclK)
    if t is not None:
        t.type = fun_type
        t.name = fun_name
        match(TokenType.OPAR)   # (
        t.child[0] = params()
        match(TokenType.CPAR)   # )
        t.child[1] = compound_stmt()
    return t

def params():
    global token, tokenString, lineno
    t = None
    if token == TokenType.VOID:
        match(TokenType.VOID)
        if token != TokenType.CPAR:
            t = param_list()
    elif token == TokenType.INT:
        t = param_list()
    else:
        t = None
    return t


def param_list():
    global token, tokenString, lineno
    t = param()
    p = t
    while token == TokenType.COMMA:
        match(TokenType.COMMA)
        q = param()
        if q is not None:
            if t is None:
                t = p = q
            else:
                p.sibling = q
                p = q
    return t

def param():
    global token, tokenString, lineno
    t = None
    if token in {TokenType.INT, TokenType.VOID}:
        param_type = token
        match(token)
        if token == TokenType.ID:
            param_name = tokenString
            match(TokenType.ID)
            t = newStmtNode(StmtKind.ParamK)
            if t is not None:
                t.type = param_type
                t.name = param_name
                if token == TokenType.OBRA:
                    match(TokenType.OBRA)
                    match(TokenType.CBRA)
                    t.val = -1  # Usamos val = -1 para marcar que es un arreglo por comodidad
        else:
            syntaxError("Expected identifier after type-specifier in parameter")
            advance()
    else:
        syntaxError("Expected type-specifier in parameter")
        advance()
    return t

def compound_stmt():
    t = newStmtNode(StmtKind.CompoundK)

    if token == TokenType.OKEY:
        match(TokenType.OKEY)
    else:
        syntaxError(f"Expected '{{'")

    if t is not None:
        t.child[0] = local_declarations()
        t.child[1] = statement_list()

    if token == TokenType.CKEY:
        match(TokenType.CKEY)
    else:
        syntaxError("Expected '}'")

    return t


def local_declarations():
    global token, tokenString, lineno
    t = None
    p = None
    while token in {TokenType.INT, TokenType.VOID}:
        var_type = token
        match(token)
        if token == TokenType.ID:
            var_name = tokenString
            match(TokenType.ID)
            q = var_declaration(var_type, var_name)
        else:
            syntaxError("Expected identifier after type-specifier in local declaration")
            advance()
            continue
        
        if q is not None:
            if t is None:
                t = p = q
            else:
                p.sibling = q
                p = q
    return t

def statement_list():
    t = None
    p = None
    while token not in {TokenType.CKEY, TokenType.ENDFILE}:
        q = statement()
        if q is not None:
            if t is None:
                t = p = q
            else:
                p.sibling = q
                p = q
    return t

def statement():
    global token, tokenString, lineno
    t = None
    if token == TokenType.IF:
        t = selection_stmt()
    elif token == TokenType.WHILE:
        t = iteration_stmt()
    elif token == TokenType.RETURN:
        t = return_stmt()
    elif token == TokenType.OKEY:
        t = compound_stmt()
    elif token in {TokenType.INT, TokenType.VOID}:
        syntaxError("Unexpected declaration in statement list")
        advance()
    else:
        t = expression_stmt()
    return t


def selection_stmt():
    t = newStmtNode(StmtKind.IfK)
    match(TokenType.IF)
    match(TokenType.OPAR)   # (
    if t is not None:
        t.child[0] = expression()   # Aqui checamos la condición
    match(TokenType.CPAR)   # )
    if t is not None:
        t.child[1] = statement()    # Aqui checamos el cuerpo dentro de if
    if token == TokenType.ELSE:
        match(TokenType.ELSE)
        if t is not None:
            t.child[2] = statement()  # Aqui nos movemos al else
    return t

def iteration_stmt():
    t = newStmtNode(StmtKind.WhileK)
    match(TokenType.WHILE)
    match(TokenType.OPAR)   # (
    if t is not None:
        t.child[0] = expression()   # Checamos la condición while
    match(TokenType.CPAR)   # )
    if t is not None:
        t.child[1] = statement()    # aqui revisamos el contenido de while
    return t

def return_stmt():
    t = newStmtNode(StmtKind.ReturnK)
    match(TokenType.RETURN)
    if token != TokenType.SEMI:
        if t is not None:
            t.child[0] = expression()   # Aqui es la expresión return
    match(TokenType.SEMI)
    return t

def expression_stmt():
    global token, tokenString, lineno
    t = None
    if token != TokenType.SEMI:
        t = expression()   # Si no es ; se parsea una expresión
    match(TokenType.SEMI)   # Consumimos el ;
    return t

def expression():
    global token, tokenString, lineno
    t = None
    if token == TokenType.ID:
        saved_name = tokenString
        match(TokenType.ID)

        if token == TokenType.OBRA:
            # arreglo[id] o arreglo[id] = expr
            match(TokenType.OBRA)
            index_expr = expression()
            match(TokenType.CBRA)

            if token == TokenType.ASSIGN:
                t = newStmtNode(StmtKind.AssignK)
                t.name = saved_name
                t.child[0] = index_expr
                match(TokenType.ASSIGN)
                t.child[1] = expression()
            else:
                t = simple_expression(saved_id=saved_name)
                if t is not None:
                    t.child[0] = index_expr
        elif token == TokenType.ASSIGN:
            t = newStmtNode(StmtKind.AssignK)
            if t is not None:
                t.name = saved_name
            match(TokenType.ASSIGN)
            if t is not None:
                t.child[0] = expression()
        elif token == TokenType.OPAR:
            t = call(saved_name)
        else:
            t = simple_expression(saved_name)
    else:
        t = simple_expression()
    return t

def simple_expression(saved_id=None):
    global token, tokenString, lineno
    if saved_id is not None:
        t = additive_expression(saved_id)
    else:
        t = additive_expression()

    if token in {TokenType.LT, TokenType.LE, TokenType.GT, TokenType.GE, TokenType.EE, TokenType.NE}:
        p = newExpNode(ExpKind.OpK)
        if p is not None:
            p.child[0] = t
            p.op = token
            match(token)
            p.child[1] = additive_expression()
            return p
    return t

def additive_expression(saved_id=None):
    global token, tokenString, lineno
    if saved_id is not None:
        t = term(saved_id)
    else:
        t = term()
    
    while token in {TokenType.PLUS, TokenType.MINUS}:
        p = newExpNode(ExpKind.OpK)
        if p is not None:
            p.child[0] = t
            p.op = token
            t = p
            match(token)
            t.child[1] = term()
    return t

def term(saved_id=None):
    global token, tokenString, lineno
    if saved_id is not None:
        t = factor(saved_id)
    else:
        t = factor()
    
    while token in {TokenType.TIMES, TokenType.OVER}:
        p = newExpNode(ExpKind.OpK)
        if p is not None:
            p.child[0] = t
            p.op = token
            t = p
            match(token)
            t.child[1] = factor()
    return t

def factor(saved_id=None):
    global token, tokenString, lineno
    t = None
    if saved_id is not None:
        t = newExpNode(ExpKind.IdK)
        if t is not None:
            t.name = saved_id
        # Acceso a arreglo: ID [ expr ]
        if token == TokenType.OBRA:
            match(TokenType.OBRA)
            t.child[0] = expression()
            match(TokenType.CBRA)
    elif token == TokenType.NUM:
        t = newExpNode(ExpKind.ConstK)
        if t is not None:
            t.val = int(tokenString)
        match(TokenType.NUM)
    elif token == TokenType.ID:
        saved_name = tokenString
        match(TokenType.ID)
        if token == TokenType.OPAR:
            t = call(saved_name)
        else:
            t = newExpNode(ExpKind.IdK)
            if t is not None:
                t.name = saved_name
            if token == TokenType.OBRA:
                match(TokenType.OBRA)
                t.child[0] = expression()
                match(TokenType.CBRA)
    elif token == TokenType.OPAR:
        match(TokenType.OPAR)
        t = expression()
        match(TokenType.CPAR)
    else:
        syntaxError("Unexpected token in factor")
        advance()
    return t

def call(fun_name):
    global token, tokenString, lineno
    t = newExpNode(ExpKind.CallK)
    if t is not None:
        t.name = fun_name
        match(TokenType.OPAR)   # (
        t.child[0] = args()
        match(TokenType.CPAR)   # )
    return t

def args():
    global token, tokenString, lineno
    t = None
    if token != TokenType.CPAR:
        t = expression()
        p = t
        while token == TokenType.COMMA:
            match(TokenType.COMMA)
            q = expression()
            if q is not None:
                if t is None:
                    t = p = q
                else:
                    p.sibling = q
                    p = q
    return t


# Function newStmtNode creates a new statement
# node for syntax tree construction
def newStmtNode(kind):
    t = TreeNode();
    if (t==None):
        print("Out of memory error at line " + lineno)
    else:
        #for i in range(MAXCHILDREN):
        #    t.child[i] = None
        #t.sibling = None
        t.nodekind = NodeKind.StmtK
        t.stmt = kind
        t.lineno = lineno
    return t

# Function newExpNode creates a new expression 
# node for syntax tree construction

def newExpNode(kind):
    t = TreeNode()
    if (t==None):
        print("Out of memory error at line " + lineno)
    else:
        #for i in range(MAXCHILDREN):
        #    t.child[i] = None
        #t.sibling = None
        t.nodekind = NodeKind.ExpK
        t.exp = kind
        t.lineno = lineno
        t.type = ExpType.Void
    return t

# Procedure printToken prints a token
# and its lexeme to the listing file
def printToken(token, tokenString):
    if token in {TokenType.IF, TokenType.ELSE, TokenType.INT,
                 TokenType.RETURN, TokenType.VOID, TokenType.WHILE}:
        print("reserved word:", tokenString)
    elif token == TokenType.ASSIGN:
        print("=")
    elif token == TokenType.LT:
        print("<")
    elif token == TokenType.LE:
        print("<=")
    elif token == TokenType.GT:
        print(">")
    elif token == TokenType.GE:
        print(">=")
    elif token == TokenType.EE:
        print("==")
    elif token == TokenType.NE:
        print("!=")
    elif token == TokenType.PLUS:
        print("+")
    elif token == TokenType.MINUS:
        print("-")
    elif token == TokenType.TIMES:
        print("*")
    elif token == TokenType.OVER:
        print("/")
    elif token == TokenType.SEMI:
        print(";")
    elif token == TokenType.COMMA:
        print(",")
    elif token == TokenType.OPAR:
        print("(")
    elif token == TokenType.CPAR:
        print(")")
    elif token == TokenType.OBRA:
        print("[")
    elif token == TokenType.CBRA:
        print("]")
    elif token == TokenType.OKEY:
        print("{")
    elif token == TokenType.CKEY:
        print("}")
    elif token == TokenType.NUM:
        print("NUM, val=", tokenString)
    elif token == TokenType.ID:
        print("ID, name=", tokenString)
    elif token == TokenType.ENDFILE:
        print("EOF")
    elif token == TokenType.ERROR:
        print("ERROR:", tokenString)
    else:
        print("Unknown token:", token)

# Variable indentno is used by printTree to
# store current number of spaces to indent
indentno = 0

# printSpaces indents by printing spaces */
def printSpaces():
    print(" "*indentno, end = "")

# procedure printTree prints a syntax tree to the 
# listing file using indentation to indicate subtrees
def printTree(tree):
    global indentno
    indentno+=2 # INDENT
    while tree != None:
        printSpaces();
        if tree.nodekind == NodeKind.StmtK:
            if tree.stmt == StmtKind.IfK:
                print(tree.lineno, "If")
            elif tree.stmt == StmtKind.WhileK:
                print(tree.lineno, "While")
            elif tree.stmt == StmtKind.AssignK:
                print(tree.lineno, "Assign to:", tree.name)
            elif tree.stmt == StmtKind.ReturnK:
                print(tree.lineno, "Return")
            elif tree.stmt == StmtKind.CompoundK:
                print(tree.lineno, "Compound")
            elif tree.stmt == StmtKind.VarDeclK:
                print(tree.lineno, f"Var declaration: {tree.name} of type {tree.type.name}")
            elif tree.stmt == StmtKind.FunDeclK:
                print(tree.lineno, f"Function declaration: {tree.name} returns {tree.type.name}")
            elif tree.stmt == StmtKind.ParamK:
                print(tree.lineno, f"Param: {tree.name} of type {tree.type.name}")
            else:
                print(tree.lineno, "Unknown StmtNode kind")
        elif tree.nodekind == NodeKind.ExpK:
            if tree.exp == ExpKind.OpK:
                print(tree.lineno, "Op: ", end="")
                printToken(tree.op, " ")
            elif tree.exp == ExpKind.ConstK:
                print(tree.lineno, "Const:", tree.val)
            elif tree.exp == ExpKind.IdK:
                print(tree.lineno, "Id:", tree.name)
            elif tree.exp == ExpKind.CallK:
                print(tree.lineno, "Call to function:", tree.name)
            else:
                print(tree.lineno, "Unknown ExpNode kind")
        else:
            print(tree.lineno, "Unknown node kind");
        for i in range(MAXCHILDREN):
            printTree(tree.child[i])
        tree = tree.sibling
    indentno-=2 #UNINDENT

# the primary function of the parser
# Function parse returns the newly 
# constructed syntax tree

def parse(imprime=True):
    global token, tokenString, lineno
    advance()
    t = declaration_list()
    if (token != TokenType.ENDFILE):
        syntaxError("Code ends before file\n")
    if imprime:
        printTree(t)
    return t, False

def recibeParser(prog, pos, long):
    recibeScanner(prog, pos, long)
    global programa, lines
    programa = prog
    lines = {}
    for i, line in enumerate(prog.splitlines(), start=1):
        lines[i] = line

#syntaxTree = parse()