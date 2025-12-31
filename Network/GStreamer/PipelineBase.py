import sys
import threading
import time
import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst

class PipelineBase:
    def __init__(self, name: str, pipeline_str: str):
        self.name = name
        self.pipeline_str = pipeline_str
        self.pipeline = None

        self._started_evt = threading.Event()
        self._error_evt = threading.Event()
        self._last_error = None

        self._bus = None
        self._bus_handler_id = None

    def _reset_signals(self):
        self._started_evt.clear()
        self._error_evt.clear()
        self._last_error = None

    def _on_bus_message(self, bus: Gst.Bus, msg: Gst.Message):
        t = msg.type

        if t == Gst.MessageType.ERROR:
            err, dbg = msg.parse_error()
            self._last_error = (err, dbg)
            print(f"[{self.name}] ERROR: {err.message}", file=sys.stderr)
            if dbg:
                print(f"[{self.name}] DEBUG: {dbg}", file=sys.stderr)
            self._error_evt.set()
            self.stop()

        elif t == Gst.MessageType.EOS:
            print(f"[{self.name}] EOS")
            self._error_evt.set()
            self.stop()

        elif t == Gst.MessageType.STATE_CHANGED:
            if msg.src == self.pipeline:
                old, new, pending = msg.parse_state_changed()
                if new == Gst.State.PLAYING:
                    self._started_evt.set()

        elif t == Gst.MessageType.WARNING:
            err, dbg = msg.parse_warning()
            print(f"[{self.name}] WARNING: {err.message}", file=sys.stderr)
            if dbg:
                print(f"[{self.name}] DEBUG: {dbg}", file=sys.stderr)

        return True

    def start(
        self,
        ok_timeout_s: float = 2.0,
        stable_s: float = 0.75,
    ) -> bool:

        if self.pipeline is not None:
            return True

        self._reset_signals()
        self.pipeline = Gst.parse_launch(self.pipeline_str)

        self._bus = self.pipeline.get_bus()
        self._bus.add_signal_watch()
        self._bus_handler_id = self._bus.connect("message", self._on_bus_message)

        ret = self.pipeline.set_state(Gst.State.PLAYING)
        if ret == Gst.StateChangeReturn.FAILURE:
            self.stop()
            return False

        print(f"[{self.name}] STARTING...")

        if not self._started_evt.wait(ok_timeout_s):
            if self._error_evt.is_set():
                return False
            print(f"[{self.name}] START TIMEOUT (no PLAYING within {ok_timeout_s}s)", file=sys.stderr)
            self.stop()
            return False

        t0 = time.monotonic()
        while time.monotonic() - t0 < stable_s:
            if self._error_evt.is_set():
                return False
            time.sleep(0.02)

        print(f"[{self.name}] STARTED (stable)")
        return True

    def stop(self):
        if self.pipeline is None:
            return
        print(f"[{self.name}] STOPPING ...")
        try:
            # Koppla ur bus watch för att minska risk för callbacks efter stop
            if self._bus is not None:
                if self._bus_handler_id is not None:
                    try:
                        self._bus.disconnect(self._bus_handler_id)
                    except Exception:
                        pass
                    self._bus_handler_id = None
                try:
                    self._bus.remove_signal_watch()
                except Exception:
                    pass
                self._bus = None

            self.pipeline.set_state(Gst.State.NULL)
        finally:
            self.pipeline = None
        print(f"[{self.name}] STOPPED")
