import re
import collections

from commonnexus._compat import cached_property
from commonnexus.tokenizer import get_name


class Payload:
    """
    The payload of a Nexus command, i.e. the stuff between command name and final ";".
    """
    __multivalued__ = False

    def __init__(self, tokens):
        self._tokens = tokens

    def format(self, *args, **kw):
        """
        Derived classes may provide functionality to format command data as correct Nexus payload.
        """
        raise NotImplementedError()

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
                cls = self.payload_map.get(cmd.name, Payload)
                res[cmd.name].append(cls(tuple(cmd.iter_payload_tokens())))
        return res

    def validate(self, log=None):
        if log:
            log.info('{} block with {} commands'.format(self.name, len(self) - 2))
        return True
