from ..command import KaaCommand

class WaitCommand(KaaCommand):
    """Wait command.
    
    # Opcode (3B):
    - 0000aaaa : opcode (4b) + waitCount (4b)

    Note: The opcode 0x0F is for the SYNC command. Opcode 0x00 is a equivalent to a NOOP (No Operation) command.

    # Description:
    Suspend the exection of commands for a specified number of cycles (0-254) starting next cycle since the WAIT command takes 1 cycle to be treated.
    
    # Parameters:
    - waitCount (4bit unsigned int): Number of APU cycles to wait (0-254). ! 255 is not allowed, it switches to the SYNC command.

    # APU (Audio Processing Unit) pseudo code:
    MOV APU.NOOP_COUNTER, 0xFFF0 & [AIP]{3:0}
    MOV APU.NOOP_SYNC, 0

    # APU (Audio Processing Unit) related cycle pipeline:
    IF APU.NOOP_COUNTER > 0 THEN
        IF APU.NOOP_SYNC == 0 THEN
            APU.NOOP_COUNTER--
        ELIF APU.RATE_COUNTER == 0 THEN
            APU.NOOP_COUNTER--
        ENDIF
        END CYCLE
    ENDIF

    # Assembly format:
        - WAIT <waitCount>
        - NOOP                  # Wait 0
    """

    OPCODE = 0b0000  # Opcode for WAIT command

    def __init__(self, waitCount: int = 0):
        self.waitCount = waitCount

    def encode(self) -> bytes:
        return bytes([
            (self.OPCODE << 4) | (self.waitCount & 0x0F),  # aaaabbbb : aaaa = opcode, bbbb = waitCount
        ])
    
    def decode(data: bytes) -> 'WaitCommand':
        return WaitCommand(data[0] & 0x0F)
