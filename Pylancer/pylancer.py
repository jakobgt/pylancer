#!/usr/bin/python

from sys import stdout, argv
from random import randint

from twisted.internet import protocol, reactor

# Client is the component connecting to the different web servers.
from twisted.internet.protocol import connectionDone

class Proxy(protocol.Protocol):
    peer = None

    def setPeer(self, peer):
        self.peer = peer

    def connectionLost(self, reason=connectionDone):
        if self.peer:
            self.peer.transport.loseConnection()
            self.peer = None
        else:
            stdout.write("Could connect to the peer")

    def dataReceived(self, data):
        self.peer.transport.write(data)


class Client(Proxy):
    def connectionMade(self):
        stdout.write("Connection to localhost:8000 successfull.\n")
        self.peer.setPeer(self)
        self.peer.transport.resumeProducing()


class ClientFactory(protocol.ClientFactory):
    server = None
    def setServer(self, server):
        self.server = server

    def buildProtocol(self, addr):
        client = Client()
        client.setPeer(self.server)
        return client

    def clientConnectionFailed(self, connector, reason):
        stdout.write("Connection to localhost:8000 failed.\n")
        self.server.transport.loseConnection()

# The server is seen from our application side, so this one is the entity users connect to.
class Server(Proxy):
    port = 1234
    host = "localhost"

    def __init__(self, port, host):
        self.port = port
        self.host = host

    # User <-> Server communication
    def connectionMade(self):
        # We pause the incoming traffic, until the connection to the backend server is up.
        self.transport.pauseProducing()


        # Need to create a connection to a backend server...
        stdout.write("Connecting to client...\n")

        client = ClientFactory()
        client.setServer(self)

        reactor.connectTCP(self.host, self.port, client)


class ServerFactory(protocol.Factory):
    port = 1234
    hosts = []

    def __init__(self, port, hosts):
        self.port = port
        self.hosts = hosts

    def buildProtocol(self, addr):
        host = self.hosts[randint(0, len(self.hosts) - 1)]
        return Server(self.port, host)


def main():
    if len(argv) > 1:
        port = int(argv[1])
    else:
        print "No port given, use pylancer [port]"
        return
    if len(argv) > 2:
        hosts = argv[2:]
    else:
        print "No forwarding hosts given..."
        return

    print "Listening on port {0} and forwarding to {0}".format(port)
    reactor.listenTCP(port, ServerFactory(port, hosts))
    reactor.run()

if __name__ == "__main__":
    main()