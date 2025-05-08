from .apu_channel import ApuChannel
from .apu_channel_phase import ApuChannelPhase
from .apu_constants import *


class Apu:
    SAMPLING_RATIO = 16

    def __init__(self):
        self.aip = 0
        self.eip = 0
        self.samplingCounter = 0

        self.noopCounter = 0
        self.noopSynced = False

        self.loopAddress = 0            # LOOP: Address the loop starts from
        self.loopCountdown = 0          # LOOP: How lany times to loop
        self.loopLength = 0             # LOOP: How many commands to loop
        self.loopCommandCountdown = 0   # LOOP: How many commands left before the loop ends

        self.channels: list[ApuChannel] = [ApuChannel() for _ in range(8)]

        self.mixerMode = 0

    def executeCommand(self, data: bytes):
        # NOOP
        if self.noopCounter < 0:
            return
        elif self.noopCounter > 0:
            if (not self.noopSynced) or (self.samplingCounter == 0):
                self.noopCounter -= 1
            return

        # Jump
        if self.loopCountdown > 0:
            if self.loopCommandCountdown == 0:
                self.aip = self.loopAddress
                self.loopCountdown -= 1
                self.loopCommandCountdown = self.loopLength
            self.loopCommandCountdown -= 1

        # Execute
        match (data[self.aip] >> 4):
            case 0b0000:
                if (data[self.aip] & 0x0F) != 0b1111:
                    self.exec_wait(data)
                else:
                    self.exec_sync(data)
            case 0b0001:
                self.exec_set(data)
            case 0b0010:
                self.exec_setPhase(data)
            case 0b0011:
                self.exec_setChannel(data)
            case 0b0100:
                self.exec_loop(data)
            case 0b0101:
                self.exec_jump(data)
            case 0b0110:
                self.exec_save(data)
            case 0b0111:
                self.exec_load(data)
            case _:
                print(f"Unknown command {data[aip]:08b}, panic mode")
                raise Exception("Unknown command")
        
        # Ensure AIP is within bounds
        if self.aip >= len(data):
            print(f"Command pointer out of bounds @{self.aip:03x}, resetting to 0")
            self.aip = 0

    def exec_wait(self, data: bytes):
        waitCycles = data[self.aip] & 0x0F
        print(f"Wait {waitCycles} cycles")
        self.noopCounter = waitCycles
        self.noopSynced = False
        self.aip += 1

    def exec_sync(self, data: bytes):
        syncCycles = (data[self.aip+2]<<8) | data[self.aip+1]
        print(f"Sync {syncCycles} sampling cycles")
        self.noopCounter = syncCycles
        self.noopSynced = True
        self.aip += 3

    def exec_set(self, data: bytes):
        registerId = data[self.aip] & 0x0F
        value = data[self.aip + 1]
        print(f"Set register {registerId} to {value}")
        match registerId:
            case 0b0000: # REG_CHAN_ENABLED
                self.channels[0].state.enabled = (value >> 0) & 1
                self.channels[1].state.enabled = (value >> 1) & 1
                self.channels[2].state.enabled = (value >> 2) & 1
                self.channels[3].state.enabled = (value >> 3) & 1
                self.channels[4].state.enabled = (value >> 4) & 1
                self.channels[5].state.enabled = (value >> 5) & 1
                self.channels[6].state.enabled = (value >> 6) & 1
                self.channels[7].state.enabled = (value >> 7) & 1
            case 0b0001: # REG_CHAN_LEFT
                self.channels[0].state.left = (value >> 0) & 1
                self.channels[1].state.left = (value >> 1) & 1
                self.channels[2].state.left = (value >> 2) & 1
                self.channels[3].state.left = (value >> 3) & 1
                self.channels[4].state.left = (value >> 4) & 1
                self.channels[5].state.left = (value >> 5) & 1
                self.channels[6].state.left = (value >> 6) & 1
                self.channels[7].state.left = (value >> 7) & 1
            case 0b0010: # REG_CHAN_RIGHT
                self.channels[0].state.right = (value >> 0) & 1
                self.channels[1].state.right = (value >> 1) & 1
                self.channels[2].state.right = (value >> 2) & 1
                self.channels[3].state.right = (value >> 3) & 1
                self.channels[4].state.right = (value >> 4) & 1
                self.channels[5].state.right = (value >> 5) & 1
                self.channels[6].state.right = (value >> 6) & 1
                self.channels[7].state.right = (value >> 7) & 1
            case _:
                print("Wrong registerId, ignored")
        self.aip += 2
    
    def exec_setChannel(self, data: bytes):
        channelId = data[self.aip] & 0x0F
        registerId = (data[self.aip + 1] >> 4) & 0x0F
        value = (data[self.aip + 1] & 0x0F) << 8 | data[self.aip + 2]
        print(f"SetChannel register {registerId} of Channel #{channelId} to {value}")
        match registerId:
            case 0b0000: # REG_PHASE_IDS
                activeId = (value & 0xF00) >> 8
                maxId = (value & 0x0F0) >> 4
                phaseIdShift = value & 0x00F
                self.channels[channelId].state.phaseMaxId = maxId
                self.channels[channelId].state.phaseIdShift = phaseIdShift
                self.channels[channelId].setPhaseActiveId(activeId)
                print(f"SetPhaseIds of Channel #{channelId} to {activeId}, {maxId}, {phaseIdShift}")
        self.aip += 3

    def exec_setPhase(self, data: bytes):
        channelId = data[self.aip] & 0x0F
        phaseId = (data[self.aip + 1] >> 4) & 0x0F
        newPhase = ApuChannelPhase(
            ((data[self.aip + 1] & 0b111) << 8) + data[self.aip + 2],
            data[self.aip + 3],
            data[self.aip + 4],
            -1 if (data[self.aip + 1] & 0b1000) == 0 else 1,
        )
        print(f"SetPhase {phaseId} of Channel #{channelId} to", newPhase)
        self.channels[channelId].state.phases[phaseId] = newPhase
        self.aip += 5

    def exec_loop(self, data: bytes):
        self.loopAddress = self.aip + 2
        self.loopCountdown = ((data[self.aip] & 0b1111) << 2) + (data[self.aip + 1] >> 6)
        self.loopLength = data[self.aip+1] & 0b111111
        self.loopCommandCountdown = self.loopLength
        print(f"Loop at @{self.loopAddress:03x} after {self.loopLength} commands, {self.loopCountdown} times")
        self.aip += 2

    def exec_jump(self, data: bytes):
        jumpAddress = ((data[self.aip] & 0b1111) << 8) + data[self.aip + 1]
        print(f"Jump to @{jumpAddress:03x}")
        self.aip = jumpAddress

    def exec_save(self, data: bytes):
        channelId = data[self.aip] & 0x0F
        self.channels[channelId].save_state()
        self.aip += 1

    def exec_load(self, data: bytes):
        channelId = data[self.aip] & 0x0F
        self.channels[channelId].load_state()
        self.aip += 1

    def combine_samples(self, samples: list[int]):
        # Mode 0 : Capped Sum
        match self.mixerMode:
            case 0:
                return (
                    min(sum(s[0] - APU_AMPLITUDE_DEF for s in samples) + APU_AMPLITUDE_DEF, APU_AMPLITUDE_MAX),
                    min(sum(s[1] - APU_AMPLITUDE_DEF for s in samples) + APU_AMPLITUDE_DEF, APU_AMPLITUDE_MAX),
                )
            # Mode 1 : Average
            case 1:
                return (
                    sum(s[0] for s in samples) / len(samples),
                    sum(s[1] for s in samples) / len(samples),
                )

    def run(self, data: bytes, cycles=1):
        samples = []
        while cycles > 0:
            self.executeCommand(data)
            # One sample every SAMPLING_RATIO Cycle
            if self.samplingCounter == 0:
                newSample = self.combine_samples([c.sample() for c in self.channels])
                samples.append(newSample)
                self.samplingCounter = self.SAMPLING_RATIO
            self.samplingCounter -= 1
            # Next cycle
            cycles -= 1
        return samples