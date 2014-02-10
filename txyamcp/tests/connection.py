from twisted.internet import defer, reactor
from twisted.internet.defer import DeferredQueue
from twisted.trial import unittest
from twisted.internet.defer import inlineCallbacks

from txyamcp import YamClientPool
from txyamcp.client import PooledYamClient
from txyamcp.tests.utils import sleep


class YamClientPoolConnectionTestSuite(unittest.TestCase):
    @inlineCallbacks
    def test_raw_connection(self):
        queue = DeferredQueue()
        client = PooledYamClient(['localhost'], queue)

        res = yield client.connect()
        yield client.poolDisconnect()

    @inlineCallbacks
    def test_pooled_reconnection(self):
        hosts = [
            'localhost',
        ]

        pool = YamClientPool(hosts, poolSize=1)

        client1 = yield pool.getConnection()
        res = yield client1.disconnect()
        client2 = yield pool.getConnection()
        yield sleep(1)  # FIXME: This is needed due to a race condition in
                        # YamClient's connect(). YamClient.connect() needs
                        # to return a single Deferred that completes when
                        # all connections are fully set up.
        yield pool.disconnect()
