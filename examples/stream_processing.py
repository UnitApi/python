"""
stream_processing.py
"""

import asyncio
import logging
import numpy as np
from typing import Dict, Any, List, Optional

from unitapi.core.server import UnitAPIServer
from unitapi.devices.base import BaseDevice, DeviceStatus


class StreamProcessor:
    """
    Advanced stream processing utility for UnitAPI.
    """

    def __init__(self, buffer_size: int = 1024):
        """
        Initialize stream processor.

        :param buffer_size: Size of processing buffer
        """
        self.buffer_size = buffer_size
        self.logger = logging.getLogger(self.__class__.__name__)

        # Processing pipeline stages
        self.processors: List[Callable] = []

    def add_processor(self, processor: Callable):
        """
        Add a processing stage to the pipeline.

        :param processor: Processing function
        """
        self.processors.append(processor)

    async def process_stream(self, stream_data: bytes) -> bytes:
        """
        Process input stream through configured pipeline.

        :param stream_data: Input stream bytes
        :return: Processed stream bytes
        """
        # Convert to numpy array
        data_array = np.frombuffer(stream_data, dtype=np.float32)

        # Apply processors
        for processor in self.processors:
            data_array = await processor(data_array)

        return data_array.tobytes()


class StreamDevice(BaseDevice):
    """
    Demonstration device for stream processing.
    """

    def __init__(
            self,
            device_id: str,
            name: str,
            stream_type: str,
            metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize stream device.

        :param device_id: Unique device identifier
        :param name: Device name
        :param stream_type: Type of stream (audio, video, sensor)
        :param metadata: Additional device information
        """
        super().__init__(
            device_id=device_id,
            name=name,
            device_type='stream',
            metadata=metadata or {}
        )

        # Stream processing configuration
        self.stream_processor = StreamProcessor()
        self.logger = logging.getLogger(f"StreamDevice_{device_id}")

    async def connect(self) -> bool:
        """
        Connect to the stream device.

        :return: Connection status
        """
        try:
            self.status = DeviceStatus.ONLINE
            self.logger.info(f"Stream device {self.device_id} connected")
            return True
        except Exception as e:
            self.status = DeviceStatus.ERROR
            self.logger.error(f"Stream device connection failed: {e}")
            return False

    async def disconnect(self) -> bool:
        """
        Disconnect from the stream device.

        :return: Disconnection status
        """
        try:
            self.status = DeviceStatus.OFFLINE
            self.logger.info(f"Stream device {self.device_id} disconnected")
            return True
        except Exception as e:
            self.logger.error(f"Stream device disconnection failed: {e}")
            return False

    async def add_stream_processor(self, processor: Callable):
        """
        Add a processing stage to the stream.

        :param processor: Processing function
        """
        self.stream_processor.add_processor(processor)

    async def process_stream(self, stream_data: bytes) -> bytes:
        """
        Process input stream.

        :param stream_data: Input stream bytes
        :return: Processed stream bytes
        """
        return await self.stream_processor.process_stream(stream_data)

    async def execute_command(
            self,
            command: str,
            params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute commands on the stream device.

        :param command: Command to execute
        :param params: Command parameters
        :return: Command execution result
        """
        try:
            if command == 'process_stream':
                # Expect base64 encoded stream data
                import base64

                if 'base64_data' in params:
                    stream_bytes = base64.b64decode(params['base64_data'])
                elif 'file_path' in params:
                    # Read stream from file
                    with open(params['file_path'], 'rb') as f:
                        stream_bytes = f.read()
                else:
                    raise ValueError("No stream data provided")

                # Process stream
                processed_data = await self.process_stream(stream_bytes)

                return {
                    'status': 'success',
                    'processed_data_length': len(processed_data)
                }

            elif command == 'add_processor':
                # Dynamic processor addition
                if 'processor' in params:
                    await self.add_stream_processor(params['processor'])
                    return {
                        'status': 'success',
                        'message': 'Processor added'
                    }
                else:
                    raise ValueError("No processor provided")

            else:
                raise ValueError(f"Unsupported command: {command}")

        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }


# Example stream processing functions
async def noise_reduction_processor(data: np.ndarray) -> np.ndarray:
    """
    Simple noise reduction processor.

    :param data: Input data array
    :return: Noise-reduced data
    """
    # Basic noise reduction using moving average
    kernel_size = 5
    kernel = np.ones(kernel_size) / kernel_size
    return np.convolve(data, kernel, mode='same')


async def amplification_processor(data: np.ndarray, gain: float = 2.0) -> np.ndarray:
    """
    Audio amplification processor.

    :param data: Input data array
    :param gain: Amplification factor
    :return: Amplified data
    """
    # Clip to prevent overflow
    return np.clip(data * gain, -1.0, 1.0)


async def demonstration():
    """
    Demonstrate stream processing capabilities.
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create UnitAPI server
    server = UnitAPIServer(host='localhost', port=7890)

    # Create stream device
    stream_device = StreamDevice(
        device_id='audio_stream_01',
        name='Audio Processing Device',
        stream_type='audio'
    )

    # Register device on server
    server.register_device(
        device_id=stream_device.device_id,
        device_type='stream',
        metadata={
            'name': stream_device.name,
            'stream_type': 'audio'
        }
    )

    # Connect device
    await stream_device.connect()

    # Add processors
    await stream_device.add_stream_processor(noise_reduction_processor)
    await stream_device.add_stream_processor(
        lambda data: amplification_processor(data, gain=1.5)
    )

    # Generate test stream data
    import numpy as np
    test_data = np.random.normal(0, 0.1, 1024).astype(np.float32)

    # Process stream
    processed_data = await stream_device.process_stream(test_data.tobytes())

    # Disconnect device
    await stream_device.disconnect()


if __name__ == "__main__":
    asyncio.run(demonstration())