import json
import subprocess
import uuid

from .common import which, expand_path
from .handlers import HandlerBase

terminal_notifier = which("terminal-notifier")
if terminal_notifier is None:
    raise ImportError(
        "Unable to find binary terminal-notifier. Please install this program "
        "to make use of TerminalNotifierHandler")

class TerminalNotifierHandler(HandlerBase):
    def __init__(self, app_name=None, show_app_name=False):
        super(MacOsHandler, self).__init__(app_name)
        self.show_app_name = show_app_name

    def _message_to_args(self, msg, ref=None):
        args = []
        timeoutable = True
        title_arg = "-subtitle" if self.show_app_name else "-title"

        # Localize actions since we may modify it later
        actions = msg.actions

        if self.show_app_name:
            args += ["-title", self.app_name]

        if msg.title is not None:
            args += [title_arg, msg.title]

        if msg.text is not None:
            args += ["-message", msg.text]

        if msg.icon is not None:
            args += ["-appIcon", expand_path(msg.icon)]

        if len(msg.actions) >= 2:
            # Use close button as the first option when there are two or more
            # options
            timeoutable = False
            args += ["-closeLabel", msg.actions[0][1]]
            args += ["-actions", ",".join(name for action, name in msg.actions[1:])]
        elif msg.actions:
            timeoutable = False
            args += ["-actions", ",".join(name for action, name in msg.actions)]

        if msg.extra.get("dropdown_label"):
            if len(msg.actions) < 2:
                raise ValueError(
                    "Dropdown label is only usable when having more than 2 "
                    "actions")
            args += ["-dropdownLabel"]

        if "reply" in msg.extra and msg.extra["reply"]:
            if msg.actions:
                raise ValueError("Must not specify actions when reply is used")
            args += ["-reply"]
            timeoutable = False

        # Timeout is not available when the user is presented by an action
        if msg.timeout is not None and timeoutable:
            args += ["-timeout", str(msg.timeout)]

        # Add group reference so the notification can be removed
        if ref is not None:
            args += ["-group", ref]

        # Make output JSON formatted
        args += ["-json"]

        return args

    def _reverse_action_lookup(self, msg, display_name):
        for action, name in msg.actions:
            if name == display_name:
                return action

    def _parse_tn_output(self, msg, output):
        output = json.loads(output.decode("utf-8"))

        # Hack for using the close button as a value when there are two or more
        # options. This will always use the
        if len(msg.actions) >= 2 and output["activationType"] == "closed":
            output["activationType"] = "actionClicked"
            output["activationValue"] = msg.actions[0][1]

        if output["activationType"] == "actionClicked":
            return self._reverse_action_lookup(
                msg, output["activationValue"]), None
        elif output["activationType"] == "replied":
            return "replied", output["activationValue"]
        else:
            reason = {
                "contentsClicked": "closed",
                "closed": "closed",
                "timeout": "timeout",
            }.get(output["activationType"])

        return reason, None

    def send(self, msg, wait=False):
        if wait is None:
            wait = False

        ref = str(uuid.uuid4())
        proc = subprocess.Popen(
            [terminal_notifier] + self._message_to_args(msg, ref),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

        if wait:
            stdout, stderr = proc.communicate()
            action, data = self._parse_tn_output(msg, stdout)
            return Response(self, ref, action, data)
        else:
            return Response(self, ref)
