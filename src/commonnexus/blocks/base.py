import re
import collections

from commonnexus._compat import cached_property
from commonnexus.tokenizer import get_name


class Payload:
    """
    The payload of a Nexus command, i.e. the stuff between command name and final ";".
    """
    def __init__(self, tokens):
        self.tokens = tokens

    def __str__(self):
        return ''.join(str(t) for t in self.tokens)

    @property
    def lines(self):
        return re.split(r'[\t\r ]*\n[\t\r ]*', str(self))


class Block(tuple):
    """
    A Block is a list of commands, starting with a BEGIN command and ending with END.
    """
    # Custom `Payload` subclasses can be registered for command names:
    __commands__ = {}

    def __getattribute__(self, name):
        if name.isupper():
            try:
                return self.commands[name][0]
            except IndexError:
                raise AttributeError('Block {} has no command {}'.format(self.name, name))
        return tuple.__getattribute__(self, name)

    @cached_property
    def name(self):
        return get_name(self[0].iter_payload_tokens())

    @cached_property
    def commands(self):
        res = collections.defaultdict(list)
        for cmd in self:
            if not (cmd.is_beginblock or cmd.is_endblock):
                cls = self.__commands__.get(cmd.name, Payload)
                res[cmd.name].append(cls(tuple(cmd.iter_payload_tokens())))
        return res
