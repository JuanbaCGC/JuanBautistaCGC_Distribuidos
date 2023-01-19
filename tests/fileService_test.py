#!/usr/bin/env python3

import sys
import time
import Ice
Ice.loadSlice('iceflix.ice')
import IceFlix
import IceStorm
import uuid


class FileI(IceFlix.FileService):
    """Servant for the IceFlix.Authenticator interface.

    Disclaimer: this is demo code, it lacks of most of the needed methods
    for this interface. Use it with caution
    """
    
class ServerMain(Ice.Application):
    def run(self, args):
        broker = self.communicator()
        servant = FileI()
        adapter = broker.createObjectAdapterWithEndpoints("FileAdapter",'default')
        
        proxy = adapter.add(servant, broker.stringToIdentity("file1"))

        topic_manager = IceStorm.TopicManagerPrx.checkedCast(broker.propertyToProxy("IceStorm.TopicManager"))
        topicPrx = topic_manager.retrieve('FileAvailabilityAnnounces')
        
        pub = topicPrx.getPublisher()
        announcement = IceFlix.FileAvailabilityAnnouncePrx.uncheckedCast(pub)
        
        if not announcement:
            raise RuntimeError("Invalid publisher proxy")
        
        announcement.announceFiles([str(uuid.uuid4()),"lasjdlsjlkjf","123456789"], str(uuid.uuid4()))
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