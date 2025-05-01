# UnitAPI Starlark Configuration for Speaker Devices

VERSION = "1.0"

# Define extensions
speaker_ext = extension(
    name = "speaker",
    version = ">=1.0.0",
    config = {
        "sample_rate": 48000,
        "channels": 2,
        "bit_depth": 16
    }
)

audio_processing_ext = extension(
    name = "audio_processing",
    version = ">=1.0.0",
    config = {
        "equalizer": True,
        "spatial_audio": True,
        "volume_normalization": True
    }
)

# Define devices
living_room_speaker = device(
    id = "living-room-speaker",
    type = "speaker",
    capabilities = ["playback", "streaming", "bluetooth"]
)

kitchen_speaker = device(
    id = "kitchen-speaker",
    type = "speaker",
    capabilities = ["playback", "voice_assistant"]
)

rpi_speaker = device(
    id = "rpi-speaker",
    type = "raspberry_pi_speaker",
    capabilities = ["playback", "streaming", "voice_feedback"]
)

# Define pipelines
# Define a music source device
music_source = device(
    id = "music-source",
    type = "custom",
    capabilities = ["storage", "streaming"]
)

music_playback = pipeline(
    name = "music-playback",
    source = music_source.id,
    target = living_room_speaker.id,
    steps = [
        step("load", source="/music/playlist.m3u"),
        step("process", equalizer_preset="music"),
        step("play", volume=0.7, repeat=True)
    ]
)

voice_assistant_output = pipeline(
    name = "voice-assistant-output",
    target = kitchen_speaker.id,
    steps = [
        step("generate", text_to_speech=True, voice="female"),
        step("process", clarity=True, speed=1.1),
        step("play", volume=0.8, interrupt_current=True)
    ]
)

# Function to create a multi-room audio pipeline
def create_multiroom_pipeline(name, sources, targets, volume=0.6):
    """Create a multi-room audio pipeline"""
    return pipeline(
        name = name,
        steps = [
            step("sync", devices=targets),
            step("load", source=sources),
            step("process", latency_compensation=True),
            step("play", volume=volume, synchronized=True)
        ]
    )

# Create a multi-room audio pipeline
whole_house_audio = create_multiroom_pipeline(
    name = "whole-house-audio",
    sources = ["/music/ambient.mp3", "/music/relaxing.mp3"],
    targets = [living_room_speaker.id, kitchen_speaker.id, rpi_speaker.id],
    volume = 0.5
)

# Alarm system pipeline
alarm_system = pipeline(
    name = "alarm-system",
    target = [living_room_speaker.id, kitchen_speaker.id],
    steps = [
        step("load", source="/sounds/alarm.wav"),
        step("process", volume_boost=True),
        step("play", volume=1.0, repeat=True, interrupt_current=True)
    ]
)
