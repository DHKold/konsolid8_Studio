import ply.yacc as yacc

from .kaa_lexer import tokens

def p_program(p):
    '''program : statement_list'''
    p[0] = p[1]

def p_statement_list(p):
    '''statement_list : statement_list EOL statement
                      | statement'''
    if len(p) == 4:
        p[0] = p[1]
        if p[3] != None:
            p[0].append(p[3])
    else:
        p[0] = []
        if p[1] != None:
            p[0].append(p[1])

def p_statement(p):
    '''statement : OPCODE parameter_list
                 | OPCODE
                 | empty'''
    if len(p) == 3:
        p[0] = (p[1], p[2])
    elif len(p) == 2 and p[1] != None:
        p[0] = (p[1], [])
    else:
        p[0] = None

def p_empty(p):
    '''empty :'''
    p[0] = None

def p_parameter_list(p):
    '''parameter_list : parameter_list SEP parameter
                      | parameter'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_parameter(p):
    '''parameter : NUMBER
                 | ID_CHANNEL
                 | ID_PHASE
                 | ID_REGISTER'''
    p[0] = p[1]

# Error rule for syntax errors
def p_error(p):
    print("Syntax error at token", p)

# Build the parser
kaaParser : yacc.LRParser = yacc.yacc()