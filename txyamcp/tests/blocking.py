from twisted.internet import reactor, task
from twisted.internet.defer import inlineCallbacks
from twisted.trial import unittest

from txyamcp import YamClientPool


class YamClientPoolBlockingTestCase(unittest.TestCase):

    @inlineCallbacks
    def test_blocking(self):
        hosts = [
            'localhost',
        ]

        pool = YamClientPool(hosts, 1)

        res = yield pool.connect()
        outerClient = yield pool.getConnection()

        def blockedConnection(client):
            innerClient = client

            assert outerClient == innerClient,\
                "Received clients are different!"

            def waitForTimeout():
                assert pool.size == 1, "More clients were allocated!"
                # "Clients were the same, no additional clients were created"

            return task.deferLater(
                reactor,
                pool.autoincTimeout,
                waitForTimeout
            )
        d = pool.getConnection().addCallback(blockedConnection)

        def releaseClient():
            outerClient.disconnect()
        yield task.deferLater(reactor, 1, releaseClient)

        yield d

        yield pool.disconnect()
