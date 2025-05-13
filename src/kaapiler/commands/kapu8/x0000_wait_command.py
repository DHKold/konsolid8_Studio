from ..command import KaaCommand

class WaitCommand(KaaCommand):
    """Wait command.
    
    # Opcode (1B):
    - 0000aaaa : opcode (4b) + waitCount (4b)

    Note: The opcode 0x0F is for the SYNC command. Opcode 0x00 is a equivalent to a NOOP (No Operation) command.

    # Description:
    Suspend the exection of commands for a specified number of cycles (0-14) starting next cycle since the WAIT command takes 1 cycle to be treated.
    
    # Parameters:
    - waitCount (4bit unsigned int): Number of APU cycles to wait (0-14). ! 15 is not allowed, it switches to the SYNC command.

    # APU (Audio Processing Unit) pseudo code:
    MOV APU.NOOP_COUNTER, [AIP]{3:0}
    MOV APU.NOOP_SYNC, 0
    INC AIP, 1
    END CYCLE

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
    OPSIZE = 1
    MNEMONIC = "WAIT"
    MNEMONIC_NOOP = "NOOP"  # No Operation

    def __init__(self, waitCount: int = 0):
        assert 0 <= waitCount <= 0x0E, "waitCount must be between 0 and 14 (4 bits)"
        self.waitCount = waitCount

    def encode(self) -> bytes:
        return bytes([
            (self.OPCODE << 4) | (self.waitCount & 0x0F),  # aaaabbbb : aaaa = opcode, bbbb = waitCount
        ])
    
    def __str__(self) -> str:
        if self.waitCount == 0:
            return self.MNEMONIC_NOOP
        return f"{self.MNEMONIC} {self.waitCount}"
    
    @classmethod
    def decode(cls, data: bytes) -> 'WaitCommand':
        assert len(data) == 1, f"Data length must be {cls.OPSIZE} byte for {cls.MNEMONIC}"
        assert (data[0] & 0xF0) == (WaitCommand.OPCODE << 4), f"Invalid opcode for {cls.MNEMONIC}"
        assert (data[0] & 0x0F) != 0x0F, "waitCount cannot be 15 (0x0F)"
        return WaitCommand(data[0] & 0x0F)
