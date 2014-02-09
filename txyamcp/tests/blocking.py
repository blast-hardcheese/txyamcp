from twisted.internet import reactor

from txyamcp import YamClientPool


def test():
    hosts = [
        'localhost',
    ]

    pool = YamClientPool(hosts, 1)

    def connected(res):
        def gotConnection(client):
            outerClient = client
            def blockedConnection(client):
                innerClient = client

                assert outerClient == innerClient, "Received clients are different!"

                def waitForTimeout():
                    assert pool.size == 1, "More clients were allocated!"
                    print "Clients were the same, no additional clients were created"
                    reactor.stop()
                reactor.callLater(pool.autoincTimeout, waitForTimeout)
            pool.getConnection().addCallback(blockedConnection)

            def releaseClient():
                client.disconnect()
            reactor.callLater(1, releaseClient)
        pool.getConnection().addCallback(gotConnection)

    pool.connect().addCallback(connected)

    reactor.run()


if __name__ == "__main__":
    test()

