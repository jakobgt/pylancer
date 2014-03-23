#!/opt/local/bin/python

from twisted.internet import protocol, reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from sys import stdout

# Client is the component connecting to the different web servers.
class Client(protocol.Protocol):
    def __init__(self):
        self.server_obj = None

    def sendData(self, data):
        self.transport.write(data)

    def dataReceived(self, data):
        pass
        # self.server_obj.sendData(data)

class ClientFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Client()

# The server is seen from our application side, so this one is the entity users connect to.
class Server(protocol.Protocol):
    def __init__(self):
        self.client_object = None

    def connectionMade(self):
        # Need to create a connection to a backend server...
        point = TCP4ClientEndpoint(reactor, "localhost", 8000)
        client_conn_deferred = point.connect(ClientFactory())
        client_conn_deferred.addCallback(self.connectionMadeForClient)

    def dataReceived(self, data):
        stdout.write("Received data\n")
        self.client_object.sendData(data)

    def connectionMadeForClient(self, client_protocol):
        stdout.write("Forwarding connection established\n")
        self.client_object = client_protocol
        client_protocol.server_obj = self

    def sendData(self, data):
        self.transport.write(data)

    # def connectionLost(self, reason=connectionDone):
    #     self.client_connection.transport.loseConnection()


class ServerFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Server()


def main():
    reactor.listenTCP(1234, ServerFactory())
    reactor.run()

if __name__ == "__main__":
    main()