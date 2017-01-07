from .common import coalesce


class HandlerBase(object):
    supported = True

    def __init__(self, app_name=None):
        self.app_name = coalesce(app_name, "OmniNotify")

    def send(self, msg, wait=False):
        raise NotImplementedError("send not implemented")

    def close(self, ref):
        pass


class NullHandler(HandlerBase):
    supported = False

    def send(self, msg, wait=False):
        pass

    def close(self, ref):
        pass


class MultiHandler(HandlerBase):
    def __init__(self, handlers):
        self.handlers = handlers

    def send(self, msg, wait=None):
        return [h.send(msg, wait) for h in self.handlers if h.supported]

    def close(self, ref):
        return [h.close(ref) for h in self.handlers if h.supported]
