import argparse
import logging
from pathlib import Path

from utils import bytes_to_hex, bytes_to_python

from ..core import KaaCompiler


class Application:
    OUTPUT_FORMAT_HEX = "hex"
    OUTPUT_FORMAT_PYTHON = "python"
    OUTPUT_FORMAT_BINARY = "binary"

    def __init__(self):
        self.logger = None

    def configure_logger(self, debug_level: str):
        logging.basicConfig(level=getattr(logging, debug_level, logging.ERROR))
        self.logger = logging.getLogger(__name__)

    def parse_arguments(self, args: list[str]) -> argparse.Namespace:
        parser = argparse.ArgumentParser(description="Kaa Compiler CLI Application")
        parser.add_argument("input_file", type=str, help="Path to the input file")
        parser.add_argument("-o", "--output_file", type=str, default=None, help="Path to the output file")
        parser.add_argument("-f", "--output_format", type=str, choices=["hex", "python", "binary"], default="binary", help="Output format")
        parser.add_argument("-t", "--output_target", type=str, default="kapu8", help="Compilation target")
        parser.add_argument("-d", "--debug_level", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], default="ERROR", help="Debugging level")
        parsed_args = parser.parse_args(args)
        if self.logger:
            self.logger.debug(f"Parsed arguments: {parsed_args}")
        return parsed_args

    def read_input_file(self, input_file: str) -> str:
        input_path = Path(input_file)
        if not input_path.exists():
            self.logger.error(f"Input file '{input_file}' does not exist.")
            raise FileNotFoundError(f"Input file '{input_file}' does not exist.")
        with input_path.open("rt") as f:
            return f.read()

    def compile_data(self, input_data: str, target: str) -> bytes:
        compiler = KaaCompiler(target=target)
        return compiler.compile(input_data)

    def format_output(self, compiled_bytes: bytes, output_format: str):
        match output_format:
            case self.OUTPUT_FORMAT_HEX:    return bytes_to_hex(compiled_bytes)
            case self.OUTPUT_FORMAT_PYTHON: return bytes_to_python(compiled_bytes)
            case self.OUTPUT_FORMAT_BINARY: return compiled_bytes
            case _:
                self.logger.error(f"Unsupported output format: {output_format}")
                raise ValueError(f"Unsupported output format: {output_format}")

    def write_output(self, output_data, output_file: str):
        if output_file:
            with open(output_file, "wb") as f:
                f.write(output_data)
            self.logger.info(f"Output written to '{output_file}'.")
        else:
            print(output_data)

    def run(self, args: list[str]):
        try:
            arguments = self.parse_arguments(args)
            self.configure_logger(arguments.debug_level)
            input_data = self.read_input_file(arguments.input_file)
            compiled_bytes = self.compile_data(input_data, arguments.output_target)
            formatted_output = self.format_output(compiled_bytes, arguments.output_format)
            self.write_output(formatted_output, arguments.output_file)
        except Exception as e:
            if self.logger:
                self.logger.error(f"An error occurred: {e}")
            raise e
