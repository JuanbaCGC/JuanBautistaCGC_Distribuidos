#!/usr/bin/env python3

import sys
import time
import Ice
Ice.loadSlice('iceflix.ice')
import IceFlix
import IceStorm
import uuid


class Main(IceFlix.Main):
    """Servant for the IceFlix.Main interface.

    Disclaimer: this is demo code, it lacks of most of the needed methods
    for this interface. Use it with caution
    """

    def getAuthenticator(self, current):  # pylint:disable=invalid-name, unused-argument
        "Return the stored Authenticator proxy."
        # TODO: implement
        return None

    def getCatalog(self, current):  # pylint:disable=invalid-name, unused-argument
        "Return the stored MediaCatalog proxy."
        # TODO: implement
        return None

    def getFileService(self, current):
        "Return the stored FileService proxy"
        return None

    def newService(self, proxy, service_id, current):  # pylint:disable=invalid-name, unused-argument
        "Receive a proxy of a new service."
        # TODO: implement
        return

    def announce(self, proxy, service_id, current):  # pylint:disable=invalid-name, unused-argument
        "Announcements handler."
        # TODO: implement
        return
    
class ServerMain(Ice.Application):
    def run(self, args):
        broker = self.communicator()
        servant = Main()
        adapter = broker.createObjectAdapterWithEndpoints("MainAdapter",'default')
        
        proxy = adapter.add(servant, broker.stringToIdentity("main1"))

        topic_manager = IceStorm.TopicManagerPrx.checkedCast(broker.propertyToProxy("IceStorm.TopicManager"))
        topicPrx = topic_manager.retrieve('Announcements')
        
        pub = topicPrx.getPublisher()
        announcement = IceFlix.AnnouncementPrx.uncheckedCast(pub)
        
        if not announcement:
            raise RuntimeError("Invalid publisher proxy")
        
        announcement.announce(proxy,str(uuid.uuid4()))

        adapter.activate()
        time.sleep(5)
        self.shutdownOnInterrupt()
        self._communicator.destroy()
        broker.waitForShutdown()
        return 0

if __name__ == '__main__':
    app=ServerMain()
    exit_status = app.main(sys.argv)
    sys.exit(exit_status)