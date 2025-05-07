import ply.lex as lex

# List of token names
tokens = [
    'NUMBER',
    'IDENTIFIER',
    'OPCODE',
    'COMMA',
    'COLON',
    'LPAREN',
    'RPAREN',
    'LSQUARE',
    'RSQUARE',
    'PLUS',
    'MINUS',
    'MULTIPLY',
    'DIVIDE',
    'EQUALS',
    'HEXNUMBER',
]

# Reserved keywords
reserved = {
    'Wait': 'WAIT',
    'SetPhase': 'SETPHASE',
    'EnableChannels': 'ENABLECHANNELS',
    'SetStereoMode': 'SETSTEREOMODE',
    'SetPhaseIds': 'SETPHASEIDS',
    'SetLoop': 'SETLOOP',
    'SaveState': 'SAVESTATE',
    'LoadState': 'LOADSTATE',
}

tokens += list(reserved.values())

# Regular expression rules for simple tokens
t_COMMA = r','
t_COLON = r':'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LSQUARE = r'\['
t_RSQUARE = r'\]'
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'/'
t_EQUALS = r'='

# Regular expression for hexadecimal numbers
def t_HEXNUMBER(t):
    r'0x[0-9A-Fa-f]+'
    t.value = int(t.value, 16)
    return t

# Regular expression for decimal numbers
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Regular expression for identifiers
def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')  # Check for reserved words
    return t

# Ignored characters (spaces and tabs)
t_ignore = ' \t'

# Define a rule for newlines
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Error handling rule
def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

# Test the lexer
if __name__ == "__main__":
    data = '''
    Wait 10
    SetPhase CHAN0, 1, 255, +128, 16
    EnableChannels 0xFF
    SetStereoMode 0xF0, 0x0F
    SetPhaseIds CHAN1, 0, 15
    SetLoop 3, 10
    SaveState CHAN2
    LoadState CHAN3
    '''
    lexer.input(data)
    for tok in lexer:
        print(tok)