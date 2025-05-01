# UnitAPI HCL Configuration

version = "1.0"

extension "keyboard" {
  version = ">=1.0.0"
  config {
    layout = "us"
  }
}

extension "mouse" {
  version = ">=1.0.0"
  config {
    sensitivity = 1.5
  }
}

device "pc-main" {
  type = "computer"
  capabilities = ["keyboard", "mouse", "display"]
}

device "rpi-remote" {
  type = "raspberry_pi"
  capabilities = ["gpio", "camera"]
}

pipeline "remote-control" {
  source = "pc-main"
  target = "rpi-remote"
  
  step "capture" {
    device = "keyboard"
  }
  
  step "filter" {
    keys = ["ctrl", "alt", "f1-f12"]
  }
  
  step "forward" {
    destination = "tcp://192.168.1.100:5000"
  }
}
