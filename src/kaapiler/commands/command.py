class KaaCommand:
    
    def encode(self) -> bytes:
        """Encode the command to bytes."""
        raise NotImplementedError("Subclasses must implement this method.")
    
    def decode(self, data: bytes) -> 'KaaCommand':
        """Decode bytes to a command."""
        raise NotImplementedError("Subclasses must implement this method.")