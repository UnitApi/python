import asyncio
import base64
import logging
from unitapi.core.client import UnitAPIClient


class RemoteSpeakerClient:
    def __init__(
            self,
            server_host: str,  # IP serwera
            server_port: int = 7890
    ):
        self.client = UnitAPIClient(
            server_host=server_host,
            server_port=server_port
        )

        # Logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)

    def list_speakers(self):
        """
        Lista dostępnych głośników.
        """
        return self.client.list_devices(device_type='speaker')

    def play_audio(self, device_id: str, audio_data: bytes):
        """
        Odtwórz dźwięk na zdalnym głośniku.
        """
        base64_audio = base64.b64encode(audio_data).decode()

        return self.client.execute_command(
            device_id=device_id,
            command='play_audio',
            params={'base64_data': base64_audio}
        )


# Przykładowe użycie
import sounddevice as sd
import numpy as np


async def record_and_play():
    """
    Nagraj dźwięk lokalnie i wyślij na zdalny głośnik.
    """
    # Parametry nagrywania
    duration = 5  # sekundy
    sample_rate = 44100
    channels = 2

    print("Nagraj dźwięk (5 sekund)")

    # Nagraj dźwięk
    recording = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=channels,
        dtype='float32'
    )
    sd.wait()  # Czekaj na zakończenie nagrywania

    # Konwersja do bajtów
    audio_bytes = recording.tobytes()

    # Klient zdalnego głośnika
    client = RemoteSpeakerClient(
        server_host='192.168.1.100'  # ZMIEŃ NA ADRES IP SERWERA
    )

    # Lista głośników
    speakers = client.list_speakers()
    print("Dostępne głośniki:", speakers)

    # Odtwórz na pierwszym głośniku
    if speakers:
        result = client.play_audio(
            device_id=speakers[0]['device_id'],
            audio_data=audio_bytes
        )
        print("Wynik odtwarzania:", result)


async def main():
    await record_and_play()


if __name__ == "__main__":
    asyncio.run(main())