import json
from time import sleep

from . import LynksService

class LynksUser:
    def __init__(self,
                 username: str,
                 password: str,
                 sub_and_pub: bool = False):
        self.video_room = None
        self.username = username
        self.password = password
        self.token = None
        self.service = LynksService.LynksService()
        self.sub_and_pub = sub_and_pub


    def to_json(self) -> dict[str, str]:
        temp_json = {"username": self.username, "password": self.password}
        return temp_json


    # log in
    def log_in(self):
        token = self.service.log_in(self)

        if token == 'fail':
            print('Login failed')

        else:
            self.token = token
            print("Logged in successfully")


    def join_room(self, room_id: int):
        self.video_room = self.service.join_room(self.token, room_id)
        self.video_room.subscribe = self.sub_and_pub

    def create_room(self):
        self.video_room = self.service.create_room(self.token)
        self.video_room.subscribe = self.sub_and_pub

    def update_room(self):
        participants: list[int] = []

        while True:
            print("checking new participants")
            check_participants = self.service.get_participants(self.token, self.video_room.room_id)

            if not check_participants:
                sleep(5)
                continue

            for participant in check_participants:
                if participant in participants:
                    continue

                print(f"Participant found: {participant}")

                ok = self.video_room.subscribe_to_feed_retry(
                    participant,
                    max_tries=10,
                    total_budget_s=10.0,
                    backoff_s=0.2
                )

                if ok:
                    participants.append(participant)
                else:
                    print("Could not establish stable connection. Exiting.")
                    return

            sleep(5)


    def stop_room(self):
        if self.video_room is not None:
            self.video_room.stop()