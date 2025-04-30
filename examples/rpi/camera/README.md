# Raspberry Pi Camera Examples for UnitAPI

This directory contains examples for controlling a camera on a Raspberry Pi using UnitAPI. These examples demonstrate how to set up a camera server on the Raspberry Pi and control it remotely from a client application.

## Files

- `camera_server.py`: Server that runs on the Raspberry Pi and exposes camera functionality through UnitAPI
- `camera_client.py`: Client that connects to the server and captures images and videos

## Prerequisites

- Raspberry Pi (any model with camera support)
- Raspberry Pi Camera Module (any version) or USB webcam
- Python 3.7 or higher
- UnitAPI installed (`pip install unitapi`)
- For Raspberry Pi Camera Module: `picamera` package
- For USB webcam: `opencv-python` package

## Server Setup

The camera server runs on the Raspberry Pi and exposes camera functionality through UnitAPI. It registers a camera device with the UnitAPI server and handles commands for image capture and video recording.

### Running the Server

```bash
# Run on the Raspberry Pi
python camera_server.py --host 0.0.0.0 --port 7890
```

Options:
- `--host`: Server host address (default: 0.0.0.0)
- `--port`: Server port (default: 7890)
- `--debug`: Enable debug logging
- `--resolution`: Camera resolution (default: 640x480)
- `--framerate`: Camera framerate (default: 30)

## Client Usage

The camera client connects to the server and controls the camera remotely. It provides methods for capturing images, recording videos, and applying image effects.

### Running the Client

```bash
# Connect to a local server
python camera_client.py --demo image

# Connect to a remote Raspberry Pi
python camera_client.py --host 192.168.1.100 --port 7890 --demo video
```

Options:
- `--host`: UnitAPI server host (default: localhost)
- `--port`: UnitAPI server port (default: 7890)
- `--debug`: Enable debug logging
- `--demo`: Demo to run (choices: image, video, timelapse)
- `--resolution`: Image resolution (e.g., 1920x1080)
- `--output`: Output file path
- `--duration`: Recording duration in seconds (for video demo)
- `--interval`: Interval between captures in seconds (for timelapse demo)

## Supported Camera Operations

The camera examples support the following operations:

- **Capture Image**: Take a still image with the camera
- **Record Video**: Record a video for a specified duration
- **Create Timelapse**: Capture a series of images at specified intervals
- **Apply Image Effects**: Apply various effects to the camera output (grayscale, negative, etc.)
- **Adjust Camera Settings**: Change resolution, framerate, brightness, contrast, etc.

## Integration with Other Applications

The camera functionality can be integrated with other applications running on the Raspberry Pi. For example:

- Security monitoring systems
- Computer vision applications
- Motion detection
- Timelapse photography
- Video streaming

## Troubleshooting

1. **Camera Not Detected**: Ensure the camera module is properly connected and enabled in raspi-config:
   ```bash
   sudo raspi-config
   ```
   Then navigate to "Interfacing Options" > "Camera" and enable it.

2. **Permission Issues**: Some systems may require additional permissions for camera access
   ```bash
   # Add user to video group
   sudo usermod -a -G video $USER
   ```

3. **Connection Issues**: Ensure the server is running and accessible from the client's network

4. **Performance Issues**: Lower the resolution or framerate if experiencing lag or high CPU usage

## Example Use Cases

1. **Security Camera**: Set up a remote security camera with motion detection
2. **Timelapse Photography**: Create timelapse videos of plants growing, construction projects, etc.
3. **Computer Vision**: Use the camera for object detection, face recognition, or other computer vision tasks
4. **Remote Monitoring**: Monitor a location remotely using the camera
