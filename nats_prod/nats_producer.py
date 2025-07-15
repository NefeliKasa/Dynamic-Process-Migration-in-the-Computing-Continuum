import json
import asyncio
from utils.logging_config import setup_logger
from nats.aio.client import Client as NATS
from nats_prod.safe_nats_call import safe_nats_call
from nats_prod.nats_codec import NatsCodec as Codec
from nats_prod.config import NATS_URL

logger = setup_logger(__name__)


class NatsProducer:
    def __init__(self, subject, json_encode=True):
        self.subject = subject
        self.json_encode = json_encode
        self.nats_url = NATS_URL
        self.nc = NATS()
        self._connected = False

    async def connect(self):
        if not self._connected:
            await safe_nats_call(self.nc.connect, self.nats_url, log_args=True)
            self._connected = True
            logger.info(f"Connected to NATS at {self.nats_url}")

    async def send_message(self, message):
        await self.connect()

        if self.json_encode:
            message = Codec.encode(message)

        await safe_nats_call(self.nc.publish, self.subject, message, log_args=True)
        logger.info(f"Sent message to subject {self.subject}: {message}")

    async def close(self):
        if self._connected:
            await safe_nats_call(self.nc.drain)
            logger.info("NATS connection closed.")
