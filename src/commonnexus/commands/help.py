"""
Get help on subcommands.
"""


def register(parser):  # pylint: disable=missing-function-docstring
    parser.add_argument('command', nargs='?', default=None)


def run(args) -> int:  # pylint: disable=missing-function-docstring
    from commonnexus.__main__ import main  # pylint: disable=import-outside-toplevel

    if args.command:
        return main([args.command, '-h'])
    print('Run "commonnexus COMMAND -h" to get help on subcommand COMMAND')
    return 0
