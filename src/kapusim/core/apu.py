from .apu_channel import ApuChannel
from .apu_channel_phase import ApuChannelPhase
from .apu_constants import *


class Apu:
    def __init__(self):
        self.aip = 0
        self.eip = 0
        self.noopCounter = 0
        self.jumpCounter = 0
        self.jumpAddress = 0
        self.jumpCommands = 0
        self.jumpCommandsReset = 0
        self.channels: list[ApuChannel] = [ApuChannel() for _ in range(8)]
        self.mixerMode = 0

    def executeCommand(self, data: bytes):
        # NOOP
        if self.noopCounter < 0:
            return
        elif self.noopCounter > 0:
            self.noopCounter -= 1
            return

        # Jump
        if self.jumpCounter > 0:
            if self.jumpCommands == 0:
                self.aip = self.jumpAddress
                self.jumpCounter -= 1
                self.jumpCommands = self.jumpCommandsReset
            self.jumpCommands -= 1

        # Cache AIP
        aip = self.aip
        if aip >= len(data):
            aip = 0

        # Opcode and nibble
        opcode = data[aip] >> 4
        nibble = data[aip] & 15

        # Execute
        match opcode:
            # 1B Wait Short
            case 0b0000:
                waitCycles = nibble
                print(f"Wait {waitCycles} cycles")
                self.noopCounter = waitCycles * APU_CLOCK_RATIO
            # 2B Wait Long
            case 0b0001:
                waitCycles = ((nibble << 8) + data[aip + 1]) * 10
                if waitCycles == 0:
                    print("Stopping Execution")
                    self.noopCounter = -1
                else:
                    print(f"Wait {waitCycles} cycles")
                    self.noopCounter = waitCycles * APU_CLOCK_RATIO
            # 5B SetPhase<4b:channelId> <4b:phaseId> <1b:phaseWay> <11b:phaseLength> <8b:phaseHeight> <8b:phaseCount>
            case 0b0010:
                phaseId = data[aip + 1] >> 4
                newPhase = ApuChannelPhase(
                    ((data[aip + 1] & 0b111) * 256) + data[aip + 2],
                    data[aip + 3],
                    data[aip + 4],
                    -1 if (data[aip + 1] & 0b1000) == 0 else 1,
                )
                print(f"SetPhase {phaseId} of Channel #{nibble} to", newPhase)
                self.channels[nibble].state.phases[phaseId] = newPhase
                self.aip = aip + 5
            # xB SetAllChannel <4b:property>
            case 0b0011:
                match nibble:
                    # 2B SetAllChannel Enabled <8b:channelsEnabled>
                    case 0b1000:
                        print(f"SetAllChannel Enabled {data[aip+1]:08b}")
                        self.channels[0].state.enabled = (data[aip + 1] >> 0) & 1
                        self.channels[1].state.enabled = (data[aip + 1] >> 1) & 1
                        self.channels[2].state.enabled = (data[aip + 1] >> 2) & 1
                        self.channels[3].state.enabled = (data[aip + 1] >> 3) & 1
                        self.channels[4].state.enabled = (data[aip + 1] >> 4) & 1
                        self.channels[5].state.enabled = (data[aip + 1] >> 5) & 1
                        self.channels[6].state.enabled = (data[aip + 1] >> 6) & 1
                        self.channels[7].state.enabled = (data[aip + 1] >> 7) & 1
                        self.aip = aip + 2
                    # 3B SetAllChannel StereoMode <16b:channelsStereo>
                    case 0b1001:
                        print(
                            f"SetAllChannel StereoMode {data[aip+1]:08b} {data[aip+2]:08b}"
                        )
                        self.channels[0].state.left = (data[aip + 1] >> 0) & 1
                        self.channels[0].state.right = (data[aip + 1] >> 1) & 1
                        self.channels[1].state.left = (data[aip + 1] >> 2) & 1
                        self.channels[1].state.right = (data[aip + 1] >> 3) & 1
                        self.channels[2].state.left = (data[aip + 1] >> 4) & 1
                        self.channels[2].state.right = (data[aip + 1] >> 5) & 1
                        self.channels[3].state.left = (data[aip + 1] >> 6) & 1
                        self.channels[3].state.right = (data[aip + 1] >> 7) & 1
                        self.channels[4].state.left = (data[aip + 2] >> 0) & 1
                        self.channels[4].state.right = (data[aip + 2] >> 1) & 1
                        self.channels[5].state.left = (data[aip + 2] >> 2) & 1
                        self.channels[5].state.right = (data[aip + 2] >> 3) & 1
                        self.channels[6].state.left = (data[aip + 2] >> 4) & 1
                        self.channels[6].state.right = (data[aip + 2] >> 5) & 1
                        self.channels[7].state.left = (data[aip + 2] >> 6) & 1
                        self.channels[7].state.right = (data[aip + 2] >> 7) & 1
                        self.aip = aip + 3
            # 2B SetPhaseIds<4b:channelId> <4b:CurentPhaseId> <4b:phaseMaxId>
            case 0b0100:
                print(
                    f"SetPhaseIds of Channel #{nibble} to {data[aip+1] >> 4} / {data[aip+1] & 0x0F}"
                )
                self.channels[nibble].state.phaseMaxId = data[aip + 1] & 0x0F
                self.channels[nibble].setPhaseActiveId(data[aip + 1] >> 4)
                self.aip = aip + 2
            # 2B SetLoop <6b:Count> <6b:Length>
            case 0b0101:
                self.jumpCounter = (nibble << 4) + (data[aip + 1] >> 6)
                self.jumpCommands = data[aip] & 0b111111
                self.jumpCommandsReset = self.jumpCommands
                self.jumpAddress = aip + 2
                print(
                    f"SetLoop jump at @{self.jumpAddress} after {self.jumpCommands} commands, {self.jumpCounter} times"
                )
                self.aip = aip + 2
            case _:
                print("Wrong opcode, ignored")

    def run(self, data: bytes, cycles=1):
        samples = []
        while cycles > 0:
            self.executeCommand(data)
            # One sample every 16 Cycle
            if cycles % 16 == 0:
                samples.append(
                    self.combine_samples([c.sample() for c in self.channels])
                )
            # Next cycle
            cycles -= 1
        return samples

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
