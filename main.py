from threading import Thread
from time import sleep
from Network.ShowMeeting import *

def main(void):
    meeting = ShowMeeting()

    try:
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        pass

    meeting.stop()


if __name__ == '__main__':
    main(None)
