# UnitAPI Starlark Configuration

# Set version
VERSION = "1.0"

# Define extensions
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
        "sensitivity": 1.5
    }
)

# Define devices
pc_main = device(
    id = "pc-main",
    type = "computer",
    capabilities = ["keyboard", "mouse", "display"]
)

rpi_remote = device(
    id = "rpi-remote",
    type = "raspberry_pi",
    capabilities = ["gpio", "camera"]
)

# Define pipelines
remote_control = pipeline(
    name = "remote-control",
    source = pc_main.id,  # Reference device ID
    target = rpi_remote.id,
    steps = [
        step("capture", device="keyboard"),
        step("filter", keys=["ctrl", "alt", "f1-f12"]),
        step("forward", destination="tcp://192.168.1.100:5000")
    ]
)

# You can use variables and functions
def create_monitoring_pipeline(device_id, threshold):
    """Create a monitoring pipeline with the given threshold"""
    return pipeline(
        name = f"monitor-{device_id}",
        source = device_id,
        steps = [
            step("read", sensor="temperature"),
            step("filter", threshold=threshold),
            # Conditional step based on threshold
            step("alert", method="email") if threshold > 80 else step("log")
        ]
    )

# Create a monitoring pipeline
temp_monitor = create_monitoring_pipeline("rpi-remote", 75)
