#!/usr/bin/python

from twisted.internet import protocol, reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from sys import stdout

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
    # User <-> Server communication
    def connectionMade(self):
        # We pause the incoming traffic, until the connection to the backend server is up.
        self.transport.pauseProducing()


        # Need to create a connection to a backend server...
        stdout.write("Connecting to client...\n")

        client = ClientFactory()
        client.setServer(self)

        reactor.connectTCP("localhost", 8080, client)


class ServerFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Server()


def main():
    reactor.listenTCP(1234, ServerFactory())
    reactor.run()

if __name__ == "__main__":
    main()