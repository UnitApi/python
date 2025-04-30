import asyncio
import logging
from unitapi.core.server import UnitAPIServer
from unitapi.protocols.websocket import WebSocketProtocol
from remote_speaker_device import RemoteSpeakerDevice


class RemoteSpeakerServer:
    def __init__(
            self,
            server_host: str = '0.0.0.0',  # Nasłuch na wszystkich interfejsach
            server_port: int = 7890,
            ws_host: str = '0.0.0.0',
            ws_port: int = 8765
    ):
        # UnitAPI Server
        self.server = UnitAPIServer(host=server_host, port=server_port)

        # WebSocket Protocol
        self.websocket = WebSocketProtocol(host=ws_host, port=ws_port)

        # Speakers registry
        self.speakers = {}

        # Logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)

    async def register_speaker(
            self,
            device_id: str,
            name: str,
            location: str
    ):
        """
        Zarejestruj zdalny głośnik.
        """
        speaker = RemoteSpeakerDevice(
            device_id=device_id,
            name=name,
            metadata={
                'location': location,
                'sample_rate': 44100,
                'channels': 2
            }
        )

        # Połącz głośnik
        await speaker.connect()

        # Zarejestruj w serwerze
        self.server.register_device(
            device_id=device_id,
            device_type='speaker',
            metadata={
                'name': name,
                'location': location
            }
        )

        # Zachowaj referencję
        self.speakers[device_id] = speaker

        self.logger.info(f"Zarejestrowano głośnik: {device_id}")

    async def start(self):
        """
        Uruchom serwer i usługi.
        """
        # Zarejestruj domyślny głośnik
        await self.register_speaker(
            device_id='living_room_speaker',
            name='Główny Głośnik',
            location='Salon'
        )

        # Uruchom serwery
        server_task = asyncio.create_task(self.server.start())
        websocket_task = asyncio.create_task(self.websocket.create_server())

        self.logger.info("Serwer uruchomiony")

        # Czekaj na zadania
        await asyncio.gather(server_task, websocket_task)


async def main():
    server = RemoteSpeakerServer()
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())