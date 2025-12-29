import sys
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

class PipelineBase:
    def __init__(self, name: str, pipeline_str: str):
        self.name = name
        self.pipeline_str = pipeline_str
        self.pipeline = None

    def _on_bus_message(self, bus: Gst.Bus, msg: Gst.Message):
        t = msg.type

        if t == Gst.MessageType.ERROR:
            err, dbg = msg.parse_error()
            print(f"[{self.name}] ERROR: {err.message}", file=sys.stderr)
            if dbg:
                print(f"[{self.name}] DEBUG: {dbg}", file=sys.stderr)
            self.stop()

        elif t == Gst.MessageType.EOS:
            print(f"[{self.name}] EOS")
            self.stop()

        elif t == Gst.MessageType.WARNING:
            err, dbg = msg.parse_warning()
            print(f"[{self.name}] WARNING: {err.message}", file=sys.stderr)
            if dbg:
                print(f"[{self.name}] DEBUG: {dbg}", file=sys.stderr)

        return True

    def start(self):
        if self.pipeline is not None:
            return

        self.pipeline = Gst.parse_launch(self.pipeline_str)

        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self._on_bus_message)

        ret = self.pipeline.set_state(Gst.State.PLAYING)
        if ret == Gst.StateChangeReturn.FAILURE:
            raise RuntimeError(f"[{self.name}] Kunde inte starta pipeline (PLAYING).")

        print(f"[{self.name}] STARTED")

    def stop(self):
        if self.pipeline is None:
            return
        print(f"[{self.name}] STOPPING ...")
        self.pipeline.set_state(Gst.State.NULL)
        self.pipeline = None
        print(f"[{self.name}] STOPPED")
