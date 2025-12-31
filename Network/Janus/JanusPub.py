from Network.GStreamer.PipelineBase import *
from Utilities.StringManip import *
from Common import CommonDefines

class JanusPub(PipelineBase):
    def __init__(self,
                 endpoint: str,
                 room_id: int,
                 feed_id: int,
                 video_src: str = "ksvideosrc",
                 audio_src: str = "wasapi2src"):

        janus_sink = f"""
            {CommonDefines.JANUS_MEDIA_SINK} name=jsink
            signaller::janus-endpoint={endpoint} 
            signaller::room-id={room_id} 
            signaller::feed-id={feed_id}
        """

        pipeline_str = f"""
        {janus_sink}
        
        {video_src} !
            queue !
            videoconvert !
            video/x-raw,framerate=30/1 !
            vp8enc deadline=1 cpu-used=8 !
            queue !
            jsink.video_0
        
        {audio_src} !
            queue !
            audioconvert !
            audioresample !
            audio/x-raw,rate=48000,channels=2 !
            opusenc bitrate=64000 !
            queue !
            jsink.audio_0
        """

        super().__init__("Publisher", squash_string(pipeline_str))