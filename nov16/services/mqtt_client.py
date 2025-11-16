import os
import json
import asyncio
from aiomqtt import Client



class AsyncIOMQTTService:
    def __init__(self, host: str = os.getenv("MQTT_SERVER"),
                 port: int = int(os.getenv("MQTT_PORT")),
                 reconnect_interval: int = 5):
        with open("services/mqtt_topics.json", "r") as file:
            topic_data = json.load(file)
        self.host = host
        self.port = port
        self.reconnect_interval = reconnect_interval
        self._client: Client | None = None
        self._task: asyncio.Task | None = None
        self._subscribers_topics: dict[str] = {name: topics.get("sub") for name, topics in topic_data.items() if topics.get("sub") is not None}
        self._publish_topics: dict[str] = {name: topics.get("pub") for name, topics in topic_data.items() if topics.get("pub") is not None}
        self.message_dict: dict[str, any] = {name: None for name, topic in topic_data.items() if topic.get("sub") is not None}
        self.message_event: dict[str, any] = {name: asyncio.Event() for name, topic in topic_data.items() if topic.get("sub") is not None}
        self._stopping = asyncio.Event()

    async def start(self):
        """启动 MQTT 循环（自动重连）"""
        self._stopping.clear()
        self._task = asyncio.create_task(self._mqtt_loop())
        print("🚀 MQTT service started")

    async def stop(self):
        """停止 MQTT 循环"""
        print("🧹 Stopping MQTT service...")
        self._stopping.set()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self._client:
            await self._client.disconnect()
        print("✅ MQTT service stopped")

    async def _mqtt_loop(self):
        while not self._stopping.is_set():
            try:
                async with Client(self.host, self.port) as client:
                    self._client = client
                    print(f"✅ Connected to MQTT broker {self.host}:{self.port}")
                    await self._subscribe_all()
                    async for message in client.messages:
                        lock = asyncio.Lock()
                        function_name = [k for k, v in self._subscribers_topics.items() if v == str(message.topic)][0]
                        async with lock:
                            self.message_dict[function_name] = message.payload.decode()
                            self.message_event[function_name].set()
            except Exception as e:
                print(e)


    async def _subscribe_all(self):
        """重新连接后自动重新订阅"""
        if not self._subscribers_topics or not self._client:
            return
        for topic in self._subscribers_topics.values():
            await self._client.subscribe(topic)

    async def publish(self, control_name: str, payload: str, str_encode: str = "utf-8"):
        if not self._client:
            raise RuntimeError("MQTT not connected")
        topic = self._publish_topics.get(control_name)
        if topic:
            await self._client.publish(topic, payload.encode(str_encode))
            print(f"📤 Published to {topic}: {payload}")
        else:
            raise ValueError("Function not set topic in json")