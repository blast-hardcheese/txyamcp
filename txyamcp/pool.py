import itertools

from twisted.internet import reactor
from twisted.internet.defer import DeferredList
from twisted.internet.defer import DeferredQueue
from twisted.internet.defer import CancelledError
from twisted.internet.error import AlreadyCalled

from zope.interface import implements

from txyamcp.interfaces import IYamClientPool
from txyamcp.client import PooledYamClient
from txyamcp.exceptions import PoolDisconnectException


class YamClientPool(object):
    implements(IYamClientPool)

    connectable = False

    desiredPoolSize = 0

    @property
    def size(self):
        return len(self.pool)

    autoincBy = 5
    autoincTimeout = 2  # seconds

    hostIter = None
    nextHost = lambda: None

    pool = None
    queue = None

    pruneTimeout = 1

    def __init__(self, hosts, poolSize=10,
                 pruneTimeout=1,
                 autoincBy=5, autoincTimeout=2,
                 ):
        """
        Initialize YamClientPool

        @param hosts: List of hosts, passed directly to YamClient. Elements
                      are either a C{hostname} or a tuple of
                      C{(hostname, port)}.
        @type hosts: C{list(str)} or C{list(tuple(str, int))}

        @param poolSize: Initial size of the connection pool.
        @type poolSize: C{int}

        @param pruneTimeout: Time, in seconds, to wait between removing excess
                             clients from the pool
        @type pruneTimeout: C{int}

        @param autoincBy: Number of connections to auto-increment by
        @type autoincBy: C{int}

        @param autoincTimeout: Seconds waiting until new connections are
                               allocated
        @type autoincTimeout: C{int}
        """

        self.pruneTimeout = pruneTimeout

        self.autoincBy = autoincBy
        self.autoincTimeout = autoincTimeout

        self.hostIter = itertools.cycle(hosts)
        self.nextHost = lambda: self.hostIter.next()

        # Build initial pool synchronously
        self.queue = DeferredQueue()
        self.pool = [self.buildClient() for i in xrange(poolSize)]
        self.connectable = True

        self.setPoolSize(poolSize)

    def buildClient(self, autoQueue=True):
        client = PooledYamClient([self.nextHost()], self.queue)
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

        FIXME: This will leak connections due to a bug in YamClient.connect!
               Do not use YamClientPool.connect() until this bug is fixed!
        """
        self.connectable = True

        return DeferredList([client.connect() for client in self.pool])

    def disconnect(self):
        """
        Get a deferred that fires only when all connections have been
        terminated.
        """
        self.connectable = False

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
        if not self.connectable:
            raise PoolDisconnectException(
                "Someone has already called pool.disconnect()"
            )

        d = self.queue.get()

        def timeout():
            self.addConnections(self.autoincBy)
            reactor.callLater(self.pruneTimeout, self.pruneConnections)
        t = reactor.callLater(self.autoincTimeout, timeout)

        def cancelTimeout(res, t):
            try:
                t.cancel()
            except AlreadyCalled:
                pass
            return res

        def cancelErrback(failure, t):
            try:
                t.cancel()
            except AlreadyCalled:
                pass
            failure.trap(CancelledError)
        d.addCallback(cancelTimeout, t)
        d.addErrback(cancelErrback, t)

        return d

    def pruneConnections(self):
        if self.size > self.desiredPoolSize:
            d = self.getConnection()

            def timeout():
                d.cancel()
            t = reactor.callLater(self.pruneTimeout, timeout)

            def prune(client):
                try:
                    t.cancel()
                except AlreadyCalled:
                    pass
                if client is not None:
                    client.poolDisconnect()
                    self.pool.remove(client)

            d.addCallback(prune)

            reactor.callLater(self.pruneTimeout, self.pruneConnections)

    def setPoolSize(self, desiredSize):
        """
        Set the desired connection pool size

        @param desiredSize: Integer defining the desired size of the pool.
        @type desiredSize: C{int}
        """

        delta = desiredSize - self.size
        self.desiredPoolSize = desiredSize
        if delta > 0:
            self.addConnections(delta)
