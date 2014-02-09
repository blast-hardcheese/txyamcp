from twisted.internet import reactor

from txyamcp import YamClientPool


def test():
    hosts = [
        'localhost',
    ]

    pool = YamClientPool(hosts)

    def connected(res):
        print "Connected!"
        def disconnected(res):
            print "Disconnected!"
            def connectedAgain(res):
                print "Connected again somehow!"
                reactor.stop()
            pool.connect().addCallback(connectedAgain)
        pool.disconnect().addCallback(disconnected)
    pool.connect().addCallback(connected)

    reactor.run()


if __name__ == "__main__":
    test()
