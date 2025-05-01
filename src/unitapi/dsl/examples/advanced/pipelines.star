# Pipeline configuration in Starlark format
# This file dynamically generates pipelines based on available devices

# Set version
VERSION = "1.0"

# Environment configuration
ENVIRONMENT = "development"  # Can be "development", "testing", or "production"
DEBUG = True if ENVIRONMENT == "development" else False

# Helper functions
def create_monitoring_pipeline(source_device, target_device, sensor_type, threshold):
    """Create a monitoring pipeline for a specific sensor type"""
    pipeline_name = f"monitor-{source_device}-{sensor_type}"
    
    # Define steps based on sensor type
    if sensor_type == "temperature":
        steps = [
            step("read", sensor=sensor_type, pins=["A0"]),
            step("filter", threshold=threshold),
            # Use different alert methods based on threshold severity
            step("alert", method="email") if threshold > 80 else step("log"),
            step("forward", destination=f"tcp://{target_device}:5000")
        ]
    elif sensor_type == "motion":
        steps = [
            step("read", sensor=sensor_type),
            step("detect", sensitivity=0.8),
            step("capture", device="camera") if threshold > 0.5 else step("log"),
            step("forward", destination=f"tcp://{target_device}:5000")
        ]
    elif sensor_type == "light":
        steps = [
            step("read", sensor=sensor_type, pins=["A1"]),
            step("transform", mode="analog_to_digital"),
            step("forward", destination=f"tcp://{target_device}:5000")
        ]
    else:
        # Generic sensor pipeline
        steps = [
            step("read", sensor=sensor_type),
            step("log"),
            step("forward", destination=f"tcp://{target_device}:5000")
        ]
    
    # Create and return the pipeline
    return pipeline(
        name=pipeline_name,
        source=source_device,
        target=target_device,
        steps=steps
    )

def create_control_pipeline(source_device, target_device, control_type):
    """Create a control pipeline for a specific control type"""
    pipeline_name = f"control-{source_device}-{target_device}-{control_type}"
    
    # Define steps based on control type
    if control_type == "keyboard":
        steps = [
            step("capture", device="keyboard"),
            step("filter", keys=["ctrl", "alt", "f1-f12"]),
            step("forward", destination=f"tcp://{target_device}:5000")
        ]
    elif control_type == "mouse":
        steps = [
            step("capture", device="mouse"),
            step("detect", gestures=True),
            step("forward", destination=f"tcp://{target_device}:5000")
        ]
    elif control_type == "gpio":
        steps = [
            step("read", pins=["GPIO17", "GPIO18", "GPIO27"]),
            step("transform", mode="digital"),
            step("forward", destination=f"tcp://{target_device}:5000")
        ]
    else:
        # Generic control pipeline
        steps = [
            step("capture", device=control_type),
            step("forward", destination=f"tcp://{target_device}:5000")
        ]
    
    # Create and return the pipeline
    return pipeline(
        name=pipeline_name,
        source=source_device,
        target=target_device,
        steps=steps
    )

# Define sensor devices and their thresholds
sensor_devices = {
    "arduino-temp": ["temperature"],
    "rpi-sensor": ["temperature", "motion", "light"],
    "esp32-control": ["humidity"]
}

# Define control devices and their control types
control_devices = {
    "pc-main": ["keyboard", "mouse"],
    "mobile-control": ["touchscreen"],
    "pc-monitor": ["keyboard"]
}

# Define monitoring targets
monitoring_targets = {
    "arduino-temp": "pc-main",
    "rpi-sensor": "pc-monitor",
    "esp32-control": "pc-main"
}

# Define control targets
control_targets = {
    "pc-main": ["rpi-sensor", "esp32-control"],
    "mobile-control": ["rpi-sensor"],
    "pc-monitor": ["arduino-temp"]
}

# Generate monitoring pipelines
monitoring_pipelines = []
for source, sensor_types in sensor_devices.items():
    target = monitoring_targets.get(source, "pc-main")
    for sensor_type in sensor_types:
        # Set different thresholds based on sensor type
        if sensor_type == "temperature":
            threshold = 75 if ENVIRONMENT == "production" else 85
        elif sensor_type == "motion":
            threshold = 0.7
        elif sensor_type == "light":
            threshold = 500
        else:
            threshold = 50
        
        # Create and add the pipeline
        monitoring_pipelines.append(
            create_monitoring_pipeline(source, target, sensor_type, threshold)
        )

# Generate control pipelines
control_pipelines = []
for source, targets in control_targets.items():
    control_types = control_devices.get(source, [])
    for target in targets:
        for control_type in control_types:
            # Create and add the pipeline
            control_pipelines.append(
                create_control_pipeline(source, target, control_type)
            )

# Add a special debug pipeline if in development mode
if DEBUG:
    debug_pipeline = pipeline(
        name="debug-logging",
        source="pc-main",
        steps=[
            step("log", level="debug", format="detailed"),
            step("publish", topic="debug/logs")
        ]
    )
    control_pipelines.append(debug_pipeline)

# Combine all pipelines
all_pipelines = monitoring_pipelines + control_pipelines
