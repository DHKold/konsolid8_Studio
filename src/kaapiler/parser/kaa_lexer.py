import re
import ply.lex as lex

# Lexer for KAA (Konsolid8 Audio Assembly) language
# This lexer is designed to tokenize the KAA assembly language used in the Konsolid8 audio engine.
#
# Following commands are supported:
# - Noop
# - Wait <number>
# - Sync <number>
# - Set <channelId>, <registerId>, <number>
# - SetChannel <channelId>, <registerId>, <number>
# - SetPhase <channelId>, <phaseId>, <number>, <number>, <number>
# - Loop <number>, <number>
# - Jump <number>
# - SaveState
# - LoadState
# 
# The lexer will recognize the following tokens:
# - NUMBER:                             : 0b[01]+ | 0o[0-7]+ | [0-9]+(e[0-9]+) | 0x[0-9A-Fa-f]+
# - ID_CHANNEL:     (case insensitive)  : CHAN[0-7] | CHAN_ALL
# - ID_PHASE:       (case insensitive)  : PHASE[0-7]
# - ID_REGISTER:    (case insensitive)  : REG_CHAN_ENABLED | REG_CHAN_LEFT | REG_CHAN_RIGHT | REG_PHASE_IDS
# - OPCODE:         (case insensitive)  : WAIT | NOOP | SYNC | SET | SETPHASE | SETCHANNEL | LOOP | JUMP | SAVE | LOAD
# - SEP:                                : ,
# - EOL:                                : (\n|\r\n)+
# 

# List of tokens
tokens = [
    'NUMBER',
    'ID_CHANNEL',
    'ID_PHASE',
    'ID_REGISTER',
    'OPCODE',
    'SEP',
    'EOL',
]

# Ignored (spaces, tabs and comments)
t_ignore = ' \t'  # Ignore spaces and tabs
t_ignore_COMMENT = r'\#.*'  # Ignore comments

# Regular expression rules for simple tokens
t_SEP = r','

# End of line tokens
def t_EOL(t:lex.LexToken):
    r'(\n|\r\n)+'
    t.type = 'EOL'
    kaaLexer.lineno += t.value.count('\n')
    t.value = '\n'  # Normalize to a single newline character
    return t

# Binary numbers (can have underscores for readability)
def t_NUMBER_BINARY(t):
    r'0b[01][01_]+'
    t.type = 'NUMBER'
    t.value = int(t.value.replace('_', ''), 2)  # Convert binary to integer
    return t

# Octal numbers
def t_NUMBER_OCTAL(t):
    r'0o[0-7]+'
    t.type = 'NUMBER'
    t.value = int(t.value, 8)  # Convert octal to integer
    return t

# Hexadecimal numbers
def t_NUMBER_HEXADECIMAL(t):
    r'0x[0-9A-Fa-f]+'
    t.type = 'NUMBER'
    t.value = int(t.value, 16)  # Convert hexadecimal to integer
    return t

# Decimal numbers
def t_NUMBER_DECIMAL(t):
    r'[+-]?[0-9]+(e[0-9]+)?'
    t.type = 'NUMBER'
    t.value = int(float(t.value))  # Convert decimal to integer
    return t

# Opcode
def t_OPCODE(t):
    r'(NOOP|WAIT|SYNC|SETPHASE|SETCHANNEL|SET|LOOP|JUMP|SAVE|LOAD)'
    t.type = 'OPCODE'
    t.value = t.value.upper()  # Normalize to uppercase
    return t

# ChannelId (value is the channel number, or 8 for CHAN_ALL)
def t_ID_CHANNEL(t):
    r'(CHAN[0-7]|CHAN_ALL)'
    t.type = 'ID_CHANNEL'
    if t.value.upper() == 'CHAN_ALL':
        t.value = 8
    else:
        t.value = int(t.value[4])  # Extract the channel number
    return t

# PhaseId (value is the phase number)
def t_ID_PHASE(t):
    r'(PHASE1[0-5]|PHASE[0-9])'
    t.type = 'ID_PHASE'
    t.value = int(t.value[5:])  # Extract the phase number
    return t

# RegisterId (value is the register number)
def t_ID_REGISTER(t):
    r'(REG_CHAN_ENABLED|REG_CHAN_LEFT|REG_CHAN_RIGHT|REG_PHASE_IDS)'
    t.type = 'ID_REGISTER'
    register_map = {
        # Global APU registers
        'REG_CHAN_ENABLED': 0,
        'REG_CHAN_LEFT': 1,
        'REG_CHAN_RIGHT': 2,
        # Channel registers
        'REG_PHASE_IDS': 0,
    }
    t.value = register_map[t.value.upper()]
    return t

# Error handling rule
def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)

# Build the lexer
kaaLexer : lex.Lexer = lex.lex(reflags=re.IGNORECASE)  # Create the lexer with case insensitive matching