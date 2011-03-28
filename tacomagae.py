"""
# tacomagae.py

tacomad client for Google App Engine (over XMPP)

Usage:

    import tacomagae

    # tacomad@tacomad.com is the Jabber ID of the tacomad process relaying
    # messages.
    irc_notifier = tacomagae.IRCNotifier('tacomad@tacomad.com')
    irc_notifier.message('#tacomad', 'hello from google app engine')
"""


try:
    import simplejson as json
except ImportError:
    import json

from google.appengine.api import xmpp


class OutgoingIRCMessage(object):
    """Represent an outgoing IRC message."""

    def __init__(self, target, body):
        """Initialize a new OutgoingIRCMessage.

        Arguments:
        target -- the nick or channel the message will go to
        body -- the message text
        """
        self._target = target
        self._body = body

    @property
    def json(self):
        return json.dumps({'target': self._target, 'body': self._body})


class IRCNotifier(object):

    def __init__(self, tacomad_jid):
        """Initialize a new IRCNotifier.

        Arguments:
        tacomad_jid -- the JID (Jabber ID) of the tacomad process that relays
                       messages to IRC.
        """
        self._tacomad_jid = tacomad_jid

    def message(self, target, body):
        """Tell tacomad to send a private message."""
        outgoing_irc_message = OutgoingIRCMessage(target, body)
        xmpp.send_message(self._tacomad_jid, outgoing_irc_message.json)
