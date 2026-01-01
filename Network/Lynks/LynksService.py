# High level implementation of sending and receiving requests
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .LynksUser import LynksUser

from . import LynksRepo
from . import VideoRoom

class LynksService:
    def __init__(self):
        self.repo = LynksRepo.LynksRepo()

    def log_in(self, user:LynksUser) -> str:
        return self.repo.log_in(user)

    def create_room(self, token: str) -> VideoRoom.VideoRoom:
        # Create and retrieve room id
        r = self.repo.create_room(token)

        print(r)

        # Construct a video room using the room id
        room = VideoRoom.VideoRoom(int(r))
        room.start()

        return room

    def join_room(self, room_id: int) -> VideoRoom.VideoRoom:
        # Create video room
        room = VideoRoom.VideoRoom(int(room_id))
        room.start()

        return room

    def get_participants(self, token:str, room_id:int) -> list[int]:
        return self.repo.list_participants(token, room_id)
