import json
import asyncio
from utils.logging_config import setup_logger
from nats.aio.client import Client as NATS
from nats_prod.safe_nats_call import safe_nats_call
from nats_prod.nats_codec import NatsCodec as Codec
from nats_prod.config import NATS_URL

logger = setup_logger(__name__)


class NatsConsumer:
    def __init__(
        self, subjects, message_handler, handler_is_async=False, json_decode=True
    ):
        self.subjects = subjects
        self.json_decode = json_decode
        self.nats_url = NATS_URL
        self.nc = NATS()
        self.message_handler = message_handler
        self.handler_is_async = handler_is_async
        self.stop_event = False
        self._connected = False

    async def connect(self):
        if not self._connected:
            await safe_nats_call(self.nc.connect, self.nats_url, log_args=True)
            self._connected = True
            logger.info(f"Connected to NATS at {self.nats_url}")

    async def _handler(self, msg):
        subject = msg.subject

        if self.json_decode:
            data = Codec.decode(msg.data)
        else:
            data = msg.data
        logger.info(f"Received message on subject {subject}: {data}")

        if self.message_handler:
            if self.handler_is_async:
                if len(self.subjects) > 1:
                    await self.message_handler(subject, data, consumer=self)
                else:
                    await self.message_handler(data, consumer=self)
            else:
                if len(self.subjects) > 1:
                    await asyncio.to_thread(
                        self.message_handler, subject, data, consumer=self
                    )
                else:
                    await asyncio.to_thread(self.message_handler, data, consumer=self)

    async def consume(self):
        await self.connect()

        for subject in self.subjects:
            await safe_nats_call(
                self.nc.subscribe, subject, cb=self._handler, log_args=True
            )
            logger.info(f"Subscribed to subject: {subject}")

        try:
            while not self.stop_event:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info("Consumer task cancelled, shutting down.")
        finally:
            await safe_nats_call(self.close)

    async def close(self):
        await safe_nats_call(self.nc.drain)
        logger.info("Closed NATS consumer connection.")
