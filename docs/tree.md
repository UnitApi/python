```bash
tree -L 4 src
```
      
```bash
src
├── unitapi
│   ├── core
│   │   ├── client_fixed.py
│   │   ├── client.py
│   │   ├── __init__.py
│   │   └── server.py
│   ├── devices
│   │   ├── base.py
│   │   ├── camera.py
│   │   ├── gamepad.py
│   │   ├── gpio.py
│   │   ├── __init__.py
│   │   ├── keyboard.py
│   │   ├── microphone.py
│   │   ├── mouse.py
│   │   ├── remote_speaker_device.py
│   │   ├── remote_speaker_service.py
│   │   └── touchscreen.py
│   ├── __init__.py
│   ├── __main__.py
│   ├── main.py
│   ├── protocols
│   │   ├── base.py
│   │   ├── __init__.py
│   │   ├── mqtt.py
│   │   └── websocket.py
│   ├── security
│   │   ├── access_control.py
│   │   ├── authentication.py
│   │   ├── encryption.py
│   │   ├── __init__.py
│   ├── _version.py
│   └── _version.py.bak
└── __init__.py
```

```bash
tree -L 4 examples
```

```bash
examples
├── camera_capture.py
├── camera_frame_capture.py
├── device_discovery.py
├── docker
│   ├── docker-compose.yml
│   ├── README.md
│   ├── speaker-client
│   │   ├── client.py
│   │   ├── data
│   │   ├── Dockerfile
│   │   └── entrypoint.sh
│   └── speaker-server
│       ├── data
│       ├── Dockerfile
│       ├── entrypoint.sh
│       └── virtual_speaker.py
├── examples.md
├── input_devices.py
├── keyboard_text_input.py
├── microphone_audio_input.py
├── microphone_recording.py
├── mouse_movement.py
├── mouse_movement_pyautogui.py
├── pc
│   ├── camera
│   │   ├── camera_client.py
│   │   ├── camera_frame_client.py
│   │   ├── camera_server.py
│   │   ├── README.md
│   │   ├── remote_camera_capture.py
│   │   ├── remote_camera_client.py
│   │   ├── remote_camera_frame_capture.py
│   │   ├── remote_camera_frame_client.py
│   │   └── screenshot_client.py
│   ├── keyboard
│   │   ├── keyboard_client.py
│   │   ├── keyboard_server.py
│   │   ├── README.md
│   │   ├── README_remote_keyboard_fixed.md
│   │   ├── README_remote_keyboard.md
│   │   ├── remote_keyboard_client.py
│   │   ├── remote_keyboard_control_fixed.py
│   │   └── remote_keyboard_control.py
│   ├── microphone
│   │   ├── microphone_input_client.py
│   │   ├── microphone_recording_client.py
│   │   ├── microphone_server.py
│   │   └── README.md
│   ├── misc
│   │   ├── device_discovery.py
│   │   ├── input_devices.py
│   │   ├── README.md
│   │   ├── remote_control.py
│   │   └── ssh_connector.py
│   ├── mouse
│   │   ├── mouse_client.py
│   │   ├── mouse_pyautogui_client.py
│   │   ├── mouse_server.py
│   │   └── README.md
│   ├── README.md
│   └── speaker
│       ├── README.md
│       ├── remote_speaker_agent.md
│       ├── speaker_audio_playback_fixed.py
│       ├── speaker_audio_playback.py
│       ├── speaker_client.py
│       ├── speaker_playback_fixed.py
│       ├── speaker_playback.py
│       └── speaker_server.py
├── rpi
│   ├── camera
│   │   ├── camera_client.py
│   │   ├── camera_server.py
│   │   └── README.md
│   ├── gpio
│   │   ├── gpio_client.py
│   │   ├── gpio_server.py
│   │   ├── led_control.py
│   │   ├── README.md
│   │   └── sensors.py
│   ├── keyboard
│   │   ├── keyboard_client.py
│   │   ├── keyboard_server.py
│   │   ├── README.md
│   │   ├── remote_keyboard_server_installation.md
│   │   └── remote_keyboard_server.py
│   ├── mic
│   │   ├── microphone_client.py
│   │   ├── microphone_server.py
│   │   └── README.md
│   ├── mouse
│   │   ├── mouse_client.py
│   │   ├── mouse_server.py
│   │   └── README.md
│   ├── README.md
│   ├── respeaker
│   │   ├── README.md
│   │   ├── respeaker_client.py
│   │   └── respeaker_server.py
│   └── speaker
│       ├── README.md
│       ├── speaker_client.py
│       └── speaker_server.py
├── speaker_audio_playback_fixed.py
├── speaker_audio_playback.py
├── speaker_client.py
├── speaker_playback_fixed.py
├── speaker_playback_fix.md
├── speaker_playback.py
├── speaker_server.py
├── ssh_connector_example.py
├── stream_processing.py
└── take_screenshot.py
```