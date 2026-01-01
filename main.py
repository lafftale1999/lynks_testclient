from Network.Lynks.LynksUser import LynksUser
from Network.GStreamer.GLibLoopThread import GLibLoopThread
import argparse

import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst


def parse_args():
    parser = argparse.ArgumentParser(description="Create or join room")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--create", "-c", action="store_true", help="Create room")
    group.add_argument("--join", "-j", metavar="ROOM_ID", type=int, help="Join room by room id")

    parser.add_argument(
        "--sub", "-s",
        action="store_true",
        help="Subscribe to publishing streams in the room",
    )

    parser.add_argument(
        "-p", "--password",
        metavar="PASSWORD",
        help="Set password for Lynks user"
    )

    parser.add_argument(
        "-u", "--username",
        metavar="USERNAME",
        help="Set username for Lynks user"
    )

    return parser.parse_args()


def main():
    args = parse_args()

    if args.join is not None and args.join <= 0:
        print("Invalid room id. Must be a positive integer.")
        return 2

    Gst.init(None)
    loop = GLibLoopThread()
    loop.start()

    user = None

    try:
        subscribe = bool(args.sub)

        if args.password is not None and args.username is not None:
            user = LynksUser(args.username, args.password, True, subscribe)
        else:
            user = LynksUser("testuser", "test123", True, subscribe)

        user.log_in()

        if args.create:
            room_id = user.create_room()
            if room_id is not None:
                print(f"Room created. Room ID: {room_id}")

        elif args.join is not None:
            user.join_room(args.join)
            print(f"Joined room: {args.join}")

        user.update_room()

    except KeyboardInterrupt:
        pass
    finally:
        if user is not None:
            try:
                user.stop_room()
            except Exception:
                pass
        loop.stop()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
