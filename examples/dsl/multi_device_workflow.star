# UnitAPI Starlark Configuration for Multi-Device Workflow

VERSION = "1.0"

# Define extensions for all required device types
camera_ext = extension(
    name = "camera",
    version = ">=1.0.0",
    config = {
        "resolution": "1080p",
        "fps": 30
    }
)

microphone_ext = extension(
    name = "microphone",
    version = ">=1.0.0",
    config = {
        "sample_rate": 44100,
        "channels": 2
    }
)

speaker_ext = extension(
    name = "speaker",
    version = ">=1.0.0",
    config = {
        "sample_rate": 48000,
        "channels": 2
    }
)

keyboard_ext = extension(
    name = "keyboard",
    version = ">=1.0.0",
    config = {
        "layout": "us"
    }
)

mouse_ext = extension(
    name = "mouse",
    version = ">=1.0.0",
    config = {
        "sensitivity": 1.2
    }
)

gpio_ext = extension(
    name = "gpio",
    version = ">=1.0.0",
    config = {
        "pin_numbering": "BCM"
    }
)

# Define devices
pc_camera = device(
    id = "pc-camera",
    type = "camera",
    capabilities = ["image_capture", "video_streaming"]
)

pc_microphone = device(
    id = "pc-microphone",
    type = "microphone",
    capabilities = ["recording", "streaming"]
)

pc_speaker = device(
    id = "pc-speaker",
    type = "speaker",
    capabilities = ["playback", "streaming"]
)

pc_keyboard = device(
    id = "pc-keyboard",
    type = "keyboard",
    capabilities = ["typing", "hotkeys"]
)

pc_mouse = device(
    id = "pc-mouse",
    type = "mouse",
    capabilities = ["movement", "buttons", "scrolling"]
)

rpi_camera = device(
    id = "rpi-camera",
    type = "raspberry_pi_camera",
    capabilities = ["image_capture", "video_streaming", "night_vision"]
)

rpi_microphone = device(
    id = "rpi-microphone",
    type = "raspberry_pi_microphone",
    capabilities = ["recording", "streaming", "voice_commands"]
)

rpi_speaker = device(
    id = "rpi-speaker",
    type = "raspberry_pi_speaker",
    capabilities = ["playback", "streaming"]
)

rpi_gpio = device(
    id = "rpi-gpio",
    type = "raspberry_pi_gpio",
    capabilities = ["digital_io", "pwm", "i2c", "spi"]
)

# Define a video conference pipeline using multiple devices
video_conference = pipeline(
    name = "video-conference",
    steps = [
        # Capture audio and video from local devices
        step("capture", 
            sources=[pc_camera.id, pc_microphone.id],
            video_settings={"resolution": "720p", "fps": 30},
            audio_settings={"sample_rate": 44100, "channels": 1}
        ),
        
        # Process the captured media
        step("process",
            video_processing={"background_blur": True, "noise_reduction": True},
            audio_processing={"echo_cancellation": True, "noise_suppression": True}
        ),
        
        # Stream to conference server
        step("stream",
            destination="rtmp://conference.example.com/live/user123",
            format="h264_aac"
        ),
        
        # Receive remote participants' streams
        step("receive",
            source="wss://conference.example.com/ws/room123",
            participants=["user456", "user789"]
        ),
        
        # Output to local devices
        step("output",
            video_target={"display": "primary"},
            audio_target=pc_speaker.id
        )
    ]
)

# Define a smart home control pipeline using multiple devices
def create_smart_home_pipeline():
    """Create a smart home control pipeline with multiple devices"""
    return pipeline(
        name = "smart-home-control",
        steps = [
            # Voice command input
            step("listen",
                source=pc_microphone.id,
                wake_word="hey_home",
                continuous=True
            ),
            
            # Process voice commands
            step("recognize",
                engine="local",
                language="en-US",
                commands=["lights", "temperature", "security", "music"]
            ),
            
            # Execute commands based on recognition
            step("execute",
                mapping={
                    "lights on": lambda: control_lights("on"),
                    "lights off": lambda: control_lights("off"),
                    "set temperature to *": lambda temp: set_temperature(temp),
                    "play music": lambda: play_music(),
                    "stop music": lambda: stop_music(),
                    "arm security": lambda: arm_security(),
                    "disarm security": lambda: disarm_security()
                }
            ),
            
            # Provide voice feedback
            step("respond",
                target=pc_speaker.id,
                text_to_speech=True,
                voice="female"
            )
        ]
    )

