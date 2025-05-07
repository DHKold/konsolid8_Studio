from ..command import KaaCommand


class SetPhaseCommand(KaaCommand):
    """SetPhase command.

    # Opcode (5B):
    - 0010aaaa : opcode (4b) + channelId (4b)
    - bbbbcddd : phaseId (4b) + phaseWay (1b) + phaseLength high bits (3b)
    - dddddddd : phaseLength low bits (8b)
    - eeeeeeee : phaseHeight (8b)
    - ffffffff : phaseCount (8b)

    # Description:
    Configures a phase for a specific channel in the APU.

    # Parameters:
    - channelId     (4bit unsigned int)     : ID of the target channel (0-15).
    - phaseId       (4bit unsigned int)     : ID of the phase to configure.
    - stepWay       (1bit)                  : Direction of the phase (0 for DOWN, 1 for UP).
    - stepLength    (11bit unsigned int)    : Length of each step.
    - stepHeight    (8bit unsigned int)     : Height of each step. Combined with the stepWay to produce a [-255, 255] range.
    - stepCount     (8-bit unsigned int)    : Number of steps for the phase.

    # Assembly format:
        - SETPHASE <channelId>, <phaseId>, <phaseLength>, <signed phaseHeight>, <phaseCount>


    # APU (Audio Processing Unit) pseudo code:
    SEL CHANNEL.ID <= [AIP]{3:0}                                        # Select the channel by ID
    SEL CHANNEL.PHASE.ID <= [AIP+1]{7:4}                                # Select the phase by ID
    MOV CHANNEL.PHASE.STEP_LENGTH, ([AIP+1]{2:0} << 8) + [AIP+2]        # Set the steps length
    MOV CHANNEL.PHASE.STEP_WAY, [AIP+1]{3}                              # Set the steps height
    MOV CHANNEL.PHASE.STEP_HEIGHT, [AIP+3]                              # Set the steps height
    MOV CHANNEL.PHASE.STEP_COUNT, [AIP+4]                               # Set the steps count
    INC AIP, 5
    END CYCLE

    # Assembly format:
    - SETPHASE <channelId>, <phaseId>, <phaseLength>, <signed phaseHeight>, <phaseCount>

    Note: Constants available are CHAN0 to CHAN5 and PHASE0 to PHASE15
    """

    OPCODE = 0b0010  # Opcode for SetPhase command
    OPSIZE = 5
    MNEMONIC = "SETPHASE"

    def __init__(self, channelId: int = 0, phaseId: int = 0, stepLength: int = 0, stepHeight: int = 0, stepCount: int = 0):
        assert 0 <= channelId <= 0x0F, "channelId must be between 0 and 15 (4 bits)"
        assert 0 <= phaseId <= 0x0F, "phaseId must be between 0 and 15 (4 bits)"
        assert 0 <= stepLength <= 0x7FF, "stepLength must be between 0 and 2047 (11 bits)"
        assert -255 <= stepHeight <= 255, "stepHeight must be between -255 and 255 (9 bits signed)"
        assert 0 <= stepCount <= 255, "stepCount must be between 0 and 255 (8 bits)"

        self.channelId = channelId
        self.phaseId = phaseId
        self.stepWay = 0 if stepHeight < 0 else 1  # 0 for DOWN, 1 for UP
        self.stepLength = stepLength
        self.stepHeight = abs(stepHeight)
        self.stepCount = stepCount

    def encode(self) -> bytes:
        return bytes([
            (self.OPCODE << 4) | (self.channelId & 0x0F),                                           # aaaabbbb : opcode, channelId
            ((self.phaseId & 0x0F) << 4) | (self.stepWay << 3) | ((self.stepLength >> 8) & 0x07),   # ccccdeee : phaseId, stepWay, stepLength high bits
            self.stepLength & 0xFF,                                                                 # ffffffff : stepLength low bits
            self.stepHeight & 0xFF,                                                                 # gggggggg : stepHeight
            self.stepCount & 0xFF                                                                   # hhhhhhhh : stepCount
        ])
    
    def __str__(self) -> str:
        return f"{self.MNEMONIC} {KaaCommand.CHANNELS[self.channelId]}, {KaaCommand.PHASES[self.phaseId]}, {self.stepLength}, {self.stepHeight}, {self.stepCount}"
    
    def __repr__(self) -> str:
        return f"SetPhaseCommand(channelId={self.channelId}, phaseId={self.phaseId}, stepLength={self.stepLength}, stepHeight={self.stepHeight}, stepCount={self.stepCount})"
    
    @classmethod
    def decode(cls, data: bytes) -> 'SetPhaseCommand':
        assert len(data) == 5, f"Data length must be {cls.OPSIZE} bytes for {cls.MNEMONIC}"
        assert (data[0] & 0xF0) == (SetPhaseCommand.OPCODE << 4), f"Invalid opcode for {cls.MNEMONIC}"
        channelId = data[0] & 0x0F
        phaseId = (data[1] >> 4) & 0x0F
        stepWay = (data[1] >> 3) & 0x01
        stepLength = ((data[1] & 0x07) << 8) | data[2]
        stepHeight = data[3] * (1 if stepWay == 1 else -1)  # Convert to signed
        stepCount = data[4]
        return SetPhaseCommand(channelId, phaseId, stepLength, stepHeight, stepCount)