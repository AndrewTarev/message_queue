import json
from dataclasses import dataclass
from aio_pika import connect_robust, Message, IncomingMessage
from aio_pika.abc import (
    AbstractRobustConnection,
    AbstractRobustChannel,
    AbstractRobustQueue,
    AbstractIncomingMessage,
)

from src.core.config import settings
from src.core.utils.logging_config import logging


@dataclass
class RabbitConnection:
    connection: AbstractRobustConnection | None = None
    channel: AbstractRobustChannel | None = None
    queue: AbstractRobustQueue | None = None

    def status(self) -> bool:
        """
        Checks if connection established

        :return: True if connection established
        """
        if self.connection.is_closed or self.channel.is_closed:
            return False
        return True

    async def _clear(self) -> None:
        if not self.channel.is_closed:
            await self.channel.close()
        if not self.connection.is_closed:
            await self.connection.close()

        self.connection = None
        self.channel = None

    async def connect(self) -> None:
        """
        Establish connection with the RabbitMQ

        :return: None
        """
        logging.info("Connecting to the RabbitMQ...")
        try:
            self.connection = await connect_robust(settings.rabbit_config.url)
            self.channel = await self.connection.channel(publisher_confirms=False)
            logging.info("Successfully connected to the RabbitMQ!")
        except Exception as e:
            await self._clear()
            logging.error(f"Failed to connect to RabbitMQ: {str(e)}")

    async def disconnect(self) -> None:
        """
        Disconnect and clear connections from RabbitMQ

        :return: None
        """
        await self._clear()

    @staticmethod
    async def _on_msg(msg: AbstractIncomingMessage):
        # if an exeception gets raised, message gets rejected and put beck in the queue
        async with msg.process(requeue=True):
            # raise Exception("asdfasdf")
            body = json.loads(msg.body.decode("utf-8"))
            if body.get("type") == "test_message":
                print(body)
            return logging.info("Not recognized task type")

    async def consume(self, queue_name):
        self.queue = await self.channel.declare_queue(queue_name)

        await self.queue.consume(
            callback=self._on_msg, no_ack=False  # deliver auto ack on
        )

        logging.info(f"started consuming queue {queue_name}")

    async def send_messages(
        self,
        messages: list | dict,
        routing_key: str = settings.rabbit_config.RMQ_QUEUE,
    ) -> None:
        """
        Public message or messages to the RabbitMQ queue.

        :param messages: list or dict with messages objects.
        :param routing_key: Routing key of RabbitMQ, not required. Tip: the same as in the consumer.
        """
        if not self.channel:
            raise RuntimeError(
                "The message could not be sent because the connection with RabbitMQ is not established"
            )

        if isinstance(messages, dict):
            messages = [messages]

        async with self.channel.transaction():
            for message in messages:
                message = Message(body=json.dumps(message).encode())

                await self.channel.default_exchange.publish(
                    message,
                    routing_key=routing_key,
                )


rabbit_connection = RabbitConnection()
