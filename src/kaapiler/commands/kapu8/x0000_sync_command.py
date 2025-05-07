from ..command import KaaCommand


class SyncCommand(KaaCommand):
    """Sync command.

    # Opcode (3B):
    - 00001111 : opcode (8b)
    - aaaaaaaa : waitCount lower byte (8b)
    - bbbbbbbb : waitCount higher byte (8b)

    # Description:
    Suspend the exection of commands for a specified number of Sampling Pulse (0-65k) starting next cycle since the SYNC command takes 1 cycle to be treated.

    # Parameters:
    - waitCount (16bit unsigned int): Number of Sampling Pulse to wait (0-65k).

    # APU (Audio Processing Unit) pseudo code:
    MOV APU.NOOP_COUNTER, ([AIP+2] << 8) & [AIP+1]
    MOV APU.NOOP_SYNC, 1
    INC AIP, 3
    END CYCLE

    # APU (Audio Processing Unit) pseudo code executed at the beginning of each cycle:
    IF APU.NOOP_COUNTER > 0 THEN
        IF APU.NOOP_SYNC == 0 THEN
            APU.NOOP_COUNTER--
        ELIF APU.RATE_COUNTER == 0 THEN
            APU.NOOP_COUNTER--
        ENDIF
        END CYCLE
    ENDIF

    # Assembly format:
        - SYNC <waitCount>
    """

    OPCODE = 0b00001111  # Opcode for SYNC command
    OPSIZE = 3
    MNEMONIC = "SYNC"

    def __init__(self, waitCount: int = 0):
        self.waitCount = waitCount

    def encode(self) -> bytes:
        return bytes([
            self.OPCODE,                                # aaaaaaaa : aaaaaaaa = opcode
            (self.waitCount >> 0) & 0xFF,               # cccccccc : waitCount lower byte
            (self.waitCount >> 8) & 0xFF,               # dddddddd : waitCount higher byte
        ])
    
    def __str__(self) -> str:
        return f"{self.MNEMONIC} {self.waitCount}"
    
    @classmethod
    def decode(cls, data: bytes) -> 'SyncCommand':
        assert len(data) == 3, f"Data length must be {cls.OPSIZE} bytes for {cls.MNEMONIC}"
        assert data[0] == (SyncCommand.OPCODE), f"Invalid opcode for {cls.MNEMONIC}"
        waitCount = data[1] | (data[2] << 8)
        return SyncCommand(waitCount)
