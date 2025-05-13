from ..command import KaaCommand


class SetCommand(KaaCommand):
    """Set command.
    
    # Opcode (2B):
    - aaaabbbb : opcode (4b), registerId (4b)
    - cccccccc : value (8b)

    # Description:
    Set the value of a specific public register in the APU.

    # Parameters:
    - value (8bit): Value to set in the register.

    # APU (Audio Processing Unit) pseudo code:
    SEL APU.REGISTER.ID <= [AIP]{3:0}   # Select the register by ID
    MOV APU.REGISTER_VALUE, [AIP+1]     # Set the register value
    INC AIP, 2
    END CYCLE

    # Assembly format:
        - SET <registerId>, <value>

        Note: Constants available for the registerId:
            - REG_CHAN_ENABLED = 0 : Channel enabled register, value is an enabling bitmask, each bit (LSB to MSB) corresponds to a channel (0-7).
            - REG_CHAN_LEFT = 1, REG_CHAN_RIGHT = 2 : Channel left/right enabled register, value is an enabling bitmask, each bit (LSB to MSB) corresponds to a channel (0-7).
    """

    OPCODE = 0b0001  # Opcode for SetChannelEnabled command
    OPSIZE = 2
    MNEMONIC = "SET"

    def __init__(self, registerId: int = 0, value: int = 0):
        assert 0 <= registerId <= 0x0F, "registerId must be between 0 and 15 (4 bits)"
        assert 0 <= value <= 0xFF, "value must be between 0 and 255 (8 bits)"
        self.registerId = registerId
        self.value = value

    def encode(self) -> bytes:
        return bytes([
            (self.OPCODE << 4) | self.registerId,       # aaaabbbb : opcode, registerId
            self.value & 0xFF,                          # cccccccc : value
        ])
    
    def __str__(self) -> str:
        return f"SET {KaaCommand.REGISTERS[self.registerId]}, {self.value}"
    
    def __repr__(self) -> str:
        return f"SetCommand(registerId={self.registerId}, value={self.value})"
    
    @classmethod
    def decode(cls, data: bytes) -> 'SetCommand':
        assert len(data) == 2, f"Data length must be {cls.OPSIZE} bytes for {cls.MNEMONIC}"
        assert data[0] >> 4 == SetCommand.OPCODE, f"Invalid opcode for {cls.MNEMONIC}"
        registerId = data[0] & 0x0F
        value = data[1]
        return SetCommand(registerId, value)