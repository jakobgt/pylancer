#!/opt/local/bin/python

from twisted.internet import protocol, reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from sys import stdout

# Client is the component connecting to the different web servers.
from twisted.internet.protocol import connectionDone


class Client(protocol.Protocol):
    def __init__(self):
        self.server_obj = None

    def sendData(self, data):
        self.transport.write(data)

    def dataReceived(self, data):
        self.server_obj.sendData(data)

class ClientFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Client()

# The server is seen from our application side, so this one is the entity users connect to.
class Server(protocol.Protocol):
    def __init__(self):
        self.client_object = None
        self.buffer = []

    def connectionMade(self):
        # Need to create a connection to a backend server...
        point = TCP4ClientEndpoint(reactor, "localhost", 8000)
        client_conn_deferred = point.connect(ClientFactory())
        client_conn_deferred.addCallback(self.connectionMadeForClient)

    def dataReceived(self, data):
        stdout.write("Received data\n")
        if self.client_object is None:
            stdout.write("client_object is none.\n")
            self.buffer.append(data)
        else:
            stdout.write("client_object is not none.\n")
            self.client_object.sendData(data)

    def connectionMadeForClient(self, client_protocol):
        stdout.write("Forwarding connection established\n")
        self.client_object = client_protocol
        client_protocol.server_obj = self
        if self.buffer:
            stdout.write("Buffer not empty: %d" % len(self.buffer))
            for data in self.buffer:
                self.client_object.sendData(data)
            self.buffer = []


    def sendData(self, data):
        self.transport.write(data)

    def connectionLost(self, reason=connectionDone):
        stdout.write("Closing connection for the client side.")
        self.client_object.transport.loseConnection()


class ServerFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Server()


def main():
    reactor.listenTCP(1234, ServerFactory())
    reactor.run()

if __name__ == "__main__":
    main()