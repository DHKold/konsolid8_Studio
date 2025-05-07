from .apu_channel_phase import ApuChannelPhase


class ApuChannelState:
    def __init__(self):
        self.enabled = 0
        self.left = 0
        self.right = 0
        self.phases = [None] * 16
        self.phaseMaxId = 0
        self.phaseActiveId = 0
        self.phaseActive: ApuChannelPhase = None
        self.phaseCountdown = 0
        self.amplitude = 0

    def __str__(self):
        phasesStr = ", ".join(p.__str__() for p in self.phases if p != None)
        return f"ChannelState#{id(self)}(enabled={self.enabled}, stereo={self.left}{self.right}, phases=#{id(self.phases)}[{phasesStr}])"
