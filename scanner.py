from globalTypes import *

lineno = 1

def recibeScanner(prog, pos, long):
    global program
    global position
    global programLength
    program = prog
    position = pos
    programLength = long

def reservedLookup(tokenString):
    for w in ReservedWords:
        if tokenString == w.value:
            return TokenType(tokenString)
    return TokenType.ID

def printToken(token, lexema, lineno):
    print(f"{str(lineno).rjust(3)}  {token.name.ljust(15)} ->  {lexema}")

def getToken(imprime = True):
    global position, lineno
    tokenString = "" # string for storing token
    currentToken = None # is a TokenType value
    state = StateType.START # current state - always begins at START
    save = True # flag to indicate save to tokenString
    while (state!=StateType.DONE):
        c = program[position]
        save = True
        if state == StateType.START:
            if c.isdigit():
                state = StateType.INNUM
            elif c.isalpha():
                state = StateType.INID
            elif c == '=':
                state = StateType.INEQ
            elif ((c == ' ') or (c == '\t') or (c == '\n')):
                save = False
                if(c == '\n'):
                    lineno += 1
            elif c == '/':
                if position + 1 < programLength and program[position + 1] == '*':
                    # Ignorar comentario /* ... */
                    position += 2
                    save = False
                    while position < programLength - 1:
                        if program[position] == '*' and program[position + 1] == '/':
                            position += 2
                            break
                        if program[position] == '\n':
                            lineno += 1
                        position += 1
                    continue  # <-- Reintenta el ciclo desde el principio ignorando el comentario
                else:
                    currentToken = TokenType.OVER
                    state = StateType.DONE
            else:
                state = StateType.DONE
                if position == programLength:
                    save = False
                    currentToken = TokenType.ENDFILE
                elif c == '<':
                    state = StateType.INLT
                elif c == '+':
                    currentToken = TokenType.PLUS
                elif c == '-':
                    currentToken = TokenType.MINUS
                elif c == '*':
                    currentToken = TokenType.TIMES
                elif c == '>':
                    state = StateType.INGT
                elif c == ';':
                    currentToken = TokenType.SEMI
                elif c == '{':
                    currentToken = TokenType.OKEY
                elif c == '}':
                    currentToken = TokenType.CKEY
                elif c == '[':
                    currentToken = TokenType.OBRA
                elif c == ']':
                    currentToken = TokenType.CBRA
                elif c == '(':
                    currentToken = TokenType.OPAR
                elif c == ')':
                    currentToken = TokenType.CPAR
                elif c == ',':
                    currentToken = TokenType.COMMA
                elif c == '!':
                    state = StateType.INNE
                else:
                    currentToken = TokenType.ERROR
        elif state == StateType.INNUM:
            if not c.isdigit():
                if position < programLength and c.isalpha():
                    currentToken = TokenType.ERROR
                    state = StateType.DONE
                else:
                    if position <= programLength:
                        position -= 1
                    save = False
                    state = StateType.DONE
                    currentToken = TokenType.NUM
        elif state == StateType.INID:
            if not c.isalpha():
                if position <= programLength:
                    position -= 1
                save = False
                state = StateType.DONE
                currentToken = TokenType.ID
        elif state == StateType.INEQ:
            save = False
            if c == '=':
                state = StateType.DONE 
                currentToken = TokenType.EE
            else:
                state = StateType.DONE
                currentToken = TokenType.ASSIGN
        elif state == StateType.INNE:
            save = False
            if c == '=':
                state = StateType.DONE
                currentToken = TokenType.NE
            else:
                state = StateType.DONE
                currentToken = TokenType.ERROR
        elif state == StateType.INLT:
            if c == '=':
                currentToken = TokenType.LE
            else:
                currentToken = TokenType.LT
                position -= 1
                save = False
            state = StateType.DONE
        elif state == StateType.INGT:
            if c == '=':
                currentToken = TokenType.GE
            else:
                currentToken = TokenType.GT
                position -= 1
                save = False
            state = StateType.DONE
        elif state == StateType.DONE:
            None
        else: # should never happen
            print('Scanner Bug: state= '+str(state))
            state = StateType.DONE
            currentToken = TokenType.ERROR
        if save:
            tokenString = tokenString + c
        if state == StateType.DONE:
            if currentToken == TokenType.ID:
                currentToken = reservedLookup(tokenString)
        position += 1
    if imprime:
        printToken(currentToken, tokenString, lineno)
    #print("CURRENT:", currentToken, lineno)
    return currentToken, tokenString, lineno

#f = open('prueba.tny', 'r')
##f = open('sample.tny', 'r')
#program = f.read() # lee todo el archivo a compilar
#programLength = len(program) # original program length
#program = program + '$' # add a character to represente EOF
#position = 0 # the position of the current char in file