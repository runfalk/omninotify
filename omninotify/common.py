import os

from collections import OrderedDict


def which(prog):
    """
    A naive re-implementation of the shell utility ``which``.

    :param prog: Name of binary to find
    :return: Absolute path to the given binary, or None if not found
    """
    for bindir in os.environ.get("PATH", "").split(":"):
        try:
            if prog in os.listdir(bindir):
                return os.path.join(bindir, prog)
        except OSError:
            pass


def expand_path(path):
    """
    Convert a path to an absolute path. This does home directory expansion,
    meaning a leading ~ or ~user is translated to the current or given user's
    home directory. Relative paths are relative to the current working
    directory.

    :param path: Relative or absolute path of file.
    :return: Absolute path
    """

    return os.path.abspath(os.path.expanduser(path))


def file_uri(path):
    """
    Convert a path to an absolute file URI. This does home directory expansion,
    meaning a leading ~ or ~user is translated to the current or given user's
    home directory. Relative paths are relative to the current working
    directory.

    :param path: Relative or absolute path of file.
    :return: Absolute path prefixed by ``file://``
    """

    return "file://{}".format(expand_path(path))


def coalesce(*args):
    """Return the first argument that is not ``None``"""
    for arg in args:
        if arg is not None:
            return arg


class LimitedSizeDict(OrderedDict):
    def __init__(self, elements=None, size_limit=None):
        self.size_limit = size_limit
        super(LimitedSizeDict, self).__init__(elements or [])
        self._trim_dict()

    def __setitem__(self, key, value):
        super(LimitedSizeDict, self).__setitem__(key, value)
        self._trim_dict()

    def _trim_dict(self):
        if self.size_limit is not None:
            while len(self) > self.size_limit:
                self.popitem(last=False)


class Message(object):
    """
    Notifier agnostic message.

    This class represents a message to display to the end user using ``.send()``
    on a handler.

    :param title: Title of notification (if no text is set this is used as the
                  text instead)
    :param text: Text of notification
    :param icon: Path to icon file (absolute or relative to current working
                 directory)
    :param timeout: Timeout in seconds as a ``float``. Timeout is ignored when
                    actions are specified.
    :param actions: List of two-tuples containing available actions. The first
                    tuple element represents the internal name of the action and
                    the element is the display name of the action.
    :param **extra: Handler specific arguments may be specified using keyword
                    arguments.
    :raise ValueError: if action display name contains ``,`` or internal name
                       collides with one of the reserved action names.
    """

    reserved_actions = frozenset([
        "closed",
        "replied",
        "timeout",
    ])

    def __init__(
            self, title, text=None, icon=None, timeout=None, actions=None,
            **extra):
        self.title = title
        self.text = text
        self.icon = icon
        self.timeout = timeout
        self.actions = coalesce(actions, [])
        self.extra = extra

        # Validate actions
        for action, name in self.actions:
            if "," in name:
                raise ValueError(
                    ", must not be used in action names, since they are"
                    "unsupported on macOS")

            if action in self.reserved_actions:
                raise ValueError(
                    "{} is a reserved action name. Please use a different one".format(name))


class Response(object):
    def __init__(self, handler, ref, action=None, data=None):
        self.handler = handler
        self.ref = ref
        self.action = action
        self.data = data

    def __repr__(self):
        return "{}(ref={!r}, action={!r}, data={!r})".format(
            self.__class__.__name__, self.ref, self.action, self.data)

    # Not implemented by any handlers yet
    # def close(self):
    #     self.handler.close(self.ref)
