from ..Janus import JanusSub, JanusPub
from Common.CommonDefines import *

import time

"""
The VideoRoom must have a room_id as it can't create
a room by itself.
"""
class VideoRoom:
    def __init__(self,
                 room_id: int = None,
                 feed_id: int = 1111,
                 endpoint: str = JANUS_WEBSOCKET_ENDPOINT,
                 publish: bool = True,
                 subscribe: bool = False):
        self.endpoint = endpoint
        self.room_id = room_id
        self.feed_id = feed_id
        self.publish = publish
        self.subscribe = subscribe

        self.publishing_pipe = None
        self.subscribing_pipe = None

        if room_id is None:
            print("Invalid room id")


    def start(self):
        self.publish_to_feed()

    def stop(self):
        if self.publishing_pipe is not None:
            self.publishing_pipe.stop()

        if self.subscribing_pipe is not None:
            self.subscribing_pipe.stop()

    def publish_to_feed(self):
        if self.publish:
            self.publishing_pipe = JanusPub.JanusPub(self.endpoint, self.room_id, self.feed_id)
            self.publishing_pipe.start()


    def subscribe_to_feed_once(self, incoming_feed_id: int) -> bool:
        if not self.subscribe:
            return False

        sub = JanusSub.JanusSub(self.endpoint, self.room_id, incoming_feed_id)

        ok = sub.start(ok_timeout_s=1.5, stable_s=0.75)

        if ok:
            self.subscribing_pipe = sub
            return True

        return False

    def subscribe_to_feed_retry(
        self,
        incoming_feed_id: int,
        max_tries: int = 10,
        total_budget_s: float = 10.0,
        backoff_s: float = 0.2,
    ) -> bool:

        deadline = time.monotonic() + total_budget_s
        last_ok = False

        for attempt in range(1, max_tries + 1):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break

            print(f"Trying to subscribe to {incoming_feed_id} ({attempt}/{max_tries}) "
                  f"[~{remaining:.2f}s left]")

            ok = self.subscribe_to_feed_once(incoming_feed_id)
            if ok:
                print(f"Successfully subscribed (stable) to {incoming_feed_id}")
                return True

            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            time.sleep(min(backoff_s, remaining))

        print(f"Failed to subscribe to {incoming_feed_id} within budget "
              f"({total_budget_s}s) / tries ({max_tries})")
        return False