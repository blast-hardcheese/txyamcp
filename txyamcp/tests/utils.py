from twisted.internet import reactor, task, defer


def sleep(seconds):
    d = defer.Deferred()
    reactor.callLater(seconds, d.callback, seconds)
    return d


def genericLog(*args):
    print args[-1]
    return args[0]
