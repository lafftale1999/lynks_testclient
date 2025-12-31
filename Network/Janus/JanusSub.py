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
                signaller::janus-endpoint={endpoint}
                signaller::room-id={room_id}
                signaller::producer-peer-id={feed_id}
        """

        pipeline_str = f"""
        {janus_src}

        src. !
          queue !
          application/x-rtp,media=video !
          rtpvp8depay !
          vp8dec !
          videoconvert !
          {video_sink}

        src. !
          queue !
          application/x-rtp,media=audio !
          rtpopusdepay !
          opusdec !
          audioconvert !
          audioresample !
          {audio_sink}
        """

        super().__init__("Subscriber", squash_string(pipeline_str))