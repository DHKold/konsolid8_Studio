import math


class PhaseSteps:
    OPCODE_SET_PHASE            = 0b0010

    def __init__(self, length=1, height=1, count=1, way=1):
        self.length = length
        self.height = height
        self.count  = count
        self.way    = way

    def getCommand(self, channelId=0, phaseId=0) -> bytes:
        return bytes([
            (PhaseSteps.OPCODE_SET_PHASE << 4) | (channelId & 0xF),             # SetPhase & ChannelId,
            (phaseId << 4) | (self.way << 3) | ((self.length >> 8) & 0b111),    # PhaseId & StepWay & StepLength_H,
            (self.length & 0xFF), self.height, self.count,                      # StepLength_L, StepHeight, StepCount
        ])
    
    def findSteps(length: int, height: int, way:int, strictUnder: bool = False) -> 'PhaseSteps':
        best = None
        bestError = float("inf")

        for stepCount in range(1, 256):
            stepLength = round(length / stepCount)
            stepHeight = round(height / stepCount)

            if not (1 <= stepLength <= 2047 and 1 <= stepHeight <= 255):
                continue

            totalLength = stepLength * stepCount
            totalHeight = stepHeight * stepCount

            if strictUnder and totalLength > length:
                continue

            lengthError = abs(length - totalLength) / totalLength
            heightError = abs(height - totalHeight) / totalHeight
            smoothnessError = stepHeight / 256
            totalError = lengthError * 0.1 + heightError * 0.1 + smoothnessError

            if best is None or totalError < bestError:
                best = PhaseSteps(stepLength, stepHeight, stepCount, way)
                bestError = totalError

        return best if best else PhaseSteps(length, height, 1, way)

class Phase:
    SAMPLING_RATE               = 44100

    def __init__(self, ratio=1., way=1, amplitude=AMPLITUDE_MAX):
        self.ratio = ratio
        self.way = way
        self.amplitude = amplitude

    def getSteps(self, frequency:int) -> PhaseSteps:
        length = math.floor(Phase.SAMPLING_RATE / frequency * self.ratio)
        return PhaseSteps.findSteps(length, self.amplitude, self.way, True)

    def getCommand(self, channelId=0, phaseId=0, frequency=130) -> bytes:
        return self.getSteps(frequency).getCommand(channelId, phaseId)


class SetPhasesCommandGenerator:
    SAMPLING_RATE               = 44100
    OPCODE_SET_PHASE            = 0b0010
    OPCODE_SET_PHASE_IDS        = 0b0100

    def phaseList(channelId:int=0, frequency:int = 200, phases:list[Phase]=[], addPadding=True) -> bytes:
        # Ensure the frequency is correctly handled
        totalLength = math.floor(SetPhasesCommandGenerator.SAMPLING_RATE / frequency)
        steps = [p.getSteps(frequency) for p in phases]
        usedLength = sum(max(1,s.count) * max(1, s.length) for s in steps)
        paddingLength = totalLength - usedLength
        phaseCount = min(15, len(phases) - 1)
        print(f'Need {totalLength} ({phaseCount+1} phases), used {usedLength}, padding would by {paddingLength} (enabled={addPadding})')

        # Generate all commands
        phasesCommands = [s.getCommand(channelId, i) for i, s in enumerate(steps)]
        paddingCommand = []
        if addPadding and paddingLength > 0:
            paddingCommand = [PhaseSteps(paddingLength, 0, 1, 0).getCommand(channelId, phaseCount)]
        endCommand = bytes([
            (SetPhasesCommandGenerator.OPCODE_SET_PHASE_IDS << 4) | (channelId & 0xF),      # SetPhaseIds & ChannelId,
            (phaseCount << 4) | phaseCount                                                  # ActivePhaseId & MaxPhaseId
        ])
        return b''.join(phasesCommands + paddingCommand + [endCommand])

    def triangle(channelId:int=0, frequency:int=130, symetry: float=0.5) -> bytes:
        return SetPhasesCommandGenerator.phaseList(channelId, frequency, [
            Phase(symetry, 1, 255), Phase(1-symetry, 0, 255)
        ])

    def square(channelId:int=0, frequency:int=130, duty: float=0.5) -> bytes:
        return SetPhasesCommandGenerator.phaseList(channelId, frequency, [
            Phase(0, 1, 255), Phase(duty, 0, 0), Phase(0, 0, 255), Phase(1-duty, 0, 0)
        ])

