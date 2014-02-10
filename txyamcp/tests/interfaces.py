from zope.interface.verify import verifyClass

from txyamcp.pool import YamClientPool
from txyamcp.interfaces import IYamClientPool


def test():
    verifyClass(IYamClientPool, YamClientPool)

if __name__ == "__main__":
    test()
