from twisted.internet import reactor, task
from twisted.internet.defer import inlineCallbacks
from twisted.trial import unittest

from txyamcp.pool import YamClientPool
from txyamcp.tests.utils import sleep, tick


class YamClientPoolAutoincTestCase(unittest.TestCase):
    @inlineCallbacks
    def test_autoinc(self):
        hosts = [
            'localhost',
        ]
        # Low prune rate will clear out all clients before this test finishes
        pool = YamClientPool(hosts, poolSize=0, pruneTimeout=0.1)

        client = yield pool.getConnection()

        def rec(count):
            if count > 0 and pool.size < pool.autoincBy:
                return task.deferLater(reactor, 0, rec, count - 1)
        yield rec(5)

        assert pool.size == pool.autoincBy,\
            "Pool size should be exactly pool.autoincBy!"

        yield client.disconnect()

        yield sleep(1)  # FIXME: This is needed due to a race condition in
                        # YamClient's connect(). YamClient.connect() needs
                        # to return a single Deferred that completes when
                        # all connections are fully set up.

    @inlineCallbacks
    def test_cancel(self):
        hosts = [
            'localhost',
        ]

        pool = YamClientPool(hosts, poolSize=0)
        d = pool.getConnection()
        yield tick()
        d.cancel()
        yield d
        assert pool.size == 0, "Don't allocate unnecessary connections!"

    @inlineCallbacks
    def test_autodec(self):
        hosts = [
            'localhost',
        ]

        pool = YamClientPool(hosts, poolSize=0, pruneTimeout=0.05)
        client = yield pool.getConnection()
        yield sleep(0.1 * pool.autoincBy + 0.1)
        client.disconnect()
        yield sleep(0.5)
        assert pool.size == 0, "Always autodec to desiredSize"
