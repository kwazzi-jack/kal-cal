import argparse
import curses
import pick
from pick import select


def get_args():
    """
    Return a list of valid arguments.
    """
    parser = argparse.ArgumentParser(description='\
    Select paths from a directory tree.')
    parser.add_argument("-a", "--hidden", action="store_false",
                        help="Show all hidden paths too.")
    parser.add_argument("path", type=str, nargs='?',
                        default=".", help="A valid path.")
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    root = args.path
    hidden = args.hidden
    paths = curses.wrapper(select, root, hidden)
    print("\n".join(paths))
