from .core.application import Application


def main():
    gui = Application()
    gui.run()


__all__ = ["main"]
