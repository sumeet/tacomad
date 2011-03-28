# tacomad.py (pronounced tacoma d)

Relay messages from Jabber to IRC. Messages are JSON strings containing `to`,
the IRC private message target (a nick or a channel) and `body`, the message
text. Example:

    {"to": "sumeet", "body": "hi :)))"}

tacomad's Jabber user needs to be friends with the user that sends messages
(for example, a Google App Engine XMPP instance). Sign in as tacomad's Jabber
user manually and send an invite to make sure.

Run this with `python tacomad.py` after editing the module to change
configuration constants.

tacomad has external dependencies: twisted, wokkel


# tacomagae.py

tacomad client for Google App Engine (over XMPP)

Usage:

    import tacomagae

    # tacomad@tacomad.com is the Jabber ID of the tacomad process relaying
    # messages.
    irc_notifier = tacomagae.IRCNotifier('tacomad@tacomad.com')
    irc_notifier.message('#tacomad', 'hello from google app engine')