# Helper functions for smart home control
def control_lights(state):
    """Control smart home lights"""
    return [
        step("set_gpio",
            device=rpi_gpio.id,
            pin=17,
            value="HIGH" if state == "on" else "LOW"
        )
    ]

def set_temperature(temp):
    """Set smart home temperature"""
    return [
        step("send_command",
            protocol="mqtt",
            topic="home/thermostat/set",
            payload={"temperature": float(temp)}
        )
    ]

def play_music():
    """Play music on home speakers"""
    return [
        step("play_audio",
            device=rpi_speaker.id,
            source="/music/playlist.m3u",
            volume=0.7
        )
    ]

def stop_music():
    """Stop music on home speakers"""
    return [
        step("stop_audio",
            device=rpi_speaker.id
        )
    ]

def arm_security():
    """Arm home security system"""
    return [
        step("set_mode",
            system="security",
            mode="armed",
            delay=30  # 30 second delay
        ),
        step("set_gpio",
            device=rpi_gpio.id,
            pin=18,
            value="HIGH"  # Turn on security LED
        )
    ]

def disarm_security():
    """Disarm home security system"""
    return [
        step("set_mode",
            system="security",
            mode="disarmed"
        ),
        step("set_gpio",
            device=rpi_gpio.id,
            pin=18,
            value="LOW"  # Turn off security LED
        )
    ]

# Create the smart home pipeline
smart_home = create_smart_home_pipeline()

# Define a security monitoring pipeline
security_monitoring = pipeline(
    name = "security-monitoring",
    steps = [
        # Monitor security cameras
        step("monitor",
            sources=[rpi_camera.id],
            mode="motion_detection",
            sensitivity=0.7
        ),
        
        # When motion is detected
        step("on_motion",
            actions=[
                # Capture a high-res image
                step("capture_image",
                    device=rpi_camera.id,
                    resolution="1080p",
                    save_path="/security/captures/{timestamp}.jpg"
                ),
                
                # Start recording video
                step("record_video",
                    device=rpi_camera.id,
                    duration=30,  # seconds
                    save_path="/security/videos/{timestamp}.mp4"
                ),
                
                # Trigger alarm if system is armed
                step("conditional",
                    condition="security.mode == 'armed'",
                    then=[
                        # Sound alarm
                        step("play_audio",
                            device=rpi_speaker.id,
                            source="/sounds/alarm.wav",
                            volume=1.0,
                            loop=True
                        ),
                        
                        # Send notification
                        step("notify",
                            method="email",
                            recipient="user@example.com",
                            subject="Security Alert",
                            body="Motion detected at {timestamp}",
                            attach_image="{latest_capture}"
                        )
                    ]
                )
            ]
        )
    ]
)

# Define a remote control pipeline
remote_control = pipeline(
    name = "remote-control",
    steps = [
        # Capture keyboard and mouse input
        step("capture_input",
            devices=[pc_keyboard.id, pc_mouse.id],
            mode="all_events"
        ),
        
        # Process and forward to remote device
        step("forward",
            destination="tcp://192.168.1.100:5000",
            protocol="unitapi_remote",
            compression=True,
            encryption=True
        ),
        
        # Receive remote camera feed
        step("receive_video",
            source="tcp://192.168.1.100:5001",
            protocol="h264"
        ),
        
        # Display remote camera feed locally
        step("display",
            target="local_display",
            fullscreen=False,
            position={"x": 0, "y": 0, "width": 1280, "height": 720}
        )
    ]
)
