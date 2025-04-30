# Raspberry Pi Speaker Examples for UnitAPI

This directory contains examples for controlling a speaker on a Raspberry Pi using UnitAPI. These examples demonstrate how to set up a speaker server on the Raspberry Pi and control it remotely from a client application.

## Files

- `speaker_server.py`: Server that runs on the Raspberry Pi and exposes speaker functionality through UnitAPI
- `speaker_client.py`: Client that connects to the server and controls audio playback and volume

## Prerequisites

- Raspberry Pi (any model)
- Speaker connected via 3.5mm audio jack, HDMI, USB, or audio HAT
- Python 3.7 or higher
- UnitAPI installed (`pip install unitapi`)
- PyAudio installed (`pip install pyaudio`)
- For audio format support: `ffmpeg` installed

## Server Setup

The speaker server runs on the Raspberry Pi and exposes speaker functionality through UnitAPI. It registers a speaker device with the UnitAPI server and handles commands for audio playback and volume control.

### Running the Server

```bash
# Run on the Raspberry Pi
python speaker_server.py --host 0.0.0.0 --port 7890
```

Options:
- `--host`: Server host address (default: 0.0.0.0)
- `--port`: Server port (default: 7890)
- `--debug`: Enable debug logging
- `--device-index`: Audio output device index (default: system default)

## Client Usage

The speaker client connects to the server and controls the speaker remotely. It provides methods for playing audio files, generating and playing tones, and controlling system volume.

### Running the Client

```bash
# Connect to a local server
python speaker_client.py --demo file --audio-file sample.wav

# Connect to a remote Raspberry Pi
python speaker_client.py --host 192.168.1.100 --port 7890 --demo tone
```

Options:
- `--host`: UnitAPI server host (default: localhost)
- `--port`: UnitAPI server port (default: 7890)
- `--debug`: Enable debug logging
- `--demo`: Demo to run (choices: file, tone, volume, all)
- `--audio-file`: Audio file to play (for file demo)
- `--frequency`: Tone frequency in Hz (default: 440)
- `--duration`: Tone or volume change duration in seconds (default: 3.0)
- `--volume`: Volume level (0.0-1.0) (default: 0.5)

## Demo Modes

The client provides several demo modes:

1. **File Demo** (`--demo file`): Plays an audio file
2. **Tone Demo** (`--demo tone`): Generates and plays a tone with specified frequency
3. **Volume Demo** (`--demo volume`): Demonstrates volume control
4. **All Demos** (`--demo all`): Runs all demos in sequence

## Supported Speaker Operations

The speaker examples support the following operations:

- **Play Audio File**: Play audio files in various formats (WAV, MP3, etc.)
- **Play Tone**: Generate and play a tone with specified frequency and duration
- **Set Volume**: Control the system volume
- **Stop Playback**: Stop the current audio playback
- **Get Playback Status**: Get the current playback status

## Audio Formats

The speaker examples support the following audio formats:

- **WAV**: Uncompressed audio format
- **MP3**: Compressed audio format
- **OGG**: Compressed audio format
- **FLAC**: Lossless compressed audio format
- Other formats supported by ffmpeg

## Troubleshooting

1. **Speaker Not Detected**: Ensure the speaker is properly connected and recognized by the system:
   ```bash
   # List audio output devices
   aplay -l
   ```

2. **No Sound**: Check if the volume is muted or too low:
   ```bash
   # Check and adjust volume
   amixer sset 'Master' 80%
   ```

3. **Permission Issues**: Some systems may require additional permissions for audio access:
   ```bash
   # Add user to audio group
   sudo usermod -a -G audio $USER
   ```

4. **PyAudio Installation Issues**: If you have trouble installing PyAudio, try:
   ```bash
   # Install dependencies
   sudo apt-get install portaudio19-dev python3-pyaudio
   
   # Then install PyAudio
   pip install pyaudio
   ```

5. **Audio Quality Issues**: If you experience poor audio quality, try using a different audio output device or format.

6. **Connection Issues**: Ensure the server is running and accessible from the client's network.

## Example Use Cases

1. **Remote Audio Player**: Control audio playback on a Raspberry Pi from another device
2. **Notification System**: Play alert sounds or notifications remotely
3. **Multi-Room Audio**: Create a distributed audio system with multiple Raspberry Pis
4. **Text-to-Speech Output**: Combine with a text-to-speech service to create voice announcements
5. **Interactive Projects**: Add audio feedback to interactive projects
