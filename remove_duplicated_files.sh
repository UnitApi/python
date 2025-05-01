#!/bin/bash
# Script to remove duplicated files from examples directory

# Files to remove
files=(
  "examples/camera_capture.py"
  "examples/camera_frame_capture.py"
  "examples/device_discovery.py"
  "examples/examples.md"
  "examples/input_devices.py"
  "examples/keyboard_text_input.py"
  "examples/microphone_audio_input.py"
  "examples/microphone_recording.py"
  "examples/mouse_movement.py"
  "examples/mouse_movement_pyautogui.py"
  "examples/speaker_audio_playback.py"
  "examples/speaker_audio_playback_fixed.py"
  "examples/speaker_client.py"
  "examples/speaker_playback.py"
  "examples/speaker_playback_fix.md"
  "examples/speaker_playback_fixed.py"
  "examples/speaker_server.py"
  "examples/ssh_connector_example.py"
  "examples/stream_processing.py"
  "examples/take_screenshot.py"
)

# Remove each file
for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "Removing $file"
    rm "$file"
  else
    echo "File $file does not exist"
  fi
done

echo "All duplicated files have been removed."
