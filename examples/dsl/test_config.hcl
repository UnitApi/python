version = "1.0"

extension "test_extension" {
  version = "1.0.0"
  config {
    enabled = true
    mode = "test"
  }
}

device "test_device" {
  type = "test_type"
  capabilities = ["test1", "test2"]
  metadata = {
    location = "test_location"
    active = true
  }
}

pipeline "test_pipeline" {
  source = "test_device"
  step "test_step" {
    param1 = "value1"
    param2 = 123
    param3 = true
    param4 = ["item1", "item2"]
  }
}
