from .cli import Application


def main():
    app = Application()
    app.run()


__all__ = ["main"]
