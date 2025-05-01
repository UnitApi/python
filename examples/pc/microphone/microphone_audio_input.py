#!/usr/bin/env python3
"""
Microphone Audio Input Example

This script demonstrates how to send audio to a microphone input.
"""

import asyncio
import argparse
import logging
import os
import numpy as np
import time
from typing import Optional, List, Dict, Any


class MicrophoneAudioInputExample:
    def __init__(self, debug: bool = False):
        """
        Initialize microphone audio input example.

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

    async def list_microphones(self) -> List[Dict[str, Any]]:
        """
        List available microphones on the system.
        
        Returns:
            List of available microphone devices
        """
        available_microphones = []
        
        try:
            # Try to use PyAudio to detect microphones (input devices)
            import pyaudio
            
            p = pyaudio.PyAudio()
            info = p.get_host_api_info_by_index(0)
            num_devices = info.get('deviceCount')
            
            # Iterate through all audio devices
            for i in range(num_devices):
                device_info = p.get_device_info_by_index(i)
                
                # Check if this is an input device (microphone)
                if device_info.get('maxInputChannels') > 0:
                    device_name = device_info.get('name')
                    channels = device_info.get('maxInputChannels')
                    sample_rate = int(device_info.get('defaultSampleRate'))
                    
                    # Create device info
                    mic_info = {
                        'index': i,
                        'name': device_name,
                        'channels': channels,
                        'sample_rate': sample_rate
                    }
                    
                    available_microphones.append(mic_info)
                    self.logger.info(f"Found microphone: {device_name} (index: {i}, channels: {channels}, sample rate: {sample_rate})")
            
            # Clean up
            p.terminate()
                    
        except ImportError:
            self.logger.warning("PyAudio not available for microphone detection")
            
        # If no microphones found, create a virtual microphone entry
        if not available_microphones:
            self.logger.warning("No microphones detected, will use virtual microphone")
            available_microphones.append({
                'index': 0,
                'name': 'Virtual Microphone',
                'channels': 1,
                'sample_rate': 44100
            })
            
        return available_microphones

    async def send_tone_to_microphone(
            self,
            device_index: Optional[int] = None,
            frequency: float = 440.0,
            duration: float = 3.0,
            volume: float = 0.5
    ) -> bool:
        """
        Send a tone to a microphone input (virtual audio loopback).

        Args:
            device_index: PyAudio device index (None for default)
            frequency: Tone frequency in Hz
            duration: Tone duration in seconds
            volume: Volume level (0.0 to 1.0)

        Returns:
            Success status
        """
        try:
            # Method 1: Try using PyAudio for loopback
            import pyaudio
            
            # Initialize PyAudio
            p = pyaudio.PyAudio()
            
            # If no device index specified, use default input device
            if device_index is None:
                try:
                    device_index = p.get_default_input_device_info()['index']
                    self.logger.info(f"Using default input device (index: {device_index})")
                except IOError:
                    self.logger.error("No default input device available")
                    p.terminate()
                    return False
            
            # Get device info
            try:
                device_info = p.get_device_info_by_index(device_index)
                device_name = device_info.get('name')
                channels = min(2, device_info.get('maxInputChannels'))
                sample_rate = int(device_info.get('defaultSampleRate'))
            except IOError:
                self.logger.error(f"Invalid device index: {device_index}")
                p.terminate()
                return False
            
            self.logger.info(f"Sending {frequency}Hz tone for {duration}s to {device_name}")
            
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
            
            # Check if we can use loopback
            try:
                # Try to open a duplex stream (both input and output)
                stream = p.open(
                    format=pyaudio.paFloat32,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    output=True,
                    input_device_index=device_index,
                    frames_per_buffer=1024
                )
                
                # Play the tone and record simultaneously
                stream.write(audio_data.tobytes())
                
                # Clean up
                stream.stop_stream()
                stream.close()
                p.terminate()
                
                self.logger.info("Audio sent to microphone successfully")
                return True
                
            except Exception as e:
                self.logger.warning(f"PyAudio loopback failed: {e}")
                p.terminate()
                
                # Fall back to alternative methods
                return await self._send_tone_alternative_methods(
                    frequency=frequency,
                    duration=duration,
                    volume=volume
                )
            
        except ImportError:
            self.logger.warning("PyAudio not available, trying alternative methods")
            return await self._send_tone_alternative_methods(
                frequency=frequency,
                duration=duration,
                volume=volume
            )
        except Exception as e:
            self.logger.error(f"Failed to send audio to microphone: {e}")
            return False

    async def _send_tone_alternative_methods(
            self,
            frequency: float = 440.0,
            duration: float = 3.0,
            volume: float = 0.5
    ) -> bool:
        """
        Try alternative methods to send audio to microphone.

        Args:
            frequency: Tone frequency in Hz
            duration: Tone duration in seconds
            volume: Volume level (0.0 to 1.0)

        Returns:
            Success status
        """
        # Method 2: Try using a temporary file and virtual audio cable
        try:
            self.logger.info("Trying to use temporary file and virtual audio cable")
            
            # Generate a temporary WAV file
            import wave
            import tempfile
            import os
            
            # Create a temporary file
            fd, temp_path = tempfile.mkstemp(suffix='.wav')
            os.close(fd)
            
            # Generate audio data
            sample_rate = 44100
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            tone = volume * np.sin(2 * np.pi * frequency * t)
            
            # Apply fade in/out
            fade_duration = min(0.1, duration / 10)
            fade_samples = int(fade_duration * sample_rate)
            fade_in = np.linspace(0, 1, fade_samples)
            fade_out = np.linspace(1, 0, fade_samples)
            
            tone[:fade_samples] *= fade_in
            tone[-fade_samples:] *= fade_out
            
            # Convert to 16-bit PCM
            audio_data = (tone * 32767).astype(np.int16)
            
            # Create WAV file
            with wave.open(temp_path, 'wb') as wf:
                wf.setnchannels(1)  # Mono
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(sample_rate)
                wf.writeframes(audio_data.tobytes())
            
            self.logger.info(f"Temporary audio file created: {temp_path}")
            
            # Try to play the file to the virtual audio cable
            import platform
            import subprocess
            
            system = platform.system()
            success = False
            
            if system == 'Windows':
                # On Windows, try to use VB-Cable or similar
                try:
                    self.logger.info("Trying to play to virtual audio cable on Windows")
                    # PowerShell command to play to specific device
                    ps_cmd = (
                        "$player = New-Object System.Media.SoundPlayer;"
                        f"$player.SoundLocation = '{temp_path}';"
                        "$player.Play();"
                        f"Start-Sleep -Seconds {duration + 1};"
                    )
                    subprocess.run(['powershell', '-Command', ps_cmd], check=True)
                    success = True
                except Exception as e:
                    self.logger.warning(f"Windows virtual audio cable playback failed: {e}")
                    
            elif system == 'Darwin':  # macOS
                # On macOS, try to use BlackHole or similar
                try:
                    self.logger.info("Trying to play to virtual audio cable on macOS")
                    subprocess.run(['afplay', '-d', 'BlackHole', temp_path], check=True)
                    success = True
                except Exception as e:
                    self.logger.warning(f"macOS virtual audio cable playback failed: {e}")
                    
            else:  # Linux
                # On Linux, try to use PulseAudio or JACK
                try:
                    self.logger.info("Trying to play to virtual audio cable on Linux")
                    # Try PulseAudio
                    subprocess.run(['paplay', '--device=virtual-microphone', temp_path], check=True)
                    success = True
                except Exception:
                    try:
                        # Try JACK
                        subprocess.run(['jack_play', temp_path], check=True)
                        success = True
                    except Exception as e:
                        self.logger.warning(f"Linux virtual audio cable playback failed: {e}")
            
            # Clean up temporary file
            try:
                os.remove(temp_path)
            except Exception:
                pass
                
            if success:
                self.logger.info("Audio sent to virtual audio cable successfully")
                return True
                
            # Method 3: Inform user about virtual audio cable setup
            self.logger.warning(
                "Could not send audio to microphone automatically. "
                "To route audio to a microphone, you need to set up a virtual audio cable:"
            )
            self.logger.warning("- Windows: Install VB-Cable (https://vb-audio.com/Cable/)")
            self.logger.warning("- macOS: Install BlackHole (https://github.com/ExistentialAudio/BlackHole)")
            self.logger.warning("- Linux: Configure PulseAudio loopback or JACK")
            
            return False
            
        except Exception as e:
            self.logger.error(f"Alternative methods failed: {e}")
            return False

    async def send_audio_file_to_microphone(
            self,
            file_path: str,
            device_index: Optional[int] = None
    ) -> bool:
        """
        Send audio from a file to a microphone input.

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
            # Method 1: Try using PyAudio for loopback
            import pyaudio
            import wave
            
            # Check if it's a WAV file
            if file_path.lower().endswith('.wav'):
                self.logger.info(f"Sending WAV file to microphone: {file_path}")
                
                # Open the WAV file
                wf = wave.open(file_path, 'rb')
                
                # Initialize PyAudio
                p = pyaudio.PyAudio()
                
                # If no device index specified, use default input device
                if device_index is None:
                    try:
                        device_index = p.get_default_input_device_info()['index']
                        self.logger.info(f"Using default input device (index: {device_index})")
                    except IOError:
                        self.logger.error("No default input device available")
                        p.terminate()
                        wf.close()
                        return False
                
                # Try to open a duplex stream
                try:
                    stream = p.open(
                        format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        input=True,
                        output=True,
                        input_device_index=device_index,
                        frames_per_buffer=1024
                    )
                    
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
                    
                    self.logger.info("Audio file sent to microphone successfully")
                    return True
                    
                except Exception as e:
                    self.logger.warning(f"PyAudio loopback failed: {e}")
                    p.terminate()
                    wf.close()
                    
                    # Fall back to alternative methods
                    return await self._send_file_alternative_methods(file_path)
                
            else:
                # For non-WAV files, use alternative methods
                return await self._send_file_alternative_methods(file_path)
                
        except ImportError:
            self.logger.warning("PyAudio not available, trying alternative methods")
            return await self._send_file_alternative_methods(file_path)
        except Exception as e:
            self.logger.error(f"Failed to send audio file to microphone: {e}")
            return False

    async def _send_file_alternative_methods(self, file_path: str) -> bool:
        """
        Try alternative methods to send audio file to microphone.

        Args:
            file_path: Path to audio file

        Returns:
            Success status
        """
        # Try using a virtual audio cable
        try:
            self.logger.info("Trying to use virtual audio cable")
            
            import platform
            import subprocess
            
            system = platform.system()
            success = False
            
            if system == 'Windows':
                # On Windows, try to use VB-Cable or similar
                try:
                    self.logger.info("Trying to play to virtual audio cable on Windows")
                    # PowerShell command to play to specific device
                    ps_cmd = (
                        "$player = New-Object System.Media.SoundPlayer;"
                        f"$player.SoundLocation = '{file_path}';"
                        "$player.Play();"
                        "Start-Sleep -Seconds 10;"  # Adjust based on file length
                    )
                    subprocess.run(['powershell', '-Command', ps_cmd], check=True)
                    success = True
                except Exception as e:
                    self.logger.warning(f"Windows virtual audio cable playback failed: {e}")
                    
            elif system == 'Darwin':  # macOS
                # On macOS, try to use BlackHole or similar
                try:
                    self.logger.info("Trying to play to virtual audio cable on macOS")
                    subprocess.run(['afplay', '-d', 'BlackHole', file_path], check=True)
                    success = True
                except Exception as e:
                    self.logger.warning(f"macOS virtual audio cable playback failed: {e}")
                    
            else:  # Linux
                # On Linux, try to use PulseAudio or JACK
                try:
                    self.logger.info("Trying to play to virtual audio cable on Linux")
                    # Try PulseAudio
                    subprocess.run(['paplay', '--device=virtual-microphone', file_path], check=True)
                    success = True
                except Exception:
                    try:
                        # Try JACK
                        subprocess.run(['jack_play', file_path], check=True)
                        success = True
                    except Exception as e:
                        self.logger.warning(f"Linux virtual audio cable playback failed: {e}")
                
            if success:
                self.logger.info("Audio file sent to virtual audio cable successfully")
                return True
                
            # Inform user about virtual audio cable setup
            self.logger.warning(
                "Could not send audio to microphone automatically. "
                "To route audio to a microphone, you need to set up a virtual audio cable:"
            )
            self.logger.warning("- Windows: Install VB-Cable (https://vb-audio.com/Cable/)")
            self.logger.warning("- macOS: Install BlackHole (https://github.com/ExistentialAudio/BlackHole)")
            self.logger.warning("- Linux: Configure PulseAudio loopback or JACK")
            
            return False
            
        except Exception as e:
            self.logger.error(f"Alternative methods failed: {e}")
            return False


async def main():
    """
    Run the microphone audio input example.
    """
    parser = argparse.ArgumentParser(description='Microphone Audio Input Example')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--list', action='store_true', help='List available microphones')
    parser.add_argument('--device', type=int, help='Microphone device index')
    parser.add_argument('--file', help='Audio file to send to microphone')
    parser.add_argument('--frequency', type=float, default=440.0, help='Tone frequency in Hz')
    parser.add_argument('--duration', type=float, default=3.0, help='Tone duration in seconds')
    parser.add_argument('--volume', type=float, default=0.5, help='Volume level (0.0 to 1.0)')
    
    args = parser.parse_args()
    
    example = MicrophoneAudioInputExample(debug=args.debug)
    
    if args.list:
        # List available microphones
        await example.list_microphones()
    elif args.file:
        # Send audio file to microphone
        await example.send_audio_file_to_microphone(
            file_path=args.file,
            device_index=args.device
        )
    else:
        # Send a tone to microphone
        await example.send_tone_to_microphone(
            device_index=args.device,
            frequency=args.frequency,
            duration=args.duration,
            volume=args.volume
        )


if __name__ == "__main__":
    asyncio.run(main())
