"""
What about PAUP's OPTIONS command:

https://paup.phylosolutions.com/tutorials/quick-start/

begin data;
dimensions ntax=12 nchar=898;
format missing=? gap=- matchchar=. interleave datatype=dna;
options gapmode=missing;
matrix

"""
import re
import collections
import types
import typing

from commonnexus._compat import cached_property
from commonnexus.tokenizer import (
    get_name, iter_tokens, iter_words_and_punctuation, word_after_equals,
)
from commonnexus.command import Command


class Payload:
    """
    The payload of a Nexus command, i.e. the stuff between command name and final ";".
    """
    __multivalued__ = False

    def __init__(self, tokens, nexus=None):
        self.nexus = nexus
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


class Title(Payload):
    """
    Support for Mesquite's mechanism to link blocks.

    https://phylo.bio.ku.edu/slides/lab9-MesquiteAncStatesBisse/09-Mesquite.html#Create_a_tree_file
    """
    def __init__(self, tokens, nexus=None):
        super().__init__(tokens, nexus=nexus)
        self.title = next(iter_words_and_punctuation(self._tokens)).upper()
        assert isinstance(self.title, str)


class Link(Payload):
    """
    Support for Mesquite's mechanism to link blocks.

    https://phylo.bio.ku.edu/slides/lab9-MesquiteAncStatesBisse/09-Mesquite.html#Create_a_tree_file
    """
    def __init__(self, tokens, nexus=None):
        super().__init__(tokens, nexus=nexus)
        words = iter_words_and_punctuation(self._tokens)
        self.block = next(words).upper()
        self.title = word_after_equals(words).upper()


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
        res = {cls.__name__.upper(): cls for cls in self.__commands__}
        res.update(LINK=Link, TITLE=Title)
        return res

    @property
    def title(self):
        if self.TITLE:
            return self.TITLE.title

    @property
    def links(self):
        return {link.block: link.title for link in self.commands['LINK']}

    @property
    def linked_blocks(self):
        res = {}
        for name, title in self.links.items():
            for block in self.nexus.blocks.get(name, []):
                if block.title == title:
                    res[name] = block
        return res

    def __getattribute__(self, name):
        if name.isupper():
            try:
                return self.commands[name][0]
            except IndexError:
                return None
        return super().__getattribute__(name)

    @cached_property
    def name(self):
        return get_name(self[0].iter_payload_tokens())

    @cached_property
    def commands(self):
        res = collections.defaultdict(list)
        for cmd in self:
            if not (cmd.is_beginblock or cmd.is_endblock):
                cls = self.payload_map.get(cmd.name, Payload)
                res[cmd.name].append(cls(tuple(cmd.iter_payload_tokens()), nexus=self.nexus))
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
        kw = {}
        if nexus:
            kw['quote'] = nexus.cfg.quote
        cmds = [Command.from_name_and_payload('BEGIN', name or cls.__name__.upper(), **kw)]
        for cname, payload in commands:
            cmds.append(Command.from_name_and_payload(cname, payload, **kw))
        cmds.append(Command.from_name_and_payload('END', **kw))
        return cls(nexus, tuple(cmds))

    @classmethod
    def from_data(cls, *args, **kw) -> 'Block':
        """
        Block implementations must overwrite this method to implement "meaningful" NEXUS writing
        functionality.
        """
        raise NotImplementedError()  # pragma: no cover
