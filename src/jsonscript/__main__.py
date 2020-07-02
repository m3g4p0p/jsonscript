import sys

from .interpreter import run


def main():
    filename, *args = sys.argv

    with open(filename) as f:
        return run(filename, None, args)


if __name__ == '__main__':
    sys.exit(main())
