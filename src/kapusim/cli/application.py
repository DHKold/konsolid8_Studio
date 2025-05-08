import argparse
import logging
import wave
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from pathlib import Path

from ..core.apu import Apu


class Application:
    OUTPUT_FORMAT_WAV = "wav"
    OUTPUT_FORMAT_SOUND = "sound"
    OUTPUT_FORMAT_PLOT = "plot"

    def __init__(self):
        self.logger = None

    def configure_logger(self, debug_level: str):
        logging.basicConfig(level=getattr(logging, debug_level, logging.ERROR))
        self.logger = logging.getLogger(__name__)

    def parse_arguments(self, args: list[str]) -> argparse.Namespace:
        parser = argparse.ArgumentParser(description="KAPU Simulator CLI Application")
        parser.add_argument("input_file", type=str, help="Path to the binary input file")
        parser.add_argument("-c", "--cycles", type=int, default=44100*Apu.SAMPLING_RATIO, help="Number of APU cycles to run (default: 44100x16 = 1s)")
        parser.add_argument("-f", "--output_format", type=str, choices=["wav", "sound", "plot"], default="sound", help="Output format (WAV file, SOUND playback, or PLOT waveform)")
        parser.add_argument("-o", "--output_file", type=str, default=None, help="Output filename (if WAV format is used)")
        parser.add_argument("-r", "--sample_rate", type=int, default=44100, help="Sample rate for audio (default: 44100)")
        parser.add_argument("-d", "--debug_level", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], default="ERROR", help="Debugging level")
        parsed_args = parser.parse_args(args)
        if self.logger:
            self.logger.debug(f"Parsed arguments: {parsed_args}")
        return parsed_args

    def read_input_file(self, input_file: str) -> bytes:
        input_path = Path(input_file)
        if not input_path.exists():
            self.logger.error(f"Input file '{input_file}' does not exist.")
            raise FileNotFoundError(f"Input file '{input_file}' does not exist.")
        with input_path.open("rb") as f:
            return f.read()

    def run_apu(self, data: bytes, cycles: int) -> list[tuple[int, int]]:
        apu = Apu()
        return apu.run(data, cycles)

    def write_wav_file(self, samples: list[tuple[int, int]], output_file: str, sample_rate: int):
        with wave.open(output_file, "w") as wav_file:
            wav_file.setnchannels(2)  # Stereo
            wav_file.setsampwidth(1)  # 8-bit samples
            wav_file.setframerate(sample_rate)
            wav_data = bytearray()
            for left, right in samples:
                wav_data.append(left)
                wav_data.append(right)
            wav_file.writeframes(wav_data)
        self.logger.info(f"WAV file written to '{output_file}'.")

    def play_sound(self, samples: list[tuple[int, int]], sample_rate: int):
        left = np.array([(s[0] - 128) / 128 for s in samples], dtype=np.float32)
        right = np.array([(s[1] - 128) / 128 for s in samples], dtype=np.float32)
        stereo = np.stack([left, right], axis=1)
        self.logger.info("Playing sound...")
        sd.play(stereo, samplerate=sample_rate)
        sd.wait()

    def plot_waveform(self, samples: list[tuple[int, int]]):
        left = np.array([(s[0] - 128) / 128 for s in samples], dtype=np.float32)
        right = np.array([(s[1] - 128) / 128 for s in samples], dtype=np.float32)

        plt.figure(figsize=(10, 4))
        plt.plot(left, label="Left Channel", linewidth=1.0)
        plt.plot(right, label="Right Channel", linewidth=1.0)
        plt.title("Waveform")
        plt.xlabel("Sample Index")
        plt.ylabel("Amplitude")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def run(self, args: list[str]):
        try:
            arguments = self.parse_arguments(args)
            self.configure_logger(arguments.debug_level)
            input_data = self.read_input_file(arguments.input_file)
            samples = self.run_apu(input_data, arguments.cycles)

            if arguments.output_format == self.OUTPUT_FORMAT_WAV:
                if not arguments.output_file:
                    raise ValueError("Output filename must be specified for WAV format.")
                self.write_wav_file(samples, arguments.output_file, arguments.sample_rate)
            elif arguments.output_format == self.OUTPUT_FORMAT_SOUND:
                self.play_sound(samples, arguments.sample_rate)
            elif arguments.output_format == self.OUTPUT_FORMAT_PLOT:
                self.plot_waveform(samples)
            else:
                self.logger.error(f"Unsupported output format: {arguments.output_format}")
                raise ValueError(f"Unsupported output format: {arguments.output_format}")
        except Exception as e:
            if self.logger:
                self.logger.error(f"An error occurred: {e}")
            raise e