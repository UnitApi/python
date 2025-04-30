import asyncio
import logging
import numpy as np
from typing import Dict, Any, Optional
from .base import AudioDevice, DeviceStatus

class RemoteSpeakerDevice(AudioDevice):
    """
    Advanced remote speaker device for network audio streaming.
    """
    def __init__(
        self,
        device_id: str,
        name: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize remote speaker device.

        :param device_id: Unique device identifier
        :param name: Human-readable device name
        :param metadata: Additional device information
        """
        super().__init__(
            device_id=device_id,
            name=name,
            device_type='speaker',
            metadata=metadata or {}
        )

        # Audio configuration
        self.sample_rate = metadata.get('sample_rate', 44100)
        self.channels = metadata.get('channels', 2)

        # Logging setup
        self.logger = logging.getLogger(f"RemoteSpeakerDevice_{device_id}")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    async def connect(self) -> bool:
        """
        Connect to the remote speaker device.

        :return: Connection status
        """
        try:
            # Simulated connection logic
            self.status = DeviceStatus.ONLINE
            self.logger.info(f"Remote speaker {self.device_id} connected")
            return True
        except Exception as e:
            self.status = DeviceStatus.ERROR
            self.logger.error(f"Remote speaker connection failed: {e}")
            return False

    async def disconnect(self) -> bool:
        """
        Disconnect from the remote speaker device.

        :return: Disconnection status
        """
        try:
            self.status = DeviceStatus.OFFLINE
            self.logger.info(f"Remote speaker {self.device_id} disconnected")
            return True
        except Exception as e:
            self.logger.error(f"Remote speaker disconnection failed: {e}")
            return False

    async def play_audio(self, audio_data: bytes) -> bool:
        """
        Play audio on the remote speaker.

        :param audio_data: Audio data to play
        :return: Playback status
        """
        try:
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.float32)

            # Simulated audio playback
            self.logger.info(
                f"Playing audio on {self.name}: "
                f"{len(audio_array)} samples, {self.channels} channels"
            )

            return True
        except Exception as e:
            self.logger.error(f"Audio playback failed: {e}")
            return False

    async def execute_command(
        self,
        command: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a command on the remote speaker.

        :param command: Command to execute
        :param params: Command parameters
        :return: Command execution result
        """
        try:
            if command == 'play_audio':
                # Expect base64 encoded audio
                import base64

                if 'base64_data' in params:
                    audio_bytes = base64.b64decode(params['base64_data'])
                elif 'file_path' in params:
                    # Read audio file
                    with open(params['file_path'], 'rb') as f:
                        audio_bytes = f.read()
                else:
                    raise ValueError("No audio data provided")

                # Play audio
                success = await self.play_audio(audio_bytes)

                return {
                    'status': 'success' if success else 'error',
                    'message': 'Audio playback completed' if success else 'Playback failed'
                }

            else:
                raise ValueError(f"Unsupported command: {command}")

        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }

# Utility function for generating test audio
def generate_test_audio(
    duration: float = 3.0,
    frequency: float = 440.0,
    sample_rate: int = 44100
) -> bytes:
    """
    Generate a simple sine wave audio test signal.

    :param duration: Audio duration in seconds
    :param frequency: Sine wave frequency
    :param sample_rate: Audio sample rate
    :return: Generated audio bytes
    """
    t = np.linspace(0, duration, int(sample_rate * duration), False)

    # Generate sine wave
    audio = np.sin(2 * np.pi * frequency * t)

    # Normalize to float32
    audio = audio.astype(np.float32)

    return audio.tobytes()