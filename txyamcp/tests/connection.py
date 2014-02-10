from twisted.internet.defer import DeferredQueue
from twisted.trial import unittest
from twisted.internet.defer import inlineCallbacks

from txyamcp.client import PooledYamClient
from txyamcp import YamClientPool


import os
os.system('clear')
os.system('date')

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
        yield pool.disconnect()
