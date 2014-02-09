from zope.interface import Interface


class IYamClientPool(Interface):
    """Interface for YamClientPool"""

    def __init__(hosts, poolSize=10):
        """
        Initialize YamClientPool

        @param hosts: List of hosts, passed directly to YamClient. Elements
                      are either a C{hostname} or a tuple of
                      C{(hostname, port)}.
        @type hosts: C{list(str)} or C{list(tuple(str, int))}

        @param poolSize: Initial size of the connection pool.
        @type poolSize: C{int}
        """

    def connect():
        """
        Get a deferred that fires only when all connections have been
        established.
        """

    def disconnect():
        """
        Get a deferred that fires only when all connections have been
        terminated.
        """

    def getConnection():
        """
        Get an available PooledYamClient.
        """

    def setPoolSize(desiredSize):
        """
        Set the desired connection pool size

        @param desiredSize: Integer defining the desired size of the pool.
        @type desiredSize: C{int}
        """
