# PC Camera Examples for UnitAPI

This directory contains examples for controlling a camera (webcam) on a PC using UnitAPI. These examples demonstrate how to capture images, record videos, and control the camera remotely.

## Files

- `camera_client.py`: Client that demonstrates local camera capture
- `camera_frame_client.py`: Client that demonstrates capturing individual frames from the camera
- `camera_server.py`: Server that exposes camera functionality through UnitAPI
- `remote_camera_client.py`: Client that connects to a remote camera server
- `remote_camera_frame_client.py`: Client that captures frames from a remote camera
- `screenshot_client.py`: Client that demonstrates taking screenshots

## Prerequisites

- Python 3.7 or higher
- UnitAPI installed (`pip install unitapi`)
- OpenCV installed (`pip install opencv-python`)
- NumPy installed (`pip install numpy`)

## Local Camera Control

The camera client examples demonstrate how to use the camera device locally to capture images and record videos.

### Running the Local Clients

```bash
# Capture images from the camera
python examples/pc/camera/camera_client.py

# Capture frames from the camera
python examples/pc/camera/camera_frame_client.py

# Take screenshots
python examples/pc/camera/screenshot_client.py
```

These examples demonstrate:
- Creating a camera device
- Capturing images with different resolutions and formats
- Applying image effects
- Capturing video frames
- Taking screenshots of the desktop

## Remote Camera Control

The camera server and remote client examples demonstrate how to control a camera remotely using UnitAPI.

### Running the Server

```bash
# Run on the PC with the camera you want to access remotely
python examples/pc/camera/camera_server.py --host 0.0.0.0 --port 7890
```

Options:
- `--host`: Server host address (default: 0.0.0.0)
- `--port`: Server port (default: 7890)
- `--debug`: Enable debug logging

### Running the Remote Clients

```bash
# Capture images from a remote camera
python examples/pc/camera/remote_camera_client.py --host 192.168.1.100 --port 7890

# Capture frames from a remote camera
python examples/pc/camera/remote_camera_frame_client.py --host 192.168.1.100 --port 7890
```

Options:
- `--host`: UnitAPI server host (default: localhost)
- `--port`: UnitAPI server port (default: 7890)
- `--debug`: Enable debug logging
- `--width`: Image width (default: 1280)
- `--height`: Image height (default: 720)
- `--format`: Image format (default: jpeg)
- `--quality`: Image quality (default: 90)
- `--effect`: Image effect to apply (e.g., grayscale, negative, sketch)

## Supported Camera Operations

The camera examples support the following operations:

- **Capture Image**: Capture a single image from the camera
- **Capture Frame**: Capture a video frame from the camera
- **Record Video**: Record video from the camera
- **Take Screenshot**: Capture the current screen contents
- **Apply Effects**: Apply visual effects to captured images

## Integration with Other Applications

The camera functionality can be integrated with other applications:

- Computer vision applications
- Video conferencing
- Security monitoring
- Automated testing with visual verification
- Image processing pipelines

## Security Considerations

Remote camera control provides powerful capabilities but also introduces security risks. Consider the following:

- Run the server on a secure, private network
- Use UnitAPI's authentication and encryption features
- Be cautious about allowing remote camera control in sensitive environments
- Consider implementing additional access controls based on your specific requirements

## Troubleshooting

1. **Camera Access Issues**: Ensure the camera is not being used by another application
2. **Permission Issues**: Some systems may require additional permissions for camera access
3. **Performance Issues**: Adjust resolution and frame rate for better performance
4. **Format Compatibility**: Ensure the image format is supported by your system

## Example Use Cases

1. **Remote Monitoring**: Monitor a location using a remote camera
2. **Computer Vision**: Develop computer vision applications with remote camera input
3. **Automated Testing**: Capture screenshots for visual regression testing
4. **Video Recording**: Record video for documentation or tutorials
5. **Security**: Create a simple security camera system
