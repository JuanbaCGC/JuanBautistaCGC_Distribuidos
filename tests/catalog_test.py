#!/usr/bin/env python3

import sys
import time
import Ice
Ice.loadSlice('iceflix.ice')
import IceFlix
import IceStorm
import uuid


class Catalog(IceFlix.MediaCatalog):
    """Servant for the IceFlix.MediaCatalog interface.

    Disclaimer: this is demo code, it lacks of most of the needed methods
    for this interface. Use it with caution
    """
    
class ServerMain(Ice.Application):
    def run(self, args):
        broker = self.communicator()
        servant = Catalog()
        adapter = broker.createObjectAdapterWithEndpoints("CatalogAdapter",'default')
        
        proxy = adapter.add(servant, broker.stringToIdentity("catalog1"))

        topic_manager = IceStorm.TopicManagerPrx.checkedCast(broker.propertyToProxy("IceStorm.TopicManager"))

        topicPrx = topic_manager.retrieve('Announcements')
        pub = topicPrx.getPublisher()
        announcement = IceFlix.AnnouncementPrx.uncheckedCast(pub)
        announcement.announce(proxy,str(uuid.uuid4()))

        topicPrx = topic_manager.retrieve('CatalogUpdates')
        
        pub = topicPrx.getPublisher()
        announcement = IceFlix.CatalogUpdatePrx.uncheckedCast(pub)
        
        if not announcement:
            raise RuntimeError("Invalid publisher proxy")
        
        announcement.renameTile("12345","Harry Potter y la piedra filosofal",str(uuid.uuid4()))
        announcement.addTags("12345","Juanba",["magos","escobas","acción","fantástica"],str(uuid.uuid4()))
        announcement.removeTags("12345","Juanba",["magos","escobas","fantástica"],str(uuid.uuid4()))

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