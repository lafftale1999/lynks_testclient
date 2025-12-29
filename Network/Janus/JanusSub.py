from Network.GStreamer.PipelineBase import PipelineBase
from Common import CommonDefines
from Utilities import StringManip
from Utilities.StringManip import squash_string


class JanusSub(PipelineBase):
    def __init__(self,
                 endpoint: str,
                 room_id: int,
                 feed_id: int,
                 video_sink: str = "autovideosink",
                 audio_sink: str = "autoaudiosink"):

        janus_src = f"""
            {CommonDefines.JANUS_MEDIA_SRC} name=src
                signaller:janus-endpoint={endpoint}
                signaller:janus-room-id={room_id}
                signaller:janus-feed-id={feed_id}"""

        pipeline_str = f"""
            src. !
                queue !
                application/x-rtp,media=video !
                decodebin !
                videoconvert !
                {video_sink} sync=false
                
            src. !
                queue !
                application/x-rtp,media=audio !
                decodebin !
                audioconvert !
                audioresample !
                {audio_sink} sync=false
            """

        super().__init__("Subscriber", squash_string(pipeline_str))