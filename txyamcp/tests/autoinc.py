from twisted.internet import reactor

from txyamcp import YamClientPool


def test():
    hosts = [
        'localhost',
    ]

    pool = YamClientPool(hosts, poolSize=0)

    def gotClient(client):
        print "Current pool size:", pool.size
        reactor.callLater(0, rec, 5)

    def rec(count):
        if count > 0 and pool.size < pool.autoincBy:
            print "Autoincrementing pool size...", pool.size
            reactor.callLater(0, rec, count - 1)
        else:
            print "Pool size:", pool.size
            reactor.stop()

    print "Pool size:", pool.size
    print "Get connection..."
    pool.getConnection().addCallback(gotClient)

    reactor.run()


if __name__ == "__main__":
    test()
