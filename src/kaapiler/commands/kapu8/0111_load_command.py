from ..command import KaaCommand


class LoadCommand(KaaCommand):
    """Load command.

    # Opcode format (1 byte):
    - 0110aaaa : opcode (4 bits), channelId (4 bits)

    # Description:
    Loads the current state of the specified channel ifromnto its save register.
    Useful for restoring a channel's state after temporary playback of other audio.

    # Parameters:
    - channelId (4-bit unsigned int): ID of the target channel.

    # APU pseudo code:
    SEL CHANNEL.ID <= [AIP]{3:0}         # Select the channel
    MOV CHANNEL.STATE, CHANNEL.SAVE_REGISTER
    INC AIP, 1
    END CYCLE

    # Assembly format:
        - LOAD <channelId>

        Note: Constants available for the channelId are CHAN0 to CHAN7 or CHAN_ALL.
    """

    OPCODE = 0b0111
    COMMAND_LENGTH = 1
    COMMAND_NAME = "LOAD"

    def __init__(self, channelId: int = 0):
        assert 0 <= channelId <= 0x0F, "channelId must be between 0 and 15 (4 bits)"
        self.channelId = channelId

    def encode(self) -> bytes:
        return bytes([
            (self.OPCODE << 4) | (self.channelId & 0x0F),
        ])

    def __str__(self) -> str:
        return f"{self.COMMAND_NAME} {KaaCommand.CHANNELS[self.channelId]}"

    def __repr__(self) -> str:
        return f"LoadCommand(channelId={self.channelId})"

    @classmethod
    def decode(cls, data: bytes) -> 'LoadCommand':
        assert len(data) == cls.COMMAND_LENGTH, f"Data length must be {cls.COMMAND_LENGTH} bytes for {cls.COMMAND_NAME}"
        assert (data[0] >> 4) == cls.OPCODE, f"Invalid opcode for {cls.COMMAND_NAME}"
        channelId = data[0] & 0x0F
        return cls(channelId)
