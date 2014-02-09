from zope.interface import implements

from txyamcp.interfaces import IYamClientPool


class YamClientPool(object):
    implements(IYamClientPool)

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
        pass

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
        pass
