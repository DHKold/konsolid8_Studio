from ..command import KaaCommand


class SetChannelCommand(KaaCommand):
    """SetChannel command.

    # Opcode (3B):
    - 0011aaaa : opcode (4b), channelId (4b)
    - bbbbcccc : registerId (4b), value higher bits (4b)
    - cccccccc : value lower bits (8b)

    # Description:
    Set the value of a specific channel register in the APU.

    # Parameters:
    - channelId (4-bit unsigned int): ID of the target channel (0-15).
    - registerId (4-bit unsigned int): ID of the register to set (0-15).
    - value (12-bit): Value to set in the channel register. Depending on the register size, the higher bits may be dropped.

    # APU (Audio Processing Unit) pseudo code:
    SEL CHANNEL.ID <= [AIP]{3:0}                                # Select the channel by ID
    SEL CHANNEL.REGISTER.ID <= [AIP+1]{7:4}                     # Select the register by ID
    MOV CHANNEL.REGISTER.VALUE, ([AIP+1]{3:0} << 8) + [AIP+2]   # Set the register value
    INC AIP, 3
    END CYCLE

    # Assembly format:
        - SETCHANNEL <channelId>, <registerId>, <value>

        Note: Constants available for the channels are CHAN0 to CHAN5
              Constants available for the registerId:
               - REG_PHASE_IDS : 12-bit register AAAABBBBCCCC, AAAA = PHASE_ACTIVE_ID, BBBB = PHASE_MAX_ID, CCCC = PHASE_ID_SHIFT.
                                 Those are used by the channel to determine the active phase of the sound and the way it will loop.
                                 The channel decrements PHASE_ACTIVE_ID at the end of the active phase (0 is 'decremented' to PHASE_MAX_ID so it loops).
                                 When loading a phase, the channel uses (PHASE_ACTIVE_ID + PHASE_ID_SHIFT) % 16.
                                 This allows to store and use phases in groups (of 1, 2, 4, 8 or 16)
    """

    OPCODE = 0b0011  # Opcode for SetChannelCommand
    COMMAND_LENGTH = 3  # Length of the command in bytes
    COMMAND_NAME = "SETCHANNEL"  # Command name

    def __init__(self, channelId: int = 0, registerId: int = 0, value: int = 0):
        assert 0 <= channelId <= 0x0F, "channelId must be between 0 and 15 (4 bits)"
        assert 0 <= registerId <= 0x0F, "registerId must be between 0 and 15 (4 bits)"
        assert 0 <= value <= 0xFFF, "value must be between 0 and 4095 (12 bits)"
        self.channelId = channelId
        self.registerId = registerId
        self.value = value

    def encode(self) -> bytes:
        return bytes([
            (self.OPCODE << 4) | (self.channelId & 0x0F),           # aaaabbbb : opcode, channelId
            (self.registerId << 4) | ((self.value >> 8) & 0x0F),    # ccccdddd : registerId, value higher bits
            self.value & 0xFF,                                      # dddddddd : value lower bits
        ])

    def __str__(self) -> str:
        return f"SETCHANNEL {KaaCommand.CHANNELS[self.channelId]}, {KaaCommand.CHANNEL_REGISTERS[self.registerId]}, {self.value}"

    def __repr__(self) -> str:
        return f"SetChannelCommand(channelId={self.channelId}, registerId={self.registerId}, value={self.value})"

    @classmethod
    def decode(cls, data: bytes) -> 'SetChannelCommand':
        assert len(data) == cls.COMMAND_LENGTH, f"Data length must be {cls.COMMAND_LENGTH} bytes for {cls.COMMAND_NAME}"
        assert (data[0] >> 4) == cls.OPCODE, f"Invalid opcode for {cls.COMMAND_NAME}"
        channelId = data[0] & 0x0F
        registerId = (data[1] >> 4) & 0x0F
        assert registerId in KaaCommand.CHANNEL_REGISTERS, "Invalid registerId for SetChannelCommand"
        value = ((data[1] & 0x0F) << 8) + data[2]
        return SetChannelCommand(channelId, registerId, value)