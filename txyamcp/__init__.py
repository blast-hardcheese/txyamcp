import itertools

from twisted.internet.defer import DeferredQueue

from zope.interface import implements

from txyamcp.interfaces import IYamClientPool


class YamClientPool(object):
    implements(IYamClientPool)

    desiredPoolSize = 0

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
        self.pool = [self.nextHost() for i in xrange(poolSize)]
        self.queue = DeferredQueue()

        self.setPoolSize(poolSize)

    def connect(self):
        """
        Get a deferred that fires only when all connections have been
        established.
        """
        pass

    def disconnect(self):
        """
        Get a deferred that fires only when all connections have been
        terminated.
        """
        pass

    def getConnection(self):
        """
        Get an available PooledYamClient.
        """
        pass

    def setPoolSize(self, desiredSize):
        """
        Set the desired connection pool size

        @param desiredSize: Integer defining the desired size of the pool.
        @type desiredSize: C{int}
        """

        self.desiredPoolSize = desiredSize
