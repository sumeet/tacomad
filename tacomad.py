"""
# tacomad.py (pronounced tacoma d)

Relay messages from Jabber to IRC. Messages are JSON strings containing `to`,
the IRC private message target (a nick or a channel) and `body`, the message
text. Example:

    {"to": "sumeet", "body": "hi :)))"}

tacomad's Jabber user needs to be friends with the user that sends messages
(for example, a Google App Engine XMPP instance). Sign in as tacomad's Jabber
user manually and send an invite to make sure.

Run this with `python tacomad.py`.

tacomad has external dependencies: twisted, wokkel
"""
import Queue
import sys

try:
    import simplejson as json
except ImportError:
    import json
from twisted.internet import reactor, protocol, ssl
from twisted.python import log
from twisted.words.protocols import irc, jabber
import wokkel.client
import wokkel.xmppim


NICK = 'tacomad'
IRC_SERVER_HOST = 'irc.efnet.net'
IRC_SERVER_PORT = 6667
IRC_SERVER_PASSWORD = None
IRC_SERVER_SSL = False
IRC_JOIN_CHANNELS = ('#tacomad',)
JABBER_USERNAME = 'tacomad@tacomad.com'
JABBER_PASSWORD = 'tacomad'
JABBER_HOST = 'talk.google.com'


# Message queue for communication from XMPP to IRC.
xmpp_to_irc_queue = Queue.Queue()


class XMPPProtocol(wokkel.xmppim.MessageProtocol):

    def connectionMade(self):
        log.msg('Connected.')
        self.send(wokkel.xmppim.AvailablePresence())

    def connectionLost(self, reason):
        log.msg('Connection lost: %s' % reason)

    def onMessage(self, message):
        """Process new received messages and insert new commands into
        `xmpp_to_irc_queue`.
        """
        log.msg('Received Command: %s' % message.body)
        xmpp_to_irc_queue.put(json.loads(str(message.body)))


class IRCProtocol(irc.IRCClient):
    nickname = NICK
    username = NICK
    realname = NICK
    password = IRC_SERVER_PASSWORD

    def _handle_commands_from_xmpp(self):
        """Listen for new commands in `xmpp_to_irc_queue` to relay to our IRC
        connection.
        """
        # TODO This assumes every command will be a private message.
        while True:
            command = xmpp_to_irc_queue.get()
            log.msg('Received command: %r' % command)
            self.msg(command['to'].encode('utf-8'),
                     command['body'].encode('utf-8'))

    def signedOn(self):
        log.msg('Signed into IRC.')
        for channel in IRC_JOIN_CHANNELS:
            self.join(channel)

        reactor.callInThread(self._handle_commands_from_xmpp)


class IRCFactory(protocol.ClientFactory):
    protocol = IRCProtocol

    def startedConnecting(self, connector):
        log.msg('Started connecting to IRC.')

    def clientConnectionLost(self, connector, reason):
        log.err('Connection lost: %s' % reason)
        connector.connect()


if __name__ == '__main__':
    log.startLogging(sys.stdout)

    xmpp_client = wokkel.client.XMPPClient(
                                         jabber.jid.internJID(JABBER_USERNAME),
                                           JABBER_PASSWORD,
                                           JABBER_HOST)
    xmpp_protocol = XMPPProtocol()
    xmpp_protocol.setHandlerParent(xmpp_client)
    xmpp_client.startService()

    irc_bot = IRCFactory()
    if IRC_SERVER_SSL:
        reactor.connectSSL(IRC_SERVER_HOST, IRC_SERVER_PORT, irc_bot,
                           ssl.ClientContextFactory())
    else:
        reactor.connectTCP(IRC_SERVER_HOST, IRC_SERVER_PORT, irc_bot)

    reactor.run()
