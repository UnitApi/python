# Raspberry Pi Microphone Examples for UnitAPI

This directory contains examples for controlling a microphone on a Raspberry Pi using UnitAPI. These examples demonstrate how to set up a microphone server on the Raspberry Pi and control it remotely from a client application.

## Files

- `microphone_server.py`: Server that runs on the Raspberry Pi and exposes microphone functionality through UnitAPI
- `microphone_client.py`: Client that connects to the server and records audio and monitors levels

## Prerequisites

- Raspberry Pi (any model)
- USB microphone or audio HAT
- Python 3.7 or higher
- UnitAPI installed (`pip install unitapi`)
- PyAudio installed (`pip install pyaudio`)
- For audio format conversion: `ffmpeg` installed

## Server Setup

The microphone server runs on the Raspberry Pi and exposes microphone functionality through UnitAPI. It registers a microphone device with the UnitAPI server and handles commands for audio recording and level monitoring.

### Running the Server

```bash
# Run on the Raspberry Pi
python microphone_server.py --host 0.0.0.0 --port 7890
```

Options:
- `--host`: Server host address (default: 0.0.0.0)
- `--port`: Server port (default: 7890)
- `--debug`: Enable debug logging

## Client Usage

The microphone client connects to the server and controls the microphone remotely. It provides methods for recording audio and monitoring audio levels.

### Running the Client

```bash
# Connect to a local server
python microphone_client.py --demo record --duration 10

# Connect to a remote Raspberry Pi
python microphone_client.py --host 192.168.1.100 --port 7890 --demo monitor
```

Options:
- `--host`: UnitAPI server host (default: localhost)
- `--port`: UnitAPI server port (default: 7890)
- `--debug`: Enable debug logging
- `--demo`: Demo to run (choices: record, monitor, vad)
- `--duration`: Recording/monitoring duration in seconds (default: 5.0)
- `--sample-rate`: Audio sample rate in Hz (default: 44100)
- `--channels`: Number of audio channels (default: 1)
- `--format`: Audio format (choices: wav, mp3) (default: wav)
- `--output`: Output file path
- `--threshold`: Voice activity detection threshold (default: 0.1)

## Demo Modes

The client provides several demo modes:

1. **Record Demo** (`--demo record`): Records audio for a specified duration and saves it to a file
2. **Monitor Demo** (`--demo monitor`): Monitors audio levels in real-time and displays a level meter
3. **Voice Activity Detection Demo** (`--demo vad`): Detects voice activity based on audio levels

## Supported Microphone Operations

The microphone examples support the following operations:

- **Start Recording**: Begin recording audio with specified parameters
- **Stop Recording**: Stop recording and save the audio file
- **Get Audio Level**: Get the current audio input level
- **Voice Activity Detection**: Detect when someone is speaking

## Audio Formats

The microphone examples support the following audio formats:

- **WAV**: Uncompressed audio format (default)
- **MP3**: Compressed audio format (requires ffmpeg)

## Troubleshooting

1. **Microphone Not Detected**: Ensure the microphone is properly connected and recognized by the system:
   ```bash
   # List audio input devices
   arecord -l
   ```

2. **Permission Issues**: Some systems may require additional permissions for audio access:
   ```bash
   # Add user to audio group
   sudo usermod -a -G audio $USER
   ```

3. **PyAudio Installation Issues**: If you have trouble installing PyAudio, try:
   ```bash
   # Install dependencies
   sudo apt-get install portaudio19-dev python3-pyaudio
   
   # Then install PyAudio
   pip install pyaudio
   ```

4. **Audio Quality Issues**: If you experience poor audio quality, try adjusting the sample rate or using a different microphone.

5. **Connection Issues**: Ensure the server is running and accessible from the client's network.

## Example Use Cases

1. **Voice Assistant**: Create a voice-controlled assistant using the microphone for input
2. **Audio Monitoring**: Monitor sound levels in a room or environment
3. **Voice Recording**: Record voice memos or audio notes remotely
4. **Sound Detection**: Create a system that responds to specific sounds or noise levels
5. **Voice Activity Detection**: Trigger actions when voice activity is detected
