import asyncio
import base64
import logging
from unitapi.core.server import UnitAPIServer
from unitapi.core.client import UnitAPIClient
from unitapi.devices.base import DeviceStatus
from unitapi.protocols.websocket import WebSocketProtocol

# Import the RemoteSpeakerDevice from the previous example
from remote_speaker_device import RemoteSpeakerDevice, generate_test_audio

class RemoteSpeakerService:
    """
    Comprehensive remote speaker network service.
    """
    def __init__(
        self, 
        server_host: str = 'localhost', 
        server_port: int = 7890,
        ws_host: str = 'localhost',
        ws_port: int = 8765
    ):
        """
        Initialize remote speaker service.
        
        :param server_host: UnitAPI server host
        :param server_port: UnitAPI server port
        :param ws_host: WebSocket server host
        :param ws_port: WebSocket server port
        """
        # UnitAPI server setup
        self.server = UnitAPIServer(host=server_host, port=server_port)
        
        # WebSocket protocol setup
        self.websocket = WebSocketProtocol(host=ws_host, port=ws_port)
        
        # Logging setup
        self.logger = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Speakers registry
        self.speakers: Dict[str, RemoteSpeakerDevice] = {}

    async def register_remote_speaker(
        self, 
        device_id: str, 
        name: str, 
        location: str
    ) -> RemoteSpeakerDevice:
        """
        Register a new remote speaker.
        
        :param device_id: Unique device identifier
        :param name: Speaker name
        :param location: Speaker location
        :return: Registered speaker device
        """
        # Create speaker device
        speaker = RemoteSpeakerDevice(
            device_id=device_id,
            name=name,
            metadata={
                'location': location,
                'sample_rate': 44100,
                'channels': 2
            }
        )
        
        # Connect speaker
        await speaker.connect()
        
        # Register in server
        self.server.register_device(
            device_id=device_id,
            device_type='speaker',
            metadata={
                'name': name,
                'location': location
            }
        )
        
        # Store in registry
        self.speakers[device_id] = speaker
        
        self.logger.info(f"Registered remote speaker: {device_id}")
        return speaker

    async def start_service(self):
        """
        Start the remote speaker service.
        """
        # Start UnitAPI server
        server_task = asyncio.create_task(self.server.start())
        
        # Start WebSocket server
        websocket_task = asyncio.create_task(self.websocket.create_server())
        
        self.logger.info("Remote Speaker Service started")
        
        # Wait for servers to start
        await asyncio.gather(server_task, websocket_task)

    async def play_audio_on_speaker(
        self, 
        device_id: str, 
        audio_data: bytes
    ) -> bool:
        """
        Play audio on a specific remote speaker.
        
        :param device_id: Speaker device ID
        :param audio_data: Audio data to play
        :return: Playback status
        """
        if device_id not in self.speakers:
            self.logger.error(f"Speaker {device_id} not found")
            return False
        
        speaker = self.speakers[device_id]
        return await speaker.play_audio(audio_data)

# User-side client for remote audio control
class RemoteSpeakerClient:
    """
    Client for controlling remote speakers.
    """
    def __init__(
        self, 
        server_host: str = 'localhost', 
        server_port: int = 7890
    ):
        """
        Initialize remote speaker client.
        
        :param server_host: UnitAPI server host
        :param server_port: UnitAPI server port
        """
        self.client = UnitAPIClient(
            server_host=server_host, 
            server_port=server_port
        )
        
        # Logging setup
        self.logger = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def list_remote_speakers(self) -> List[Dict[str, Any]]:
        """
        List available remote speakers.
        
        :return: List of remote speakers
        """
        return self.client.list_devices(device_type='speaker')

    def play_remote_audio(
        self, 
        device_id: str, 
        audio_data: bytes
    ) -> Dict[str, Any]:
        """
        Send audio to be played on a remote speaker.
        
        :param device_id: Target speaker device ID
        :param audio_data: Audio data to play
        :return: Playback command result
        """
        # Encode audio data to base64 for transmission
        base64_audio = base64.b64encode(audio_data).decode()
        
        return self.client.execute_command(
            device_id=device_id,
            command='play_audio',
            params={'base64_data': base64_audio}
        )

# Example usage scenario
async def main():
    """
    Demonstrate remote speaker network usage.
    """
    # Start remote speaker service
    service = RemoteSpeakerService()
    
    # Register a remote speaker
    living_room_speaker = await service.register_remote_speaker(
        device_id='living_room_speaker_01',
        name='Living Room Speaker',
        location='Living Room'
    )
    
    # Start service in background
    service_task = asyncio.create_task(service.start_service())
    
    # Simulate brief delay for service startup
    await asyncio.sleep(2)
    
    try:
        # Create client
        remote_client = RemoteSpeakerClient()
        
        # List available speakers
        speakers = remote_client.list_remote_speakers()
        print("Available Speakers:", speakers)
        
        # Generate test audio
        test_audio = generate_test_audio(
            duration=3.0,   # 3 seconds
            frequency=440.0  # A4 note
        )
        
        # Play audio on remote speaker
        result = remote_client.play_remote_audio(
            device_id='living_room_speaker_01',audio_data=test_audio
        )

        print("Remote Audio Playback Result:", result)

        # Wait to simulate audio playback
        await asyncio.sleep(4)

    finally:
        # Stop service
        service_task.cancel()
        try:
            await service_task
        except asyncio.CancelledError:
            pass

