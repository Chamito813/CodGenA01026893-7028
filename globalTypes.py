from enum import Enum

#Token Type
class TokenType(Enum):
    ENDFILE = 300
    ERROR = 301
    #reserved words
    IF = 'if'
    ELSE = 'else'
    INT = 'int'
    RETURN = 'return'
    VOID = 'void'
    WHILE = 'while'
    # multicharacter tokens
    ID = 310
    NUM = 311
    # special symbols
    PLUS = '+'
    MINUS = '-'
    TIMES = '*'
    OVER = '/'
    LT = '<'
    LE = '<='
    GT = '>'
    GE = '>='
    EE = '=='
    NE = '!='
    ASSIGN = '='
    SEMI = ';'
    COMMA = ','
    OPAR = '('
    CPAR = ')'
    OBRA = '['
    CBRA = ']'
    OKEY = '{'
    CKEY = '}'
    COMMENT = '/**/'
    
# StateType
class StateType(Enum):
    START = 0
    INID = 1
    INNUM = 2
    INLT = 3
    INGT = 4
    INEQ = 5
    INNE = 6
    INCOMMENT = 7
    OUTCOMMENT = 8
    DONE = 9
    ERROR = 10

class ReservedWords(Enum):
    IF = 'if'
    ELSE = 'else'
    INT = 'int'
    RETURN = 'return'
    VOID = 'void'
    WHILE = 'while'
    
#***********   Syntax tree for parsing ************

class NodeKind(Enum):
    StmtK = 0
    ExpK = 1

class StmtKind(Enum):
    IfK = 0
    AssignK = 1
    WhileK = 2
    ReturnK = 3
    CompoundK = 4
    VarDeclK = 5
    FunDeclK = 6
    ParamK = 7

class ExpKind(Enum):
    OpK = 0
    ConstK = 1
    IdK = 2
    CallK = 3

# ExpType is used for type checking
class ExpType(Enum):
    Void = 0
    Integer = 1
    Boolean = 2

# Máximo número de hijos por nodo (3 para el if)
MAXCHILDREN = 3

class TreeNode:
    def __init__(self):
        # MAXCHILDREN = 3 está en globalTypes
        self.child = [None] * MAXCHILDREN # tipo treeNode
        self.sibling = None               # tipo treeNode
        self.lineno = 0                   # tipo int
        self.nodekind = None              # tipo NodeKind, en globalTypes
        # en realidad los dos siguientes deberían ser uno solo (kind)
        # siendo la  union { StmtKind stmt; ExpKind exp;}
        self.stmt = None                  # tipo StmtKind
        self.exp = None                   # tipo ExpKind
        # en realidad los tres siguientes deberían ser uno solo (attr)
        # siendo la  union { TokenType op; int val; char * name;}
        self.op = None                    # tipo TokenType
        self.val = None                   # tipo int
        self.name = None                  # tipo String
        # for type checking of exps
        self.type = None                  # de tipo ExpType

