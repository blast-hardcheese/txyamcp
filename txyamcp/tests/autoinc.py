from twisted.internet import reactor, task
from twisted.internet.defer import inlineCallbacks
from twisted.trial import unittest

from txyamcp.pool import YamClientPool
from txyamcp.tests.utils import sleep


class YamClientPoolAutoincTestCase(unittest.TestCase):
    @inlineCallbacks
    def test_autoinc(self):
        hosts = [
            'localhost',
        ]

        pool = YamClientPool(hosts, poolSize=0)

        client = yield pool.getConnection()

        def rec(count):
            if count > 0 and pool.size < pool.autoincBy:
                return task.deferLater(reactor, 0, rec, count - 1)
        yield rec(5)

        assert pool.size == pool.autoincBy,\
            "Pool size should be exactly pool.autoincBy!"

        yield sleep(1)  # FIXME: This is needed due to a race condition in
                        # YamClient's connect(). YamClient.connect() needs
                        # to return a single Deferred that completes when
                        # all connections are fully set up.

        yield pool.disconnect()
