import argparse, os.path, sys, tigger.core, tigger.error

def file_exists(filename):
    if os.path.exists(filename):
        return filename
    else:
        raise IOError(2, "'{}' does not exist.".format(os.path.abspath(filename)), filename)


def init(args):
    try:
        tigger.core.find_base_dir()
        if args.force:
            raise tigger.error.NotInTaggedDir(".")
        else:
            sys.stderr.write("WARNING: This directory is inside an " +
                    "already-tracked directory. Use --force to go ahead anyway "
                    + "if, and only if, you're sure you want to start tracking "
                    + "here.\n")
    except tigger.error.NotInTaggedDir:
        tigger.core.initialize_base_dir()
        sys.stdout.write("Initialized tag tracking under the current directory.\n")

def tag(args):
    for tag in args.tags:
        try:
            tigger.core.tag_add_files(tag, args.files)
            sys.stdout.write("'{}' tag applied to all chosen files.\n".format(tag))
        except tigger.error.InvalidTag as e:
            sys.stderr.write("ERROR: " + str(e) + "\n")

def untag(args):
    for tag in args.tags:
        try:
            tigger.core.tag_remove_files(tag, args.files)
            sys.stdout.write("'{}' tag removed from all chosen files.\n".format(tag))
        except tigger.error.InvalidTag as e:
            sys.stderr.write("ERROR: " + str(e) + "\n")

def tags(args):
    for filename in args.files:
        try:
            tags = tigger.core.file_get_tags(filename)
            if tags == []:
                sys.stdout.write("{} is untagged.\n".format(filename))
            else:
                sys.stdout.write("{}:\n".format(filename))
                for tag in tags:
                    sys.stdout.write("\t{}\n".format(tag))
                    sys.stdout.write("")
        except tigger.error.NotInTaggedDir as e:
            sys.stderr.write("ERROR: " + str(e) + "\n")

def files(args):
    try:
        for tag in args.tags:
            try:
                files = tigger.core.tag_get_files(tag, rel_paths=True)
                if files == []:
                    sys.stdout.write("{} is an unused tag.\n".format(tag))
                else:
                    sys.stdout.write("{}:\n".format(tag))
                    for filename in files:
                        sys.stdout.write("\t{}\n".format(filename))
            except tigger.error.InvalidTag as e:
                sys.stderr.write("ERROR: " + str(e) + "\n")
    except tigger.error.NotInTaggedDir as e:
        sys.stderr.write("ERROR: " + str(e) + "\n")


def main():
    parser = argparse.ArgumentParser(description="""Tagging tool for arbitrary
        files.""")

    parser.add_argument("--trace", action="store_true", help="""[DEBUG] Trace
            the subcommand's execution.""")

    subparsers = parser.add_subparsers(title="subcommands")

    tag_command = subparsers.add_parser("init", description="""Initialize
            tag tracking for the current directory.""")
    tag_command.add_argument("--force", action="store_true", help="""Force
            initialization, even when already inside a tracked directory.
            Operating in the resulting environment may produce unexpected
            behaviour.""")
    tag_command.set_defaults(subcommand=init)

    tag_command = subparsers.add_parser("tag", description="""Add tag(s) to
            file(s).""")
    tag_command.add_argument("-t", "--tag", action="append", metavar="TAG",
            help="""A tag to be applied to the target file(s). This argument can
            be given more than once to apply multiple tags.""", dest="tags",
            required=True)
    tag_command.add_argument("files", nargs="+", metavar="FILE", help="""A file
            to be tagged.""", type=file_exists)
    tag_command.set_defaults(subcommand=tag)

    untag_command = subparsers.add_parser("untag", description="""Remove tag(s)
            from file(s).""")
    untag_command.add_argument("-t", "--tag", action="append", metavar="TAG",
            help="""A tag to be removed from the target file(s). This argument
            can be given more than once to remove multiple tags.""",
            dest="tags", required=True)
    untag_command.add_argument("files", nargs="+", metavar="FILE", help="""A file
            to be untagged.""", type=file_exists)
    untag_command.set_defaults(subcommand=untag)

    tags_command = subparsers.add_parser("tags", description="""List tags on one
            or more files.""")
    tags_command.add_argument("files", nargs="+", metavar="FILE", help="""A file
            to list tags on.""", type=file_exists)
    tags_command.set_defaults(subcommand=tags)

    files_command = subparsers.add_parser("files", description="""List files
            with one or more tags.""")
    files_command.add_argument("tags", nargs="+", metavar="TAG", help="""A tag to
            search for.""")
    files_command.set_defaults(subcommand=files)

    try:
        args = parser.parse_args()

        if args.subcommand is not None:
            if args.trace:
                import trace
                tracer = trace.Trace(ignoredirs=[sys.prefix, sys.exec_prefix],
                        trace=1, count=0)
                tracer.runctx('args.subcommand(args)', globals=globals(),
                        locals=locals())
            else:
                args.subcommand(args)
    except IOError as e:
        sys.stderr.write("ERROR: " + e.strerror + "\n")

if __name__ == "__main__":
    main()
