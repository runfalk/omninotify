from .common import coalesce


class HandlerBase(object):
    supported = True

    def __init__(self, app_name=None):
        self.app_name = coalesce(app_name, "OmniNotify")

    def send(self, msg, wait=False):
        raise NotImplementedError("send not implemented")

    def dismiss(self, ref):
        raise NotImplementedError("dismiss not implemented")

    def close(self):
        pass


class NullHandler(HandlerBase):
    supported = False

    def send(self, msg, wait=False):
        pass

    def dismiss(self, ref):
        pass


class MultiHandler(HandlerBase):
    def __init__(self, handlers):
        self.handlers = handlers

    def send(self, msg, wait=None):
        return [h.send(msg, wait) for h in self.handlers if h.supported]

    def dismiss(self, ref):
        return [h.dismiss(ref) for h in self.handlers if h.supported]

    def close(self):
        return [h.close() for h in self.handlers if h.supported]
