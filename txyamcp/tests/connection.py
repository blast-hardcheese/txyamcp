from twisted.internet.defer import DeferredQueue
from twisted.trial import unittest

from txyamcp.client import PooledYamClient
from txyamcp import YamClientPool


import os
os.system('clear')
os.system('date')

class YamClientPoolConnectionTestSuite(unittest.TestCase):
    def test_raw_connection(self):
        queue = DeferredQueue()
        client = PooledYamClient(['localhost'], queue)
        def disconnect(res):
            return client.poolDisconnect()
        return client.connect().addCallback(disconnect)

    def test_pooled_reconnection(self):
        hosts = [
            'localhost',
        ]

        pool = YamClientPool(hosts, poolSize=1)

        def connected(client):
            print "Connected!"
            def disconnected(res):
                print "Disconnected!"
                def connectedAgain(res):
                    print "Connected again somehow!"
                    return pool.disconnect()
                return pool.getConnection().addCallback(connectedAgain)
            return client.disconnect().addCallback(disconnected)
        return pool.getConnection().addCallback(connected)
