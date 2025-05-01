# UnitAPI HCL Configuration for GPIO Devices

version = "1.0"

extension "gpio" {
  version = ">=1.0.0"
  config {
    pin_numbering = "BCM"  # Broadcom numbering scheme
    safety_checks = true
  }
}

extension "sensors" {
  version = ">=1.0.0"
  config {
    polling_interval = 1000  # ms
    auto_calibration = true
  }
}

extension "actuators" {
  version = ">=1.0.0"
  config {
    pwm_frequency = 1000  # Hz
    default_duty_cycle = 0.0
  }
}

device "rpi-gpio" {
  type = "raspberry_pi_gpio"
  capabilities = ["digital_io", "pwm", "i2c", "spi"]
  metadata = {
    board_model = "Raspberry Pi 4B"
    total_pins = 40
  }
}

device "arduino-gpio" {
  type = "arduino_gpio"
  capabilities = ["digital_io", "analog_input", "pwm"]
  metadata = {
    board_model = "Arduino Uno"
    connection = "serial:///dev/ttyACM0"
    baud_rate = 115200
  }
}

device "esp32-gpio" {
  type = "esp32_gpio"
  capabilities = ["digital_io", "analog_input", "pwm", "touch", "wifi"]
  metadata = {
    board_model = "ESP32 DevKit"
    connection = "wifi://192.168.1.120:8080"
  }
}

pipeline "led-control" {
  source = "rpi-gpio"
  
  step "configure" {
    pins = [17, 18, 27]
    mode = "output"
  }
  
  step "set_state" {
    pin_17 = "high"
    pin_18 = "pwm"
    pin_27 = "low"
  }
  
  step "pwm_control" {
    pin = 18
    duty_cycle = 0.5
    frequency = 1000
  }
}

pipeline "button-monitor" {
  source = "rpi-gpio"
  
  step "configure" {
    pins = [22, 23]
    mode = "input"
    pull = "up"
  }
  
  step "read" {
    pins = [22, 23]
    debounce = true
    interval = 50  # ms
  }
  
  step "on_change" {
    pin_22 = {
      on_press = "toggle_led"
      on_hold = "brightness_up"
    }
    pin_23 = {
      on_press = "next_mode"
      on_hold = "brightness_down"
    }
  }
}

pipeline "sensor-reading" {
  source = "arduino-gpio"
  
  step "configure" {
    analog_pins = ["A0", "A1"]
    digital_pins = [2, 3]
    modes = {
      "A0" = "analog_input"
      "A1" = "analog_input"
      "2" = "input_pullup"
      "3" = "input"
    }
  }
  
  step "read" {
    pins = ["A0", "A1", 2, 3]
    interval = 500  # ms
  }
  
  step "process" {
    mapping = {
      "A0" = "temperature"
      "A1" = "light_level"
    }
    calibration = {
      "temperature" = "celsius = (reading * 0.48876) - 50"
      "light_level" = "percent = (reading / 1023) * 100"
    }
  }
  
  step "trigger" {
    conditions = {
      "temperature > 30" = "activate_fan"
      "light_level < 20" = "activate_light"
    }
  }
}

pipeline "multi-device-control" {
  source = "rpi-gpio"
  target = "esp32-gpio"
  
  step "read" {
    source_pins = [4, 5, 6]
    interval = 100  # ms
  }
  
  step "process" {
    mapping = {
      "4" = "relay_1"
      "5" = "relay_2"
      "6" = "relay_3"
    }
  }
  
  step "forward" {
    destination = "tcp://192.168.1.120:8080/gpio"
    protocol = "json"
  }
  
  step "set_remote" {
    target_pins = {
      "relay_1" = 12
      "relay_2" = 14
      "relay_3" = 27
    }
    mode = "output"
  }
}

# Home automation pipeline
pipeline "home-automation" {
  source = "rpi-gpio"
  
  step "configure" {
    inputs = [
      { pin = 17, name = "motion_sensor", pull = "up" },
      { pin = 18, name = "door_sensor", pull = "up" },
      { pin = 22, name = "light_switch", pull = "up" }
    ]
    outputs = [
      { pin = 23, name = "light_relay" },
      { pin = 24, name = "fan_relay" },
      { pin = 25, name = "alarm_buzzer", pwm = true }
    ]
  }
  
  step "monitor" {
    sensors = ["motion_sensor", "door_sensor", "light_switch"]
    interval = 100  # ms
    debounce = true
  }
  
  step "automation" {
    rules = [
      {
        condition = "motion_sensor == LOW && time_between('18:00', '07:00')"
        actions = [
          { target = "light_relay", value = "HIGH", duration = 300 }  # 5 minutes
        ]
      },
      {
        condition = "door_sensor == LOW && security_mode == 'armed'"
        actions = [
          { target = "alarm_buzzer", value = "PWM", duty_cycle = 0.7, frequency = 2000 },
          { target = "notification", value = "Door opened while armed!" }
        ]
      },
      {
        condition = "light_switch == LOW"
        actions = [
          { target = "light_relay", value = "TOGGLE" }
        ]
      }
    ]
  }
}
