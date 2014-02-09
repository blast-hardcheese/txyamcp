import itertools

from twisted.internet import reactor
from twisted.internet.defer import DeferredList
from twisted.internet.defer import DeferredQueue
from twisted.internet.error import AlreadyCalled

from zope.interface import implements

from txyamcp.interfaces import IYamClientPool
from txyamcp.client import PooledYamClient


class YamClientPool(object):
    implements(IYamClientPool)

    desiredPoolSize = 0

    autoincBy = 5
    autoincTimeout = 2  # seconds

    hostIter = None
    nextHost = lambda: None

    pool = None
    queue = None

    def __init__(self, hosts, poolSize=10):
        """
        Initialize YamClientPool

        @param hosts: List of hosts, passed directly to YamClient. Elements
                      are either a C{hostname} or a tuple of
                      C{(hostname, port)}.
        @type hosts: C{list(str)} or C{list(tuple(str, int))}

        @param poolSize: Initial size of the connection pool.
        @type poolSize: C{int}
        """

        self.hostIter = itertools.cycle(hosts)
        self.nextHost = lambda: self.hostIter.next()

        # Build initial pool synchronously
        self.queue = DeferredQueue()
        self.pool = [self.buildClient() for i in xrange(poolSize)]

        self.setPoolSize(poolSize)

    def buildClient(self, autoQueue=True):
        client = PooledYamClient([ self.nextHost() ], self.queue)
        if autoQueue:
            def queue(client):
                self.queue.put(client)
                return client
            client.connect().addCallback(queue)
        return client

    def connect(self):
        """
        Get a deferred that fires only when all connections have been
        established.
        """

        return DeferredList([client.connect() for client in self.pool])

    def disconnect(self):
        """
        Get a deferred that fires only when all connections have been
        terminated.
        """

        return DeferredList([client.poolDisconnect() for client in self.pool])

    def addConnections(self, count):
        """
        Add new connections to the pool.

        @param count: Number of new connections to add
        @type count: C{int}
        """

        if count > 0:
            client = self.buildClient()
            self.pool.append(client)
            reactor.callLater(0, self.addConnections, count - 1)

    def getConnection(self):
        """
        Get an available PooledYamClient.
        """
        d = self.queue.get()

        def timeout():
            self.addConnections(self.autoincBy)
        t = reactor.callLater(self.autoincTimeout, timeout)

        def cancelTimeout(res, t):
            try:
                t.cancel()
            except AlreadyCalled:
                pass
            return res
        d.addCallback(cancelTimeout, t)

        return d

    def setPoolSize(self, desiredSize):
        """
        Set the desired connection pool size

        @param desiredSize: Integer defining the desired size of the pool.
        @type desiredSize: C{int}
        """

        self.desiredPoolSize = desiredSize
