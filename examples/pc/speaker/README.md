# PC Speaker Examples for UnitAPI

This directory contains examples for controlling speakers on a PC using UnitAPI. These examples demonstrate how to play audio files, generate sounds, and control speakers remotely.

## Files

- `speaker_client.py`: Client that demonstrates basic speaker control
- `speaker_playback.py`: Client that demonstrates playing audio files
- `speaker_audio_playback.py`: Client that demonstrates advanced audio playback features
- `speaker_playback_fixed.py`: Fixed version of the playback example with improved error handling
- `speaker_audio_playback_fixed.py`: Fixed version of the audio playback example with improved error handling
- `speaker_server.py`: Server that exposes speaker functionality through UnitAPI for remote control

## Prerequisites

- Python 3.7 or higher
- UnitAPI installed (`pip install unitapi`)
- PyAudio installed (`pip install pyaudio`)
- NumPy installed (`pip install numpy`)

## Local Speaker Control

The speaker client examples demonstrate how to use the speaker device locally to play audio files and generate sounds.

### Running the Local Clients

```bash
# Basic speaker control
python examples/pc/speaker/speaker_client.py

# Play audio files
python examples/pc/speaker/speaker_playback.py --file path/to/audio.wav

# Advanced audio playback
python examples/pc/speaker/speaker_audio_playback.py --file path/to/audio.wav

# Fixed versions with improved error handling
python examples/pc/speaker/speaker_playback_fixed.py --file path/to/audio.wav
python examples/pc/speaker/speaker_audio_playback_fixed.py --file path/to/audio.wav
```

These examples demonstrate:
- Creating a speaker device
- Playing audio files in various formats
- Controlling volume and playback speed
- Generating tones and sounds
- Error handling and resource management

## Remote Speaker Control

The speaker server allows remote clients to control the speakers on a PC using UnitAPI.

### Running the Server

```bash
# Run on the PC with the speakers you want to access remotely
python examples/pc/speaker/speaker_server.py --host 0.0.0.0 --port 7890
```

Options:
- `--host`: Server host address (default: 0.0.0.0)
- `--port`: Server port (default: 7890)
- `--debug`: Enable debug logging

### Connecting to the Server

You can connect to the speaker server using the UnitAPI client:

```python
from unitapi.core.client import UnitAPIClient

async def control_remote_speaker():
    # Connect to the server
    client = UnitAPIClient(server_host="192.168.1.100", server_port=7890)
    
    # List available devices
    devices = await client.list_devices()
    
    # Find the speaker device
    speaker_devices = [d for d in devices if d.get('type') == 'speaker']
    if not speaker_devices:
        print("No speaker devices found")
        return
    
    speaker_device = speaker_devices[0]
    device_id = speaker_device.get('device_id')
    
    # Play audio file
    await client.execute_command(
        device_id=device_id,
        command="play_audio",
        params={
            "file_path": "path/to/audio.wav",
            "volume": 0.8
        }
    )
    
    # Generate a tone
    await client.execute_command(
        device_id=device_id,
        command="play_tone",
        params={
            "frequency": 440,  # A4 note
            "duration": 1.0,   # 1 second
            "volume": 0.5
        }
    )
```

## Supported Audio Formats

The examples support various audio formats:

- **WAV**: Uncompressed audio (default)
- **MP3**: Compressed audio (requires additional libraries)
- **OGG**: Compressed audio (requires additional libraries)
- Other formats supported by the system's audio libraries

## Integration with Other Applications

The speaker functionality can be integrated with other applications:

- Text-to-speech systems
- Music players
- Notification systems
- Audio visualization tools
- Interactive applications and games

## Troubleshooting

1. **Audio Device Issues**: Ensure the audio device is properly configured and not in use by another application
2. **Format Support**: Some audio formats may require additional libraries
3. **PyAudio Installation**: On some systems, PyAudio may require additional dependencies
4. **Volume Control**: If no sound is heard, check system volume and application volume settings

## Example Use Cases

1. **Audio Playback**: Play music or sound effects in applications
2. **Text-to-Speech**: Convert text to speech for accessibility
3. **Notifications**: Play alert sounds for system events
4. **Remote Control**: Control audio playback on a remote system
5. **Sound Generation**: Generate tones and sounds for testing or musical applications
