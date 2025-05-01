# Speaker Playback Fix

## Issue

The UnitAPI speaker playback examples were encountering several issues:

1. `speaker_playback.py` was failing with "No speakers found" even when the device discovery service was running.
2. `speaker_audio_playback.py` was encountering ALSA and JACK errors when trying to use the default audio device.

## Root Causes

1. **WebSocket Communication Issue**: The `UnitAPIClient` in `src/unitapi/core/client.py` was not actually connecting to the WebSocket server. Instead, it was returning mock responses for testing purposes.

2. **Default Audio Device Selection**: The `speaker_audio_playback.py` script was trying to use `get_default_output_device_info()` which might not be available on all systems or might return an invalid device index.

## Solutions

### 1. Fixed Client Implementation

A new client implementation (`client_fixed.py`) was created that properly connects to the WebSocket server using the websockets library. This allows the client to communicate with the device discovery service.

```python
async def send_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send a command to the server using WebSockets.
    """
    try:
        async with websockets.connect(self.ws_url) as websocket:
            # Convert command to JSON
            command_json = json.dumps(command)
            
            # Send command
            await websocket.send(command_json)
            
            # Wait for response
            response_json = await websocket.recv()
            
            # Parse response
            response = json.loads(response_json)
            return response
    except Exception as e:
        self.logger.error(f"WebSocket communication error: {e}")
        return {"status": "error", "message": f"Communication error: {str(e)}"}
```

### 2. Improved Audio Device Selection

The audio playback scripts were modified to use a more robust method for selecting the default audio device:

```python
# Find the first available output device instead of using get_default_output_device_info()
info = p.get_host_api_info_by_index(0)
num_devices = info.get('deviceCount')

# Find output devices
output_devices = []
for i in range(num_devices):
    device_info = p.get_device_info_by_index(i)
    if device_info.get('maxOutputChannels') > 0:
        output_devices.append((i, device_info.get('name')))

if not output_devices:
    self.logger.error("No output devices found")
    p.terminate()
    return False

# Use the first output device
device_index = output_devices[0][0]
self.logger.info(f"Using default output device (index: {device_index})")
```

## Fixed Scripts

1. `src/unitapi/core/client_fixed.py` - A fixed version of the UnitAPI client with proper WebSocket support.
2. `examples/speaker_playback_fixed.py` - A fixed version of the speaker playback example.
3. `examples/speaker_audio_playback_fixed.py` - A fixed version of the speaker audio playback example.

## Usage

### Running the Device Discovery Service

Before using the speaker examples, you need to start the device discovery service:

```bash
python examples/device_discovery.py --debug
```

### Using the Fixed Speaker Playback Example

```bash
# Using the WebSocket client (requires device discovery service)
python examples/speaker_playback_fixed.py --debug

# Using local playback (doesn't require device discovery service)
python examples/speaker_playback_fixed.py --local --debug

# Specifying a specific device index
python examples/speaker_playback_fixed.py --local --device-index 0 --debug
```

### Using the Fixed Speaker Audio Playback Example

```bash
# Play a tone on the default device
python examples/speaker_audio_playback_fixed.py --debug

# Specifying a specific device index
python examples/speaker_audio_playback_fixed.py --device 0 --debug

# List available speakers
python examples/speaker_audio_playback_fixed.py --list --debug

# Play on all available speakers
python examples/speaker_audio_playback_fixed.py --all-devices --debug
```

## Notes

- The ALSA warnings about "Unknown PCM cards" and the JACK errors are not critical and don't affect the functionality of the scripts.
- If you're still having issues with the WebSocket connection, make sure the device discovery service is running and check if the WebSocket server is listening on the expected port (7891 by default).
- The local playback option (`--local` for `speaker_playback_fixed.py` or direct device specification for `speaker_audio_playback_fixed.py`) works independently of the device discovery service.
