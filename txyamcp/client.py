from twisted.internet.defer import Deferred
from txyam.client import YamClient


class PooledYamClient(YamClient):
    queue = None

    def __init__(self, hosts, queue, *args, **kwargs):
        """
        @param hosts: List of hosts, will be passed directly to
                      YamClient.__init__.
        @param queue: Anything that conforms to DeferredQueue's interface.
        """
        self.queue = queue
        self.connectingDeferred = None
        YamClient.__init__(self, hosts, *args, **kwargs)

    def disconnect(self):
        """disconnect: Since this is a pooled client, put this client back in
                       the pool.
        """
        self.queue.put(self)
        d = Deferred()
        d.callback(None)
        return d

    def poolDisconnect(self):
        """poolDisconnect: Actually disconnect this client. This should only be
           called by the controlling pool.
        """
        return YamClient.disconnect(self)

    def connect(self):
        if self.connectingDeferred is None:
            self.connectingDeferred = YamClient.connect(self)
        return self.connectingDeferred  # XXX: What happens when the factory
                                        # connection is lost for other reasons
                                        # than .disconnect()?
