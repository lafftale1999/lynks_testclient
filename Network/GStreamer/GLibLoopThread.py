from threading import Thread

import gi
gi.require_version('Glib','2')
from gi.repository import GLib

gi.require_version('GLib', "2.0")

class GLibLoopThread():
    def __init__(self):
        self.loop = GLib.MainLoop()
        self.thread = Thread(target=self.loop.run, daemon=True)

    def start(self):
        if not self.thread.is_alive():
            self.thread.start()

    def stop(self):
        if self.loop.is_running():
            self.loop.quit()

        if self.thread.is_alive():
            self.thread.join()