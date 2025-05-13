from ..command import KaaCommand


class SaveCommand(KaaCommand):
    """Save command.

    # Opcode format (1 byte):
    - 0110aaaa : opcode (4 bits), channelId (4 bits)

    # Description:
    Saves the current state of the specified channel into its save register.
    Useful for pausing a channel's state to allow temporary playback of other audio.

    # Parameters:
    - channelId (4-bit unsigned int): ID of the target channel.

    # APU pseudo code:
    SEL CHANNEL.ID <= [AIP]{3:0}         # Select the channel
    MOV CHANNEL.SAVE_REGISTER <= CHANNEL.STATE
    INC AIP, 1
    END CYCLE

    # Assembly format:
        - SAVE <channelId>

        Note: Constants available for the channelId are CHAN0 to CHAN7 or CHAN_ALL.
    """

    OPCODE = 0b0110
    OPSIZE = 1
    MNEMONIC = "SAVE"

    def __init__(self, channelId: int = 0):
        assert 0 <= channelId <= 0x0F, "channelId must be between 0 and 15 (4 bits)"
        self.channelId = channelId

    def encode(self) -> bytes:
        return bytes([
            (self.OPCODE << 4) | (self.channelId & 0x0F),
        ])

    def __str__(self) -> str:
        return f"{self.MNEMONIC} {KaaCommand.CHANNELS[self.channelId]}"

    def __repr__(self) -> str:
        return f"SaveCommand(channelId={self.channelId})"

    @classmethod
    def decode(cls, data: bytes) -> 'SaveCommand':
        assert len(data) == cls.OPSIZE, f"Data length must be {cls.OPSIZE} bytes for {cls.MNEMONIC}"
        assert (data[0] >> 4) == cls.OPCODE, f"Invalid opcode for {cls.MNEMONIC}"
        channelId = data[0] & 0x0F
        return cls(channelId)
