from copy import copy

from twisted.internet import reactor

from zope.interface.verify import verifyObject

from txyamcp import YamClientPool
from txyamcp.interfaces import IYamClientPool


def test():
    hosts = [
        'localhost',
        ('localhost', 11211)
    ]

    pool = YamClientPool(hosts, 2)

    left = copy(hosts)

    def connected(client):
        print "Client connected:", client
        print "\tConnected hosts:", client.hosts
        assert len(client.hosts) == 1,\
            "Wrong number of hosts for pooled client!"
        host = client.hosts[0]
        assert host in left, "Host not in remaining hosts!"

        print "\tRemoving..."
        left.remove(host)

        if len(left) == 0:
            print "All hosts resolved correctly, success!"

            def disconnected(res):
                print "Pool disconnected!"
                reactor.stop()
            pool.disconnect().addCallback(disconnected)

    pool.getConnection().addCallback(connected)
    pool.getConnection().addCallback(connected)

    verifyObject(IYamClientPool, pool)

    reactor.run()

if __name__ == "__main__":
    test()
