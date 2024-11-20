import asyncio
import json

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from src.core.config import settings
from src.core.utils.logging_config import logging

PARALLEL_TASKS = 10


def test_task(message: dict):
    print(f'Test task message: {message.get("message")}')


async def message_router(
    message: AbstractIncomingMessage,
) -> None:
    async with message.process():
        body = json.loads(message.body.decode())
        if body.get("type") == "test_message":
            return test_task(body)
        return logging.info("Not recognized task type")


async def main() -> None:
    connection = await aio_pika.connect_robust(settings.rabbit_config.url)

    queue_name = settings.rabbit_config.RMQ_QUEUE

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=PARALLEL_TASKS)
        queue = await channel.declare_queue(queue_name, auto_delete=True)

        logging.info("Consumer successfully started!")

        await queue.consume(message_router)

        try:
            await asyncio.Future()
        finally:
            await connection.close()


if __name__ == "__main__":
    logging.info("Starting consumer...")
    asyncio.run(main())
