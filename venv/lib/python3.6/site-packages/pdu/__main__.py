import argparse
import os
from pdu import du


def chkpath(path):
    """
    Checks if a path exists.
    """
    if os.path.exists(path):
        return path
    else:
        msg = "{0} does not exist.".format(path)
        raise argparse.ArgumentTypeError(msg)


def getargs():
    """
    Return a list of valid arguments.
    """
    parser = argparse.ArgumentParser(
        description='Python Disk Usage Calculator.')
    parser.add_argument("path", type=chkpath, nargs='?',
                        default=".", help="A valid path.")
    return parser.parse_args()


def main():
    args = getargs()
    path = os.path.abspath(args.path)
    size = du(path)
    print("{0} = {1}".format(path, size))


if __name__ == '__main__':
    main()
