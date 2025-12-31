# Low level implementation of sending and receiving requests
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .LynksUser import LynksUser

from Common import CommonDefines
import requests
import json
from typing import List



class LynksRepo:
    def __init__(self,
                 url: str = CommonDefines.LYNKS_ENDPOINT
                 ):
        self.url = url


    def log_in(self, user: LynksUser) -> str:
        headers = {'content-type': 'application/json'}

        r = requests.post(
            self.url + '/login',
            json=user.to_json(),
            headers=headers
        )

        if r.status_code == 200 or r.json()['action'] == 'success':
            print(r.json())
            return r.json()['token']

        else:
            return "fail"


    def create_room(self, token: str) -> str:
        headers = {'content-type': 'application/json',
                   'authorization': token}

        r = requests.post(
            self.url + '/create',
            json={},
            headers=headers
        )

        if r.status_code == 200 or r.json()['action'] == 'success':
            print(r.json())
            return r.json()['room_id']

        else:
            return "fail"

    def join_room(self, token:str, room_id: int) -> list[int]:
        return self.list_participants(token, room_id)

    def list_participants(self, token: str, room_id: int) -> list[int] | None:
        headers = {
            'authorization': token
        }

        data = {"room_id": room_id}

        r = requests.post(
            self.url + '/list_participants',
            json=data,
            headers=headers
        )

        if r.status_code != 200:
            return None

        payload = r.json()
        print(payload)

        if payload.get('action') != 'success':
            return None

        return payload.get('publishers', [])