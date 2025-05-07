class KaaCommand:

    CHANNELS = [f"CHAN{i}" for i in range(8)] + ["CHAN_ALL"]
    PHASES = [f"PHASE{i}" for i in range(16)]
    REGISTERS = {
        0: "REG_CHAN_ENABLED",
        1: "REG_CHAN_LEFT",
        2: "REG_CHAN_RIGHT",
    }
    CHANNEL_REGISTERS = {
        0: "REG_PHASE_IDS",
    }
    
    def encode(self) -> bytes:
        """Encode the command to bytes."""
        raise NotImplementedError("Subclasses must implement this method.")