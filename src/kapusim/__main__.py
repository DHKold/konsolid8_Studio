import sys
from .cli import Application


def main():
    app = Application()
    app.run(sys.argv[1:])


__all__ = ["main"]
