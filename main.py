from threading import Thread
from time import sleep
from Network.Lynks.LynksUser import LynksUser
from Network.GStreamer.GLibLoopThread import GLibLoopThread

import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst

def main(void):
    Gst.init(None)
    loop = GLibLoopThread()
    loop.start()

    user = LynksUser('testuser', 'test123', True)
    user.log_in()
    user.create_room()

    try:
        user.update_room()
    except KeyboardInterrupt:
        pass

    user.stop_room()
    loop.stop()


if __name__ == '__main__':
    main(None)
