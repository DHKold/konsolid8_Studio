class JumpCommand(KaaCommand):
    """Jump command.

    # Opcode format (2 bytes):
    - 0101aaaa : opcode (4 bits), address higher bits (4 bits)
    - aaaaaaaa : address lower bits (8 bits)

    # Description:
    Jumps to a specific address. Pointed address will be the next command to be executed.

    # Parameters:
    - address (12-bit unsigned int): Address to jump to (0-4095).

    # APU pseudo code:
    MOV AIP, ([AIP]{3:0} << 8) | [AIP+1]                    # Set AIP to the jump address
    END CYCLE

    # Assembly format:
        - JUMP <address>
    """

    OPCODE = 0b0101
    COMMAND_LENGTH = 2
    COMMAND_NAME = "JUMP"

    def __init__(self, address: int = 0):
        assert 0 <= address <= 0xFFF, "address must be between 0 and 4095 (12 bits)"
        self.address = address

    def encode(self) -> bytes:
        return bytes([
            (self.OPCODE << 4) | ((self.address >> 8) & 0x0F),
            self.address & 0xFF,
        ])
    
    def __str__(self) -> str:
        return f"{self.COMMAND_NAME} 0x{self.address:03X}"
    
    def __repr__(self) -> str:
        return f"JumpCommand(address={self.address})"
    
    @classmethod
    def decode(cls, data: bytes) -> 'JumpCommand':
        assert len(data) == cls.COMMAND_LENGTH, f"Data length must be {cls.COMMAND_LENGTH} bytes for {cls.COMMAND_NAME}"
        assert (data[0] >> 4) == cls.OPCODE, f"Invalid opcode for {cls.COMMAND_NAME}"
        address = ((data[0] & 0x0F) << 8) | data[1]
        return cls(address)