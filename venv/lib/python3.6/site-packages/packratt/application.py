# -*- coding: utf-8 -*-
import argparse
import logging
import sys

from packratt.dispatch import Dispatch

log = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

commands = Dispatch()


@commands.register("get")
def get(args):
    from packratt.interface import get
    return get(args.key, args.destination)


def create_parser():
    p = argparse.ArgumentParser()
    sp = p.add_subparsers(help='command', dest='command')

    # Get a data product
    get = sp.add_parser('get')
    get.add_argument("key")
    get.add_argument("destination", default=".", nargs="?")

    return p


def _run(args):
    parser = create_parser()
    args = parser.parse_args(args)

    if args.command:
        commands(args.command, args)
    else:
        parser.print_help()

    return 0


def run():
    return _run(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(run())
