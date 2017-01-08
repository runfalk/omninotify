import threading

from time import sleep

from .common import Response, LimitedSizeDict, coalesce, file_uri
from .handlers import HandlerBase

try:
    from tdbus import SimpleDBusConnection, DBUS_BUS_SESSION, DBusHandler, \
        signal_handler
except ImportError:
    raise ImportError(
        "tdbus not available, which makes FreedesktopHandler unavailable")

class TdbusHandler(DBusHandler):
    def __init__(self, handler):
        super(TdbusHandler, self).__init__()
        self.handler = handler

    @signal_handler()
    def NotificationClosed(self, message):
        print('signal received: %s, args = %s' % (
            message.get_member(), repr(message.get_args())))
        self.handler._handle_closed(*message.get_args())

    @signal_handler()
    def ActionInvoked(self, message):
        print('signal received: %s, args = %s' % (
            message.get_member(), repr(message.get_args())))
        self.handler._handle_action(*message.get_args())

class FreedesktopHandler(HandlerBase):
    def __init__(self, app_name=None, *args, **kwargs):
        super(FreedesktopHandler, self).__init__(app_name)

        self.dbus_handler = TdbusHandler(self)

        self.dbus = SimpleDBusConnection(DBUS_BUS_SESSION)
        self.dbus.add_handler(self.dbus_handler)
        self.dbus.subscribe_to_signals()

        self.locals = threading.local()
        self.locals.events = LimitedSizeDict(size_limit=10)

    def _wait_for(self, ref, timeout=None):
        # Remember which notification to listen for
        self.locals.wait_for = ref

        # Implement timeout using a timer since signals are not necessary sent
        # when the notification is hidden
        if timeout is not None:
            # Extract thread local since it is used in the Timer thread
            events = self.locals.events

            # Callback to set status to timeout and stop event loop
            def timeout_callback():
                events[ref] = "timeout"
                self.dbus.stop()

            # Start timeout timer
            timer = threading.Timer(timeout, timeout_callback)
            timer.start()

            # Enter event loop
            self.dbus.dispatch()

            # Cancel timer in case it didn't fire, to save context local value
            timer.cancel()
        else:
            self.dbus.dispatch()

        # Cleanup
        del self.locals.wait_for

        return self.locals.events.pop(ref, None)

    def _handle_closed(self, ref, reason):
        self.locals.events[ref] = "closed"
        if ref == self.locals.wait_for:
            self.dbus.stop()

    def _handle_action(self, ref, action):
        self.locals.events[ref] = action
        if ref == self.locals.wait_for:
            self.dbus.stop()

    def _notify(
            self, title=None, text=None, icon=None, ref=None, actions=None,
            hints=None, timeout=None):
        return self.dbus.call_method(
            "/org/freedesktop/Notifications",
            "Notify",
            interface="org.freedesktop.Notifications",
            destination="org.freedesktop.Notifications",
            format="susssasa{sv}i",
            args=(
                self.app_name,
                ref or 0,
                icon or "",
                title or "",
                text or "",
                actions or [],
                hints or {},
                timeout or 0)).get_args()[0]

    def send(self, msg, wait=False):
        timeout = int(coalesce(msg.timeout, 5) * 1000)
        if msg.actions:
            timeout = None

        ref = self._notify(
            msg.title,
            msg.text,
            None if msg.icon is None else file_uri(msg.icon),
            actions=[x for pair in msg.actions for x in pair],
            #hints={"transient": True},
            timeout=timeout)

        if wait:
            return Response(
                self, ref, self._wait_for(
                    ref, None if timeout is None else timeout / 1000.0))
        return Response(self, ref)

    def close(self):
        self.dbus.remove_handler(self.dbus_handler)
        self.dbus.close()
