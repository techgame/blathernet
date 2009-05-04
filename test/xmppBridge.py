#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from getpass import getpass
import xmpp
from TG.blathernet import Blather, advertIdForNS

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherJabber(object):
    command_prefix = 'bot_'

    def __init__(self, jid, password, res = None):
        self.jid = xmpp.JID( jid)
        self.password = password
        self.res = (res or self.__class__.__name__)
        self.conn = None


    def log(self, s):
        """Logging facility, can be overridden in subclasses to log to file, etc.."""
        print '%s: %s' % (self.__class__.__name__, s, )

    def connect(self):
        if not self.conn:
            conn = xmpp.Client(self.jid.getDomain(), debug = [])
            
            if not conn.connect():
                self.log( 'unable to connect to server.')
                return None
            
            if not conn.auth(self.jid.getNode(), self.password, self.res):
                self.log( 'unable to authorize with server.')
                return None
            
            conn.RegisterHandler( 'message', self.onMessage)
            conn.sendInitPresence()
            self.conn = conn

        return self.conn

    _finished = False
    def quit(self):
        self._finished = True

    def send(self, user, text, in_reply_to = None):
        """Sends a simple message to the specified user."""
        mess = xmpp.Message( user, text)
        if in_reply_to:
            mess.setThread( in_reply_to.getThread())
            mess.setType( in_reply_to.getType())
        
        self.connect().send( mess)

    def onMessage(self, conn, mess):
        text = mess.getBody()
        print (text, mess.getFrom())
    
    def idle_proc(self):
        """This function will be called in the main loop."""
        pass

    def serve_forever(self, connect_callback = None, disconnect_callback = None):
        """Connects to the server and handles messages."""
        conn = self.connect()
        if conn:
            self.log('bot connected. serving forever.')
        else:
            self.log('could not connect to server - aborting.')
            return

        if connect_callback:
            connect_callback()

        while not self._finished:
            try:
                conn.Process(1)
                self.idle_proc()
            except KeyboardInterrupt:
                self.log('bot stopped by user request. shutting down.')
                break

        if disconnect_callback:
            disconnect_callback()



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    adChat = advertIdForNS('#demoChat')
    blather = Blather('JabberBridge')
    blather.routes.factory.connectAllMUDP()
    blather.run(True)

    blather.addAdvertRoutes(adChat)

    bj = BlatherJabber('shane.holloway@techgame.net', getpass())
    bj.targets = [
        'brian@techgame.net',
        #'shane@techgame.net',
        'lking@techgame.net',
        #'mottai@techgame.net',
        ]

    @blather.respondTo(adChat)
    def chatResponder(body, fmt, topic, mctx):
        print 'redirecting to jabber:', bj.targets
        body = body.decode('utf-8')
        for tgt in bj.targets:
            bj.send(tgt, 'from %s@blather: %s' % (topic, body))


    chatMsg = blather.newMsg(adChat)
    chatMsg.forward(None, False)
    def jabberResponder(conn, mess):
        body = mess.getBody()
        if not body: return
        who = str(mess.getFrom())

        body = body.encode("utf-8")
        cm = chatMsg.copy()
        cm.msg(body, 0, str(who))
        cm.send()

    bj.onMessage = jabberResponder
    bj.serve_forever()

