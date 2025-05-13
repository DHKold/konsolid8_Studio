from ..commands.kapu8 import *
from ..commands import KaaCommand
from ..parser import kaaLexer, kaaParser

class KaaCompiler:
    """A simple compiler for the Kaa programming language."""

    def __init__(self, target: str = "kapu8"):
        self.target = target
        self.logger = None

    def compile(self, code: str) -> bytes:
        statements : list[tuple[str,list]] = kaaParser.parse(code, lexer=kaaLexer)
        return b"".join([self.getCommand(s).encode() for s in statements])

    def getCommand(self, statement:tuple) -> KaaCommand:
        mnemonic = statement[0].upper()
        params = statement[1]
        match mnemonic:
            case "NOOP":
                return WaitCommand()
            case "WAIT":
                return WaitCommand(params[0])
            case "SYNC":
                return SyncCommand(params[0])
            case "SET":
                return SetCommand(params[0], params[1])
            case "SETPHASE":
                return SetPhaseCommand(params[0], params[1], params[2], params[3], params[4])
            case "SETCHANNEL":
                return SetChannelCommand(params[0], params[1], params[2])
            case "LOOP":
                return LoopCommand(params[0], params[1])
            case "JUMP":
                return JumpCommand(params[0])
            case "SAVE":
                return SaveCommand(params[0])
            case "LOAD":
                return LoadCommand(params[0])
        raise NotImplementedError(f"Command {mnemonic} not implemented")
