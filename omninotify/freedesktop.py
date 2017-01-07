import threading

from time import sleep

from .common import Response, LimitedSizeDict, coalesce, file_uri
from .handlers import HandlerBase

try:
    from pydbus import SessionBus, Variant
    from gi.repository import GLib
except ImportError:
    raise ImportError(
        "pydbus and/or gi.repository not available, which makes "
        "FreedesktopHandler unavailable")


class FreedesktopHandler(HandlerBase):
    def __init__(self, app_name=None, *args, **kwargs):
        super(FreedesktopHandler, self).__init__(app_name)

        self.session_bus = SessionBus()
        self.notifications = self.session_bus.get(".Notifications")

        # Register handlers
        self.notifications.NotificationClosed.connect(self._handle_closed)
        self.notifications.ActionInvoked.connect(self._handle_action)

        self.locals = threading.local()
        self.locals.events = LimitedSizeDict(size_limit=10)

    def _wait_for(self, ref, timeout=None):
        # Remember which notification to listen for
        self.locals.wait_for = ref

        # Make the loop available in a thread local so the handlers can stop it
        self.locals.loop = GLib.MainLoop()

        # Implement timeout using a timer since signals are not necessary sent
        # when the notification is hidden
        if timeout is not None:
            # Run the loop until a timeout is reached or it is cancelled by a
            # handler
            def cancel_on_timeout(loop):
                loop.quit()

                # Add the timeout event
                self.locals.events[self.locals.wait_for] = "timeout"

                # We must return True to ensure that the callback is not removed
                # until we do it manually further down. If not the
                return True

            # Add timer to stop the loop on timeout
            event_id = GLib.timeout_add_seconds(
                timeout, cancel_on_timeout, self.locals.loop)

            # Run main loop
            self.locals.loop.run()

            # Remove timer
            GLib.source_remove(event_id)
        else:
            self.locals.loop.run()

        # Cleanup
        del self.locals.wait_for
        del self.locals.loop

        return self.locals.events.pop(ref, None)

    def _handle_closed(self, ref, reason):
        self.locals.events[ref] = "closed"
        if self.locals.wait_for == ref:
            self.locals.loop.quit()

    def _handle_action(self, ref, action):
        self.locals.events[ref] = action
        if self.locals.wait_for == ref:
            self.locals.loop.quit()

    def _notify(
            self, title=None, text=None, icon=None, ref=None, actions=None,
            hints=None, timeout=None):
        return self.notifications.Notify(
            self.app_name,
            ref or 0,
            icon or "",
            title or "",
            text or "",
            actions or [],
            hints or {},
            timeout or 0)

    def send(self, msg, wait=False):
        timeout = int(coalesce(msg.timeout, 5) * 1000)
        if msg.actions:
            timeout = None

        ref = self._notify(
            msg.title,
            msg.text,
            None if msg.icon is None else file_uri(msg.icon),
            actions=[x for pair in msg.actions for x in pair],
            # hints={"transient": Variant("b", True)},
            timeout=timeout)

        if wait:
            return Response(
                self, ref, self._wait_for(
                    ref, None if timeout is None else timeout / 1000.0))
        return Response(self, ref)
