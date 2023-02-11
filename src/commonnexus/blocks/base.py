import re
import collections
import typing

from commonnexus._compat import cached_property
from commonnexus.tokenizer import get_name, iter_tokens
from commonnexus.command import Command


class Payload:
    """
    The payload of a Nexus command, i.e. the stuff between command name and final ";".
    """
    __multivalued__ = False

    def __init__(self, tokens):
        self._tokens = list(iter_tokens(iter(tokens))) if isinstance(tokens, str) else tokens

    def format(self, *args, **kw):
        """
        Derived classes may provide functionality to format command data as correct Nexus payload.
        """
        raise NotImplementedError()  # pragma: no cover

    def __str__(self):
        return ''.join(str(t) for t in self._tokens)

    @property
    def lines(self):
        return re.split(r'[\t\r ]*\n[\t\r ]*', str(self))


class Block(tuple):
    """
    A Block is a list of commands, starting with a BEGIN command and ending with END.
    """
    # Custom `Payload` subclasses can be registered for command names:
    __commands__ = {}

    def __new__ (cls, nexus, cmds):
        return super().__new__(cls, tuple(cmds))

    def __init__(self, nexus, cmds):
        self.nexus = nexus

    @cached_property
    def payload_map(self):
        return {cls.__name__.upper(): cls for cls in self.__commands__}

    def __getattribute__(self, name):
        if name.isupper():
            try:
                return self.commands[name][0]
            except IndexError:
                return None
        return tuple.__getattribute__(self, name)

    @cached_property
    def name(self):
        return get_name(self[0].iter_payload_tokens())

    @cached_property
    def commands(self):
        res = collections.defaultdict(list)
        for cmd in self:
            if not (cmd.is_beginblock or cmd.is_endblock):
                cls = self.payload_map.get(cmd.name, Payload)
                res[cmd.name].append(cls(tuple(cmd.iter_payload_tokens())))
        return res

    def validate(self, log=None):
        if log:
            log.info('{} block with {} commands'.format(self.name, len(self) - 2))
        return True

    @classmethod
    def from_commands(cls,
                      commands: typing.Iterable[typing.Tuple[str, str]],
                      nexus=None,
                      name=None) -> 'Block':
        """
        Generic factory method for blocks.

        This method will create a block with the uppercase name of the ``cls`` as name (or the
        explicitly passed block ``name``). The (name str, payload str) tuples from ``commands``
        are simply passed to :meth:`commonnexus.command.Command.from_name_and_payload` to assemble
        the commands in the block.

        This method should be used to create custom, non-public NEXUS blocks, while for public
        blocks the ``from_data`` method of the class implementing the block should be preferred,
        because the latter will make sure that consistent, valid block data is written.

        :param commands:
        :param nexus:
        :param name:
        :return:

        .. code-block:: python

            >>> from commonnexus import Nexus, Block
            >>> nex = Nexus()
            >>> nex.append_block(Block.from_commands([('mycommand', 'with data')], name='myblock'))
            >>> print(nex)
            #NEXUS
            BEGIN myblock;
            mycommand with data;
            END;
            >>> str(nex.MYBLOCK.MYCOMMAND)
            'with data'
        """
        cmds = [Command.from_name_and_payload('BEGIN', name or cls.__name__.upper())]
        for cname, payload in commands:
            cmds.append(Command.from_name_and_payload(cname, payload))
        cmds.append(Command.from_name_and_payload('END'))
        return cls(nexus, tuple(cmds))

    @classmethod
    def from_data(cls, *args, **kw) -> 'Block':
        """
        Block implementations must overwrite this method to implement "meaningful" NEXUS writing
        functionality.
        """
        raise NotImplementedError()  # pragma: no cover
