# trio_paho_mqtt
[trio](https://github.com/python-trio/trio) specific async MQTT client. The goal of this project is to have all 
the MQTT protocol stuff handled by [paho-mqtt](https://github.com/eclipse/paho.mqtt.python),
while the async loopy stuff is handled by trio. This keeps our MQTT communication async, without having to
shove paho-mqtt into a thread, and without having to reimplement the MQTT protocol.

All callbacks are also removed to be more trio-like. Messages are accessed through an `async for` loop.

This is meant to be a light-as-possible wrapper around paho-mqtt. That way if something goes wrong with MQTT message
parsing, it's not my fault ;-)

## Usage
First, see the `example.py` and paho-mqtt documentation.
The goal is to expose all the same methods as the paho-mqtt `Client`. If any methods (besides callbacks) are missing
or do something unexpected, this is a bug. Please open an issue.

`AsyncClient` is initialized with a sync `mqtt.Client` and a `trio.Nursery` but then otherwise should operate much
like the sync `Client`.  Methods are *not* coroutines, they are non-blocking functions, so you do not need to call
`await`. The only exception is accessing messages through `async for`.

### Example
```python
import paho.mqtt.client as mqtt
import trio
from trio_paho_mqtt import AsyncClient


async def handle_messages(client):
    async for msg in client.messages():
        print(f"Received msg: {msg}")

async with trio.open_nursery() as nursery:
    sync_client = mqtt.Client()
    client = AsyncClient(sync_client, nursery)
    client.connect('mqtt.eclipse.org', 1883, 60)
    client.subscribe(topic)
    client.publish(topic, msg)

    nursery.start_soon(handle_messages, client)
```

## Related projects
  - [gmqtt](https://github.com/wialon/gmqtt) - Uses asyncio and callbacks. Isn't compatible with trio.
  - [hbmqtt](https://github.com/beerfactory/hbmqtt) - Uses asyncio. Reimplements the MQTT protocol.
  - [aiomqtt](https://github.com/mossblaser/aiomqtt) - Uses asyncio and wraps paho, but still uses the loop from 
  paho-mqtt. I believe all operations are put into a worker thread.
  - [distmqtt](https://github.com/smurfix/distmqtt) - anyio-ified hbmqtt fork. Works with trio.