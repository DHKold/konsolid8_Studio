from ..command import KaaCommand


class LoopCommand(KaaCommand):
    """Loop command.

    # Opcode format (2 bytes):
    - 0100aaaa : opcode (4 bits), loopCount higher bits (4 bits)
    - aabbbbbb : loopCount lower bits (2 bits), loopLength (6 bits)

    # Description:
    Configures a loop with a specific iteration count and length (number of commands).
    The APU will repeat the next `loopLength` commands `loopCount` times.
    Nested Loop calls overwrite the current loop configuration (no stacking).

    # Parameters:
    - loopCount (6-bit unsigned int): Number of times to repeat the loop (0-63).
    - loopLength (6-bit unsigned int): Number of commands to include in the loop (0-63).

    # APU pseudo code:
    MOV APU.LOOP.ADDRESS, AIP + 2                           # Set the loop address to the next command
    MOV APU.LOOP.COUNT, ([AIP]{3:0} << 2) | [AIP+1]{7:6}    # Set the loop count (0-63)
    MOV APU.LOOP.LENGTH, [AIP+1]{5:0}                       # Set the loop length (0-63)
    MOV APU.LOOP.CURRENT, [AIP+1]{5:0}                      # Reset the current loop counter
    INC AIP, 2
    END CYCLE

    # APU (Audio Processing Unit) pseudo code executed at the beginning of each cycle:
    IF APU.LOOP.COUNT > 0 THEN                              # There is a loop in progress
        IF APU.LOOP.CURRENT == 0 THEN                       # End of the loop-cycle
            APU.LOOP.CURRENT = APU.LOOP.LENGTH              # Reset the command counter
            APU.LOOP.COUNT = APU.LOOP.COUNT - 1             # Decrement the loop count
            AIP = APU.LOOP.ADDRESS                          # Jump to the loop address
        ENDIF
        DEC APU.LOOP.CURRENT, 1
    ENDIF

    # Assembly format:
        - LOOP <loopCount>, <loopLength>
    """

    OPCODE = 0b0100
    COMMAND_LENGTH = 2
    COMMAND_NAME = "LOOP"

    def __init__(self, loopCount: int = 0, loopLength: int = 0):
        assert 0 <= loopCount <= 0x3F, "loopCount must be between 0 and 63 (6 bits)"
        assert 0 <= loopLength <= 0x3F, "loopLength must be between 0 and 63 (6 bits)"
        self.loopCount = loopCount
        self.loopLength = loopLength

    def encode(self) -> bytes:
        return bytes([
            (self.OPCODE << 4) | ((self.loopCount >> 2) & 0x0F),
            ((self.loopCount & 0x03) << 6) | (self.loopLength & 0x3F),
        ])

    def __str__(self) -> str:
        return f"{self.COMMAND_NAME} {self.loopCount}, {self.loopLength}"

    def __repr__(self) -> str:
        return f"LoopCommand(loopCount={self.loopCount}, loopLength={self.loopLength})"

    @classmethod
    def decode(cls, data: bytes) -> 'LoopCommand':
        assert len(data) == cls.COMMAND_LENGTH, f"Data length must be {cls.COMMAND_LENGTH} bytes for {cls.COMMAND_NAME}"
        assert (data[0] >> 4) == cls.OPCODE, f"Invalid opcode for {cls.COMMAND_NAME}"
        loopCount = ((data[0] & 0x0F) << 2) | ((data[1] >> 6) & 0x03)
        loopLength = data[1] & 0x3F
        return cls(loopCount, loopLength)
