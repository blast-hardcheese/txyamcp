txyamcp: Yet Another Memcached (YAM) Connection Pool (for Twisted)
==================================================================

A connection-pooling extension to txyam.

Usage
=====

    from txyamcp.pool import YamClientPool

    hosts = [ 'localhost', ('otherhost', 123) ]
    pool = YamClientPool(hosts, poolSize=100)

    # getConnection will reserve a client until you call client.disconnect()
    client = yield pool.getConnection()

    [ ... do work ... ]

    # client.disconnect() returns the client back into the pool of available clients.
    client.disconnect()