class CommandGenerator:
    SAMPLING_RATE           = 44100
    OPCODE_WAIT_LONG        = 0b0001
    OPCODE_SET_ENABLED      = 0b00111000
    OPCODE_SET_STEREO       = 0b00111001
    OPCODE_SET_JUMP         = 0b0101

    PARAM_ENABLE_ALL        = 255
    PARAM_ENABLE_NONE       = 0
    PARAM_ENABLE_CHAN0      = 1
    PARAM_ENABLE_CHAN1      = 2
    PARAM_ENABLE_CHAN2      = 4
    PARAM_ENABLE_CHAN3      = 8
    PARAM_ENABLE_CHAN4      = 16
    PARAM_ENABLE_CHAN5      = 32
    PARAM_ENABLE_CHAN6      = 68
    PARAM_ENABLE_CHAN7      = 128

    PARAM_STEREO_NONE       = 0b00
    PARAM_STEREO_LEFT       = 0b01
    PARAM_STEREO_RIGHT      = 0b10
    PARAM_STEREO_BOTH       = 0b11

    def waitLong(duration: float = 0) -> bytes:
        totalLength = math.ceil(CommandGenerator.SAMPLING_RATE * duration)
        return bytes([
            (CommandGenerator.OPCODE_WAIT_LONG << 4) | (totalLength >> 8),
            (totalLength & 0xFF)
        ])
    
    def setEnabled(flags: bytes) -> bytes:
        return bytes([
            (CommandGenerator.OPCODE_SET_ENABLED), flags
        ])
    
    def setStereo(chan0 = PARAM_STEREO_BOTH, chan1 = PARAM_STEREO_BOTH, chan2 = PARAM_STEREO_BOTH, chan3 = PARAM_STEREO_BOTH, 
                  chan4 = PARAM_STEREO_BOTH, chan5 = PARAM_STEREO_BOTH, chan6 = PARAM_STEREO_BOTH, chan7 = PARAM_STEREO_BOTH ) -> bytes:
        return bytes([
            (CommandGenerator.OPCODE_SET_STEREO),
            (chan0 << 0) | (chan1 << 2) | (chan2 << 4)| (chan3 << 5),
            (chan4 << 0) | (chan5 << 2) | (chan6 << 4)| (chan7 << 5)
        ])
    
    def setJump(jumpCount:int, jumpLength:int=1) -> bytes:
        return bytes([
            (CommandGenerator.OPCODE_SET_JUMP << 4) | ((jumpCount >> 2) & 0b1111),   # SetJump <4b:COUNTER_H>
            (jumpCount & 0b11 << 6) | (jumpLength & 0b111111)                        # <2b:COUNTER_L> <6b:LENGTH>
        ])


################## Demo Data #####################
data: bytes = bytes().join([
    SetPhasesCommandGenerator.triangle(0, 50, 1.0),
    SetPhasesCommandGenerator.triangle(1, 440, 0.5),
    SetPhasesCommandGenerator.square(2, 220, 0.5),
    CommandGenerator.setEnabled(CommandGenerator.PARAM_ENABLE_CHAN0 | CommandGenerator.PARAM_ENABLE_CHAN1 | CommandGenerator.PARAM_ENABLE_CHAN2),
    CommandGenerator.waitLong(0),
])

