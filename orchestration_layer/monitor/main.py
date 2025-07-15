import asyncio
from nats_prod.nats_producer import NatsProducer as Producer
from metrics import build_metrics_message
from config import (
    MONITORING_INTERVAL,
    CPU_OBSERVATION_INTERVAL,
    MONITORING_TOPIC,
)


async def main():
    producer = Producer(MONITORING_TOPIC, json_encode=True)

    # The monitoring sidecar will run indefinitely, sending monitoring data at the specified interval.
    try:
        while True:
            message = await asyncio.to_thread(
                build_metrics_message, CPU_OBSERVATION_INTERVAL
            )
            await producer.send_message(message)
            await asyncio.sleep(MONITORING_INTERVAL)
    except asyncio.CancelledError:
        await producer.close()


if __name__ == "__main__":
    asyncio.run(main())
