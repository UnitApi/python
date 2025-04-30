#!/usr/bin/env python3
"""
Speaker Audio Playback Example (Fixed)

This script demonstrates how to send audio to a local speaker.
"""

import asyncio
import argparse
import logging
import os
import numpy as np
from typing import Optional, List, Dict, Any


class SpeakerAudioPlaybackExample:
    def __init__(self, debug: bool = False):
        """
        Initialize speaker audio playback example.

        Args:
            debug: Enable debug logging
        """
        # Configure logging
        log_level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)

    async def list_speakers(self) -> List[Dict[str, Any]]:
        """
        List available speakers on the system.
        
        Returns:
            List of available speaker devices
        """
        available_speakers = []
        
        try:
            # Try to use PyAudio to detect speakers (output devices)
            import pyaudio
            
            p = pyaudio.PyAudio()
            info = p.get_host_api_info_by_index(0)
            num_devices = info.get('deviceCount')
            
            # Iterate through all audio devices
            for i in range(num_devices):
                device_info = p.get_device_info_by_index(i)
                
                # Check if this is an output device (speaker)
                if device_info.get('maxOutputChannels') > 0:
                    device_name = device_info.get('name')
                    channels = device_info.get('maxOutputChannels')
                    sample_rate = int(device_info.get('defaultSampleRate'))
                    
                    # Create device info
                    speaker_info = {
                        'index': i,
                        'name': device_name,
                        'channels': channels,
                        'sample_rate': sample_rate
                    }
                    
                    available_speakers.append(speaker_info)
                    self.logger.info(f"Found speaker: {device_name} (index: {i}, channels: {channels}, sample rate: {sample_rate})")
            
            # Clean up
            p.terminate()
                    
        except ImportError:
            self.logger.warning("PyAudio not available for speaker detection")
            
        # If no speakers found, create a virtual speaker entry
        if not available_speakers:
            self.logger.warning("No speakers detected, will use default system audio output")
            available_speakers.append({
                'index': 0,
                'name': 'Default System Audio',
                'channels': 2,
                'sample_rate': 44100
            })
            
        return available_speakers

    async def play_tone(
            self,
            device_index: Optional[int] = None,
            frequency: float = 440.0,
            duration: float = 3.0,
            volume: float = 0.5
    ) -> bool:
        """
        Play a simple tone on a speaker.

        Args:
            device_index: PyAudio device index (None for default)
            frequency: Tone frequency in Hz
            duration: Tone duration in seconds
            volume: Volume level (0.0 to 1.0)

        Returns:
            Success status
        """
        try:
            import pyaudio
            
            # Initialize PyAudio
            p = pyaudio.PyAudio()
            
            # If no device index specified, use default output device
            if device_index is None:
                # Find the first available output device instead of using get_default_output_device_info()
                # which might not be available on all systems
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
            
            # Get device info
            device_info = p.get_device_info_by_index(device_index)
            device_name = device_info.get('name')
            channels = min(2, device_info.get('maxOutputChannels'))
            sample_rate = int(device_info.get('defaultSampleRate'))
            
            self.logger.info(f"Playing {frequency}Hz tone for {duration}s on {device_name}")
            
            # Generate a sine wave tone
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            tone = volume * np.sin(2 * np.pi * frequency * t)
            
            # Apply fade in/out to avoid clicks
            fade_duration = min(0.1, duration / 10)
            fade_samples = int(fade_duration * sample_rate)
            fade_in = np.linspace(0, 1, fade_samples)
            fade_out = np.linspace(1, 0, fade_samples)
            
            tone[:fade_samples] *= fade_in
            tone[-fade_samples:] *= fade_out
            
            # Convert to float32 and duplicate for stereo if needed
            audio_data = tone.astype(np.float32)
            if channels == 2:
                audio_data = np.column_stack((audio_data, audio_data))
            
            # Open stream
            stream = p.open(
                format=pyaudio.paFloat32,
                channels=channels,
                rate=sample_rate,
                output=True,
                output_device_index=device_index,
                frames_per_buffer=1024
            )
            
            # Play the tone
            stream.write(audio_data.tobytes())
            
            # Clean up
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            self.logger.info("Audio playback completed")
            return True
            
        except ImportError:
            self.logger.error("PyAudio not available for audio playback")
            return False
        except Exception as e:
            self.logger.error(f"Failed to play audio: {e}")
            return False

    async def play_audio_file(
            self,
            file_path: str,
            device_index: Optional[int] = None
    ) -> bool:
        """
        Play an audio file on a speaker.

        Args:
            file_path: Path to audio file
            device_index: PyAudio device index (None for default)

        Returns:
            Success status
        """
        if not os.path.exists(file_path):
            self.logger.error(f"Audio file not found: {file_path}")
            return False
            
        try:
            import pyaudio
            import wave
            
            # Check if it's a WAV file
            if file_path.lower().endswith('.wav'):
                self.logger.info(f"Playing WAV file: {file_path}")
                
                # Open the WAV file
                wf = wave.open(file_path, 'rb')
                
                # Initialize PyAudio
                p = pyaudio.PyAudio()
                
                # If no device index specified, find the first available output device
                if device_index is None:
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
                
                # Get device info
                device_info = p.get_device_info_by_index(device_index)
                device_name = device_info.get('name')
                
                # Open stream
                stream = p.open(
                    format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    output_device_index=device_index
                )
                
                self.logger.info(f"Playing audio on {device_name} (channels: {wf.getnchannels()}, rate: {wf.getframerate()})")
                
                # Read data in chunks and play
                chunk_size = 1024
                data = wf.readframes(chunk_size)
                
                while data:
                    stream.write(data)
                    data = wf.readframes(chunk_size)
                
                # Clean up
                stream.stop_stream()
                stream.close()
                p.terminate()
                wf.close()
                
                self.logger.info("Audio playback completed")
                return True
                
            else:
                # For non-WAV files, try to use a media player
                self.logger.info(f"Playing audio file using system media player: {file_path}")
                
                import platform
                import subprocess
                
                system = platform.system()
                
                if system == 'Windows':
                    # Use Windows Media Player
                    subprocess.run(['start', 'wmplayer', file_path], shell=True, check=True)
                elif system == 'Darwin':  # macOS
                    # Use afplay
                    subprocess.run(['afplay', file_path], check=True)
                else:  # Linux and others
                    # Try several players
                    players = ['aplay', 'paplay', 'mplayer', 'mpg123', 'mpg321', 'play']
                    
                    for player in players:
                        try:
                            subprocess.run(['which', player], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            subprocess.run([player, file_path], check=True)
                            self.logger.info(f"Played audio using {player}")
                            return True
                        except subprocess.SubprocessError:
                            continue
                    
                    self.logger.error("No suitable audio player found")
                    return False
                
                return True
                
        except ImportError:
            self.logger.error("Required audio libraries not available")
            return False
        except Exception as e:
            self.logger.error(f"Failed to play audio file: {e}")
            return False

    async def generate_audio_file(
            self,
            output_file: str = 'generated_tone.wav',
            frequency: float = 440.0,
            duration: float = 3.0,
            volume: float = 0.5,
            sample_rate: int = 44100
    ) -> bool:
        """
        Generate an audio file with a tone.

        Args:
            output_file: Path to save the generated audio
            frequency: Tone frequency in Hz
            duration: Tone duration in seconds
            volume: Volume level (0.0 to 1.0)
            sample_rate: Audio sample rate

        Returns:
            Success status
        """
        try:
            import wave
            import struct
            
            self.logger.info(f"Generating {frequency}Hz tone for {duration}s")
            
            # Generate a sine wave tone
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            tone = volume * np.sin(2 * np.pi * frequency * t)
            
            # Apply fade in/out to avoid clicks
            fade_duration = min(0.1, duration / 10)
            fade_samples = int(fade_duration * sample_rate)
            fade_in = np.linspace(0, 1, fade_samples)
            fade_out = np.linspace(1, 0, fade_samples)
            
            tone[:fade_samples] *= fade_in
            tone[-fade_samples:] *= fade_out
            
            # Convert to 16-bit PCM
            audio_data = (tone * 32767).astype(np.int16)
            
            # Create WAV file
            with wave.open(output_file, 'wb') as wf:
                wf.setnchannels(1)  # Mono
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(sample_rate)
                wf.writeframes(audio_data.tobytes())
            
            self.logger.info(f"Audio file saved to {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to generate audio file: {e}")
            return False


async def main():
    """
    Run the speaker audio playback example.
    """
    parser = argparse.ArgumentParser(description='Speaker Audio Playback Example (Fixed)')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--list', action='store_true', help='List available speakers')
    parser.add_argument('--device', type=int, help='Speaker device index')
    parser.add_argument('--all-devices', action='store_true', help='Play on all available speakers')
    parser.add_argument('--file', help='Audio file to play')
    parser.add_argument('--generate', action='store_true', help='Generate and play a tone')
    parser.add_argument('--frequency', type=float, default=440.0, help='Tone frequency in Hz')
    parser.add_argument('--duration', type=float, default=3.0, help='Tone duration in seconds')
    parser.add_argument('--volume', type=float, default=0.5, help='Volume level (0.0 to 1.0)')
    parser.add_argument('--output', default='generated_tone.wav', help='Output file for generated tone')
    
    args = parser.parse_args()
    
    example = SpeakerAudioPlaybackExample(debug=args.debug)
    
    if args.list:
        # List available speakers
        await example.list_speakers()
    elif args.all_devices:
        # Play on all available speakers
        speakers = await example.list_speakers()
        
        if args.file:
            # Play audio file on all speakers
            for speaker in speakers:
                example.logger.info(f"Playing on device: {speaker['name']} (index: {speaker['index']})")
                try:
                    success = await example.play_audio_file(file_path=args.file, device_index=speaker['index'])
                    if not success:
                        example.logger.warning(f"Failed to play audio on device: {speaker['name']} (index: {speaker['index']})")
                except Exception as e:
                    example.logger.warning(f"Error playing on device: {speaker['name']} (index: {speaker['index']}): {e}")
        elif args.generate:
            # Generate audio file and play it on all speakers
            if await example.generate_audio_file(
                output_file=args.output,
                frequency=args.frequency,
                duration=args.duration,
                volume=args.volume
            ):
                for speaker in speakers:
                    example.logger.info(f"Playing on device: {speaker['name']} (index: {speaker['index']})")
                    try:
                        success = await example.play_audio_file(file_path=args.output, device_index=speaker['index'])
                        if not success:
                            example.logger.warning(f"Failed to play audio on device: {speaker['name']} (index: {speaker['index']})")
                    except Exception as e:
                        example.logger.warning(f"Error playing on device: {speaker['name']} (index: {speaker['index']}): {e}")
        else:
            # Play a tone directly on all speakers
            for speaker in speakers:
                example.logger.info(f"Playing on device: {speaker['name']} (index: {speaker['index']})")
                try:
                    success = await example.play_tone(
                        device_index=speaker['index'],
                        frequency=args.frequency,
                        duration=args.duration,
                        volume=args.volume
                    )
                    if not success:
                        example.logger.warning(f"Failed to play tone on device: {speaker['name']} (index: {speaker['index']})")
                except Exception as e:
                    example.logger.warning(f"Error playing on device: {speaker['name']} (index: {speaker['index']}): {e}")
    elif args.file:
        # Play audio file
        await example.play_audio_file(file_path=args.file, device_index=args.device)
    elif args.generate:
        # Generate audio file and play it
        if await example.generate_audio_file(
            output_file=args.output,
            frequency=args.frequency,
            duration=args.duration,
            volume=args.volume
        ):
            await example.play_audio_file(file_path=args.output, device_index=args.device)
    else:
        # Play a tone directly
        await example.play_tone(
            device_index=args.device,
            frequency=args.frequency,
            duration=args.duration,
            volume=args.volume
        )


if __name__ == "__main__":
    asyncio.run(main())
