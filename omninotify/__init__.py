
from .common import Message
from .handlers import NullHandler, MultiHandler

handlers = []
errors = []

try:
    from .macos import TerminalNotifierHandler
    handlers.append(TerminalNotifierHandler)
except ImportError as e:
    errors.append(str(e))

try:
    from .freedesktop import FreedesktopHandler
    handlers.append(FreedesktopHandler)
except ImportError as e:
    errors.append(str(e))


def notification_handler(app_name=None, allow_null_handler=False, *args, **kwargs):
    if not handlers and not allow_null_handler:
        raise ImportError(
            "No handlers available, reasons:\n{}".format("\n".join(errors)))
    elif allow_null_handler:
        return NullHandler(app_name)

    return handlers[0](app_name, *args, **kwargs)
