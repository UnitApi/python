# UnitAPI Simple DSL Configuration for Multi-Device Workflow

version "1.0"

# Load extensions for all required device types
load camera version=">=1.0.0" config={resolution:"1080p", fps:30}
load microphone version=">=1.0.0" config={sample_rate:44100, channels:2}
load speaker version=">=1.0.0" config={sample_rate:48000, channels:2}
load keyboard version=">=1.0.0" config={layout:"us", hotkeys:true}
load mouse version=">=1.0.0" config={sensitivity:1.2, acceleration:true}
load gpio version=">=1.0.0" config={pin_numbering:"BCM", safety_checks:true}
load touchscreen version=">=1.0.0" config={multi_touch:true}
load gamepad version=">=1.0.0" config={controller_type:"xbox"}

# Define devices
device pc-camera type=camera with image_capture,video_streaming
device pc-microphone type=microphone with recording,streaming
device pc-speaker type=speaker with playback,streaming
device pc-keyboard type=keyboard with typing,hotkeys
device pc-mouse type=mouse with movement,buttons,scrolling
device pc-touchscreen type=touchscreen with touch,multi_touch,gestures
device pc-gamepad type=gamepad with buttons,triggers,joysticks,rumble

device rpi-camera type=raspberry_pi_camera with image_capture,video_streaming,night_vision
device rpi-microphone type=raspberry_pi_microphone with recording,streaming,voice_commands
device rpi-speaker type=raspberry_pi_speaker with playback,streaming
device rpi-gpio type=raspberry_pi_gpio with digital_io,pwm,i2c,spi

# Define a media center control pipeline
pipeline media-center-control:
  # Voice command input
  listen source=pc-microphone wake_word="hey_media" continuous=true
  
  # Process voice commands
  recognize engine="local" language="en-US" commands=["play","pause","volume","channel"]
  
  # Map commands to actions
  map "play *" action="play_content" params={content_name:"$1"}
  map "pause" action="pause_content"
  map "volume up" action="volume_change" params={change:+10}
  map "volume down" action="volume_change" params={change:-10}
  map "channel *" action="change_channel" params={channel:"$1"}
  
  # Execute media actions
  execute target=pc-speaker
  
  # Provide visual feedback
  display target=pc-touchscreen message="Command: $command" duration=3
end

# Define a gaming control pipeline
pipeline gaming-control from pc-gamepad to pc-keyboard,pc-mouse:
  # Capture gamepad input
  capture events=all
  
  # Map gamepad controls to keyboard/mouse actions
  map button="a" to="keyboard.key_press" params={key:"space"}
  map button="b" to="keyboard.key_press" params={key:"escape"}
  map button="x" to="keyboard.key_press" params={key:"e"}
  map button="y" to="keyboard.key_press" params={key:"q"}
  
  map left_trigger to="mouse.right_click"
  map right_trigger to="mouse.left_click"
  
  map left_stick to="mouse.move" params={relative:true, multiplier:10}
  map right_stick to="keyboard.arrow_keys"
  
  # Provide haptic feedback
  on event="game_hit" do="rumble" params={strength:0.8, duration:0.3}
  on event="game_explosion" do="rumble" params={strength:1.0, duration:0.7}
end

# Define a home automation pipeline
pipeline home-automation from pc-microphone,pc-touchscreen to rpi-gpio:
  # Accept input from multiple sources
  listen source=pc-microphone wake_word="hey_home" continuous=true
  touch source=pc-touchscreen
  
  # Process commands from either source
  recognize source="microphone" engine="local" language="en-US"
  detect source="touchscreen" gestures=true
  
  # Map voice commands to actions
  map voice="lights on *" action="set_gpio" params={room:"$1", state:"on"}
  map voice="lights off *" action="set_gpio" params={room:"$1", state:"off"}
  map voice="fan on" action="set_gpio" params={device:"fan", state:"on"}
  map voice="fan off" action="set_gpio" params={device:"fan", state:"off"}
  
  # Map touch gestures to actions
  map gesture="tap" target="room_button" action="toggle_light"
  map gesture="swipe_up" action="increase_brightness"
  map gesture="swipe_down" action="decrease_brightness"
  
  # Execute GPIO actions
  execute target=rpi-gpio mapping={
    "living_room_light": 17,
    "kitchen_light": 18,
    "bedroom_light": 22,
    "fan": 23
  }
  
  # Provide feedback
  speak target=pc-speaker message="$action completed"
  display target=pc-touchscreen message="$action completed" duration=2
end

# Define a security system pipeline
pipeline security-system:
  # Monitor security cameras
  monitor source=rpi-camera mode="motion_detection" sensitivity=0.7
  
  # Monitor door/window sensors
  read source=rpi-gpio pins=[5,6,7] names=["front_door","back_door","window"] pull="up"
  
  # When motion is detected
  on motion:
    capture_image device=rpi-camera resolution="1080p" save="/security/captures/{timestamp}.jpg"
    record_video device=rpi-camera duration=30 save="/security/videos/{timestamp}.mp4"
  end
  
  # When a door/window is opened
  on gpio_change pin="front_door" to="low":
    log message="Front door opened at {timestamp}"
    if security_mode=="armed":
      sound_alarm device=rpi-speaker source="/sounds/alarm.wav" volume=1.0 loop=true
      send_notification method="email" to="user@example.com" subject="Security Alert" body="Front door opened at {timestamp}"
    end
  end
  
  # Arm/disarm via voice command
  listen source=pc-microphone wake_word="security" continuous=true
  recognize commands=["arm","disarm"] auth_required=true
  
  on command="arm":
    set security_mode="armed"
    speak target=pc-speaker message="Security system armed"
    set_gpio target=rpi-gpio pin=12 value="high" # Security indicator LED
  end
  
  on command="disarm":
    set security_mode="disarmed"
    speak target=pc-speaker message="Security system disarmed"
    set_gpio target=rpi-gpio pin=12 value="low" # Security indicator LED
    stop_sound device=rpi-speaker # Stop alarm if it's sounding
  end
end

# Define a multi-room audio pipeline
pipeline multi-room-audio from pc-touchscreen to pc-speaker,rpi-speaker:
  # Control interface
  touch source=pc-touchscreen
  
  # Map touch controls to audio actions
  map gesture="tap" target="play_button" action="toggle_playback"
  map gesture="swipe_left" action="previous_track"
  map gesture="swipe_right" action="next_track"
  map gesture="pinch" action="volume" params={mode:"adjust"}
  
  # Room selection
  map tap="living_room_button" action="select_room" params={room:"living_room"}
  map tap="kitchen_button" action="select_room" params={room:"kitchen"}
  map tap="all_rooms_button" action="select_room" params={room:"all"}
  
  # Execute audio playback
  play source="/music/playlist.m3u" targets={
    "living_room": pc-speaker,
    "kitchen": rpi-speaker,
    "all": [pc-speaker, rpi-speaker]
  }
  
  # Synchronize audio between rooms when playing to all
  on room="all":
    sync devices=[pc-speaker, rpi-speaker] master=pc-speaker
  end
end

# Start commands (optional)
# start media-center-control
# start home-automation
# start security-system
