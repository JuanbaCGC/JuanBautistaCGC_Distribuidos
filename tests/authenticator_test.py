#!/usr/bin/env python3

import sys
import time
import Ice
Ice.loadSlice('iceflix.ice')
import IceFlix
import IceStorm
import uuid


class Auth(IceFlix.Authenticator):
    """Servant for the IceFlix.Authenticator interface.

    Disclaimer: this is demo code, it lacks of most of the needed methods
    for this interface. Use it with caution
    """
    
class ServerMain(Ice.Application):
    def run(self, args):
        broker = self.communicator()
        servant = Auth()
        adapter = broker.createObjectAdapterWithEndpoints("AuthAdapter",'default')
        
        proxy = adapter.add(servant, broker.stringToIdentity("auth1"))


        topic_manager = IceStorm.TopicManagerPrx.checkedCast(broker.propertyToProxy("IceStorm.TopicManager"))
        topicPrx = topic_manager.retrieve('UserUpdates')
        
        pub = topicPrx.getPublisher()
        announcement = IceFlix.UserUpdatePrx.uncheckedCast(pub)
        
        if not announcement:
            raise RuntimeError("Invalid publisher proxy")
        
        announcement.newUser("JUANBA","12345",str(uuid.uuid4()))
        announcement.newToken("JUANBA","LJLKSJDFLKAJSLKDFJLAKSJFI4UROWJE",str(uuid.uuid4()))
        announcement.revokeToken("lsjLFJKASLK", str(uuid.uuid4()))
        time.sleep(5)
        adapter.activate()
        
        self.shutdownOnInterrupt()
        self._communicator.destroy()
        broker.waitForShutdown()
        return 0

if __name__ == '__main__':
    app=ServerMain()
    exit_status = app.main(sys.argv)
    sys.exit(exit_status)