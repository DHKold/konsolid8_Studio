import copy

from .apu_channel_state import ApuChannelState
from .apu_constants import *


class ApuChannel:
    def __init__(self):
        self.state = ApuChannelState()
        self.saved = self.state

    def __str__(self):
        return f"Channel#{id(self)}(state={self.state})"

    def sample(self):
        if not self.state.enabled:
            return (APU_AMPLITUDE_DEF, APU_AMPLITUDE_DEF)

        # End of the current step: Start the next
        self.state.phaseCountdown -= 1
        if self.state.phaseCountdown <= 0:
            self.state.amplitude += self.state.phaseActive.stepHeight * self.state.phaseActive.stepWay
            self.state.amplitude = min(max(self.state.amplitude, APU_AMPLITUDE_MIN), APU_AMPLITUDE_MAX)
            self.state.phaseActive.stepCount -= 1
            self.state.phaseCountdown = self.state.phaseActive.stepLength

        # No more steps, load next phase
        if self.state.phaseActive.stepCount == 0:
            if self.state.phaseActiveId == 0:  # The current phase was the last one
                self.setPhaseActiveId(self.state.phaseMaxId)  # Loop back to first phase
            else:  # The current phase is not the last one:
                self.setPhaseActiveId(self.state.phaseActiveId - 1)  # Go to next phase

        # Sampling
        return (
            self.state.amplitude * self.state.left,
            self.state.amplitude * self.state.right,
        )

    def setPhaseActiveId(self, id: int):
        self.state.phaseActiveId = id
        self.state.phaseActive = copy.deepcopy(
            self.state.phases[(self.state.phaseActiveId + self.state.phaseIdShift) % 16]
        )
        self.state.phaseCountdown = self.state.phaseActive.stepLength

    def save_state(self):
        self.saved = self.state

    def load_state(self):
        self.state = self.saved
