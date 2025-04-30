# PC Microphone Examples for UnitAPI

This directory contains examples for controlling a microphone on a PC using UnitAPI. These examples demonstrate how to record audio, measure audio levels, and control the microphone remotely.

## Files

- `microphone_recording_client.py`: Client that demonstrates local microphone recording
- `microphone_input_client.py`: Client that demonstrates capturing audio input from the microphone
- `microphone_server.py`: Server that exposes microphone functionality through UnitAPI for remote control

## Prerequisites

- Python 3.7 or higher
- UnitAPI installed (`pip install unitapi`)
- PyAudio installed (`pip install pyaudio`)
- NumPy installed (`pip install numpy`)
- FFmpeg (optional, for non-WAV audio formats)

## Local Microphone Control

The microphone client examples demonstrate how to use the microphone device locally to record audio and capture audio input.

### Running the Local Clients

```bash
# Record audio from the microphone
python examples/pc/microphone/microphone_recording_client.py

# Capture audio input from the microphone
python examples/pc/microphone/microphone_input_client.py
```

These examples demonstrate:
- Creating a microphone device
- Recording audio with different sample rates and formats
- Measuring audio input levels
- Processing audio data in real-time

## Remote Microphone Control

The microphone server allows remote clients to control the microphone on a PC using UnitAPI.

### Running the Server

```bash
# Run on the PC with the microphone you want to access remotely
python examples/pc/microphone/microphone_server.py --host 0.0.0.0 --port 7890
```

Options:
- `--host`: Server host address (default: 0.0.0.0)
- `--port`: Server port (default: 7890)
- `--debug`: Enable debug logging

### Connecting to the Server

You can connect to the microphone server using the UnitAPI client:

```python
from unitapi.core.client import UnitAPIClient

async def control_remote_microphone():
    # Connect to the server
    client = UnitAPIClient(server_host="192.168.1.100", server_port=7890)
    
    # List available devices
    devices = await client.list_devices()
    
    # Find the microphone device
    mic_devices = [d for d in devices if d.get('type') == 'microphone']
    if not mic_devices:
        print("No microphone devices found")
        return
    
    mic_device = mic_devices[0]
    device_id = mic_device.get('device_id')
    
    # Start recording
    result = await client.execute_command(
        device_id=device_id,
        command="start_recording",
        params={
            "sample_rate": 44100,
            "channels": 1,
            "format": "wav",
            "output_file": "remote_recording.wav",
            "duration": 10  # Record for 10 seconds
        }
    )
    
    recording_id = result.get('recording_id')
    
    # Get audio level
    level_result = await client.execute_command(
        device_id=device_id,
        command="get_audio_level",
        params={}
    )
    
    print(f"Audio level: {level_result.get('level')}")
    
    # Wait for recording to complete
    await asyncio.sleep(10)
    
    # Stop recording manually if no duration was specified
    # await client.execute_command(
    #     device_id=device_id,
    #     command="stop_recording",
    #     params={"recording_id": recording_id}
    # )
```

## Supported Microphone Operations

The microphone examples support the following operations:

- **Start Recording**: Start recording audio from the microphone
- **Stop Recording**: Stop an active recording
- **Get Audio Level**: Measure the current audio input level
- **Process Audio**: Process audio data in real-time

## Audio Format Support

The examples support various audio formats:

- **WAV**: Uncompressed audio (default)
- **MP3**: Compressed audio (requires FFmpeg)
- Other formats supported by FFmpeg

## Integration with Other Applications

The microphone functionality can be integrated with other applications:

- Speech recognition systems
- Audio processing pipelines
- Voice assistants
- Audio visualization tools
- Sound detection and monitoring

## Security Considerations

Remote microphone control provides powerful capabilities but also introduces security risks. Consider the following:

- Run the server on a secure, private network
- Use UnitAPI's authentication and encryption features
- Be cautious about allowing remote microphone control in sensitive environments
- Consider implementing additional access controls based on your specific requirements

## Troubleshooting

1. **Microphone Access Issues**: Ensure the microphone is not being used by another application
2. **Permission Issues**: Some systems may require additional permissions for microphone access
3. **PyAudio Installation**: On some systems, PyAudio may require additional dependencies
4. **FFmpeg Missing**: For non-WAV formats, ensure FFmpeg is installed and available in the system path

## Example Use Cases

1. **Voice Recording**: Record voice for documentation or dictation
2. **Audio Monitoring**: Monitor audio levels in an environment
3. **Speech Recognition**: Capture audio for speech-to-text processing
4. **Sound Detection**: Detect specific sounds or noise levels
5. **Remote Conferencing**: Implement remote audio capture for conferencing applications