# Speech synthesis example (requires additional library)
async def text_to_speech_example():
    """
    Demonstrate text-to-speech on a remote speaker.
    """
    try:
        import pyttsx3
    except ImportError:
        print("pyttsx3 not installed. Install with: pip install pyttsx3")
        return

    # Initialize TTS engine
    engine = pyttsx3.init()

    # Generate audio from text
    engine.save_to_file("Hello! This is a test of remote audio streaming.", "test_speech.wav")
    engine.runAndWait()

    # Read generated audio file
    with open("test_speech.wav", 'rb') as f:
        speech_audio = f.read()

    # Start remote speaker service
    service = RemoteSpeakerService()

    # Register a remote speaker
    await service.register_remote_speaker(
        device_id='kitchen_speaker_01',
        name='Kitchen Speaker',
        location='Kitchen'
    )

    # Start service in background
    service_task = asyncio.create_task(service.start_service())

    # Simulate brief delay for service startup
    await asyncio.sleep(2)

    try:
        # Create client
        remote_client = RemoteSpeakerClient()

        # Play text-to-speech audio on remote speaker
        result = remote_client.play_remote_audio(
            device_id='kitchen_speaker_01',
            audio_data=speech_audio
        )

        print("Remote Speech Playback Result:", result)

        # Wait to simulate audio playback
        await asyncio.sleep(4)

    finally:
        # Stop service
        service_task.cancel()
        try:
            await service_task
        except asyncio.CancelledError:
            pass

# Multiple speaker streaming example
async def multi_speaker_streaming():
    """
    Demonstrate streaming to multiple remote speakers.
    """
    # Start remote speaker service
    service = RemoteSpeakerService()

    # Register multiple speakers
    speakers = [
        await service.register_remote_speaker(
            device_id=f'speaker_{i}',
            name=f'Room {i} Speaker',
            location=f'Room {i}'
        ) for i in range(1, 4)  # 3 speakers
    ]

    # Start service in background
    service_task = asyncio.create_task(service.start_service())

    # Simulate brief delay for service startup
    await asyncio.sleep(2)

    try:
        # Create client
        remote_client = RemoteSpeakerClient()

        # Generate different audio for each speaker
        def generate_frequency_audio(freq: float, duration: float = 3.0) -> bytes:
            """Generate audio with specific frequency."""
            import numpy as np
            sample_rate = 44100
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            audio = np.sin(2 * np.pi * freq * t)
            audio = audio.astype(np.float32)
            return audio.tobytes()

        # Frequencies for different speakers
        frequencies = [440.0, 523.25, 587.33]  # A4, C5, D5 notes

        # Play audio on each speaker
        for speaker, freq in zip(speakers, frequencies):
            audio_data = generate_frequency_audio(freq)
            result = remote_client.play_remote_audio(
                device_id=speaker.device_id,
                audio_data=audio_data
            )
            print(f"Playback on {speaker.name}: {result}")

        # Wait to simulate audio playback
        await asyncio.sleep(4)

    finally:
        # Stop service
        service_task.cancel()
        try:
            await service_task
        except asyncio.CancelledError:
            pass

# Audio recording and remote playback
async def record_and_play_example():
    """
    Demonstrate recording audio locally and playing on a remote speaker.
    """
    try:
        import sounddevice as sd
        import soundfile as sf
    except ImportError:
        print("sounddevice or soundfile not installed. Install with: pip install sounddevice soundfile")
        return

    # Start remote speaker service
    service = RemoteSpeakerService()

    # Register a remote speaker
    await service.register_remote_speaker(
        device_id='office_speaker_01',
        name='Office Speaker',
        location='Office'
    )

    # Start service in background
    service_task = asyncio.create_task(service.start_service())

    # Simulate brief delay for service startup
    await asyncio.sleep(2)

    try:
        # Recording parameters
        duration = 5  # seconds
        sample_rate = 44100
        channels = 2

        print("Recording audio... Speak now!")

        # Record audio
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=channels,
            dtype='float32'
        )
        sd.wait()  # Wait until recording is finished

        # Save recording to file (optional)
        sf.write('local_recording.wav', recording, sample_rate)

        # Convert to bytes
        audio_bytes = recording.tobytes()

        # Create client
        remote_client = RemoteSpeakerClient()

        # Play recorded audio on remote speaker
        result = remote_client.play_remote_audio(
            device_id='office_speaker_01',
            audio_data=audio_bytes
        )

        print("Remote Audio Playback Result:", result)

        # Wait to simulate audio playback
        await asyncio.sleep(duration + 1)

    finally:
        # Stop service
        service_task.cancel()
        try:
            await service_task
        except asyncio.CancelledError:
            pass

# Main execution
if __name__ == "__main__":
    import asyncio

    async def run_all_examples():
        """Run all remote speaker examples sequentially."""
        print("\n=== Basic Remote Speaker Example ===")
        await main()

        print("\n=== Text-to-Speech Example ===")
        await text_to_speech_example()

        print("\n=== Multi-Speaker Streaming ===")
        await multi_speaker_streaming()

        print("\n=== Record and Play Example ===")
        await record_and_play_example()

    # Run all examples
    asyncio.run(run_all_examples())