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
        YamClient.__init__(self, hosts, *args, **kwargs)

    def disconnect(self):
        """disconnect: Since this is a pooled client, put this client back in
                       the pool.
        """
        self.queue.put(self)

    def poolDisconnect(self):
        """poolDisconnect: Actually disconnect this client. This should only be
           called by the controlling pool.
        """
        return YamClient.disconnect(self)