data: bytes = bytes().join([
    # --- Motif de 4 secondes ---
    SetPhasesCommandGenerator.triangle(0, 440, 0.5),     # La (A4)
    SetPhasesCommandGenerator.triangle(1, 494, 0.5),     # Si (B4)
    SetPhasesCommandGenerator.square(2, 220, 0.5),       # Basse La (A3)

    CommandGenerator.setStereo(
        CommandGenerator.PARAM_STEREO_BOTH,  # Chan 0
        CommandGenerator.PARAM_STEREO_BOTH,  # Chan 1
        CommandGenerator.PARAM_STEREO_LEFT,  # Chan 2 (Basse un peu à gauche)
    ),
    CommandGenerator.setEnabled(
        CommandGenerator.PARAM_ENABLE_CHAN0 | 
        CommandGenerator.PARAM_ENABLE_CHAN1 | 
        CommandGenerator.PARAM_ENABLE_CHAN2
    ),
    CommandGenerator.waitLong(0.25),

    SetPhasesCommandGenerator.triangle(0, 392, 0.5),     # Sol (G4)
    SetPhasesCommandGenerator.triangle(1, 440, 0.5),     # La (A4)
    SetPhasesCommandGenerator.square(2, 196, 0.5),       # Basse Sol (G3)
    CommandGenerator.waitLong(0.25),

    SetPhasesCommandGenerator.triangle(0, 349, 0.5),     # Fa (F4)
    SetPhasesCommandGenerator.triangle(1, 392, 0.5),     # Sol (G4)
    SetPhasesCommandGenerator.square(2, 175, 0.5),       # Basse Fa (F3)
    CommandGenerator.waitLong(0.25),

    SetPhasesCommandGenerator.triangle(0, 330, 0.5),     # Mi (E4)
    SetPhasesCommandGenerator.triangle(1, 349, 0.5),     # Fa (F4)
    SetPhasesCommandGenerator.square(2, 165, 0.5),       # Basse Mi (E3)
    CommandGenerator.waitLong(0.25),

    # --- On boucle 4 fois le motif précédent (4 x 4s = 16s) ---
    CommandGenerator.setJump(jumpCount=3, jumpLength=16),  # Jump back over 16 instructions, repeat 4 times

    # --- Petite variation finale (4s) ---
    SetPhasesCommandGenerator.triangle(0, 494, 0.5),     # Si (B4)
    SetPhasesCommandGenerator.triangle(1, 523, 0.5),     # Do (C5)
    SetPhasesCommandGenerator.square(2, 247, 0.5),       # Basse Si (B3)
    CommandGenerator.waitLong(0.5),

    SetPhasesCommandGenerator.triangle(0, 440, 0.5),     # La (A4)
    SetPhasesCommandGenerator.triangle(1, 494, 0.5),     # Si (B4)
    SetPhasesCommandGenerator.square(2, 220, 0.5),       # Basse La (A3)
    CommandGenerator.waitLong(0.5),

    SetPhasesCommandGenerator.triangle(0, 392, 0.5),     # Sol (G4)
    SetPhasesCommandGenerator.triangle(1, 440, 0.5),     # La (A4)
    SetPhasesCommandGenerator.square(2, 196, 0.5),       # Basse Sol (G3)
    CommandGenerator.waitLong(0.5),

    SetPhasesCommandGenerator.triangle(0, 440, 0.5),     # La (A4) - note finale
    SetPhasesCommandGenerator.triangle(1, 659, 0.5),     # Mi (E5)
    SetPhasesCommandGenerator.square(2, 220, 0.5),       # Basse La (A3)
    CommandGenerator.waitLong(1.0),

    # Fade out / silence
    CommandGenerator.setEnabled(CommandGenerator.PARAM_ENABLE_NONE),
])

################## TESTING THE LIBRARY #################
import numpy as np
import sounddevice as sd

print("🧠 Decoding APU binary and playing...")
apu = CustomAPU()
apu.channels = [Channel() for _ in range(8)]
samples = apu.run(data, CLOCK_HZ*25)
left = np.array([(s[0] - 128) / 128 for s in samples])
right = np.array([(s[1] - 128) / 128 for s in samples])
stereo = np.stack([left, right], axis=1).astype(np.float32)

print(f'Playing sound ({len(samples)} samples)...')
sd.play(stereo, samplerate=SAMPLE_RATE)
sd.wait(False)
print(f"✅ Done.")


################### DISPLAY #########################
import matplotlib.pyplot as plt

display = True
if (display):
    plt.figure(figsize=(10, 3))
    plt.plot(left[0:2000], linewidth=1.0)
    plt.plot(right[0:2000], linewidth=1.0)
    plt.title("Waveform")
    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.tight_layout()
    plt.show()