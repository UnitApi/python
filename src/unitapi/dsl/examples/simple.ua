# UnitAPI Simple DSL Configuration

version "1.0"

# Load extensions
load keyboard version=">=1.0.0" config={layout:"us"}
load mouse version=">=1.0.0" config={sensitivity:1.5}
load gpio

# Define devices
device pc-main type=computer with keyboard,mouse,display
device rpi-remote type=raspberry_pi with gpio,camera
device arduino-sensor type=arduino with gpio,serial

# Define pipelines
pipeline remote-control from pc-main to rpi-remote:
  capture keyboard
  filter ctrl,alt,f1-f12
  forward destination="tcp://192.168.1.100:5000"
end

pipeline gesture-control:
  capture mouse
  detect gestures
  on circle=rotate_camera
  on swipe_left=previous_slide
end

# Comments are supported
pipeline sensor-monitor from arduino-sensor to pc-main:
  read pins=[A0,A1,A2]
  transform mode=analog_to_digital
  publish topic="mqtt://broker/sensors"
end

# Start commands (optional)
# start remote-control
# start gesture-control
