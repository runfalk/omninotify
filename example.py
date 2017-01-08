from omninotify import notification_handler, Message


# A message is not bound to a particular handler. It is possible to specify:
# - title: Which is usually displayed in bold above the text message
# - message: Which contains the major portion of the data
# - icon: Path to an image file to use for the notification
# - timeout: Timeout in seconds for the message
# - actions: List of actions to allow the user to do

# Simple message
simple = Message(u"This is a simple notification")

# Simple message with title
msg = Message(u"Title", u"Message")

# Simple message with title and icon
icon = Message(u"Title", u"Message", "~/.weechat/weechat.png")

# The same with home directory expansion
home_icon = Message(u"Title", u"Message", "~/icon.png")

# A message with a timeout (default is 5 seconds unless actions are specified).
# This message has a 0.5 second timeout
timeout = Message(u"Title", u"Message", timeout=0.5)

# A message with two buttons. Timeout is ignored when actions are specified
question = Message(u"Question", u"Will you switch to Python 3?", actions=[
    ("yes", "Yes!"),
    ("no", "No!"),
])

# On macOS it is possible to use the reply action which allows the user to write
# a reply directly in the notification bubble. This will degrade to just showing
# the notification when using other handlers.
reply = Message(u"TheFriend", u"Hey man, how you doin'?", reply=True)

# Construct a notification handler with the given application name. If there are
# no available handlers and allow_null_handler is False an exception will be
# raised. allow_null_handler set to True allows the application to continue
# using the library as usual, however no notifications will be shown.
h = notification_handler("Weechat", allow_null_handler=False)

# To send the message, just call send on the handler. If wait is True (default
# False) the method will block until the notification disappears
print(h.send(icon, wait=True))
