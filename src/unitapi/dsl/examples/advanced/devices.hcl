# Device configuration in HCL format
# This file defines additional devices that will be merged with the base configuration

# Raspberry Pi device
device "rpi-sensor" {
  type = "raspberry_pi"
  capabilities = ["gpio", "camera", "sensors"]
}

# Arduino device for sensor readings
device "arduino-temp" {
  type = "arduino"
  capabilities = ["gpio", "sensors"]
}

# ESP32 device for IoT control
device "esp32-control" {
  type = "esp32"
  capabilities = ["gpio", "wifi"]
}

# Smartphone device for remote control
device "mobile-control" {
  type = "smartphone"
  capabilities = ["display", "camera", "touchscreen"]
}

# Additional computer for monitoring
device "pc-monitor" {
  type = "computer"
  capabilities = ["display", "keyboard", "mouse"]
}
