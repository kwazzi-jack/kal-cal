import argparse
import curses
import os

from treepick import pick


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
    parser = argparse.ArgumentParser(description='\
    Select paths from a directory tree.')
    parser.add_argument("-a", "--hidden", action="store_false",
                        help="Show all hidden paths too.")
    parser.add_argument("-r", "--relative", action="store_true",
                        help="Output relative paths.")
    parser.add_argument("path", type=chkpath, nargs='?',
                        default=".", help="A valid path.")
    return parser.parse_args()


def main():
    args = getargs()
    root = os.path.abspath(os.path.expanduser(args.path))
    hidden = args.hidden
    relative = args.relative
    paths = curses.wrapper(pick, root, hidden, relative)
    print("\n".join(paths))


if __name__ == '__main__':
    main()
