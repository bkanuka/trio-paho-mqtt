#!/usr/bin/env python3

import time
import uuid

import paho.mqtt.client as mqtt
import trio

from trio_paho_mqtt import AsyncClient

client_id = 'trio-paho-mqtt/' + str(uuid.uuid4())
topic = client_id
print("Using client_id / topic: " + client_id)


async def test_read(client):
    async for msg in client.messages():
        print(f"Received msg: {msg}")


async def test_write(client):
    for i in range(3):
        print("sleeping for 5 seconds")
        await trio.sleep(5)
        now = time.time()
        print(f"publishing: {now} * 40000")
        client.publish(topic, bytes(str(now), encoding='utf8') * 40000, qos=1)
        print(f"publish took {time.time() - now} seconds")
    client.disconnect()


async def main():
    async with trio.open_nursery() as nursery:

        sync_client = mqtt.Client()
        client = AsyncClient(sync_client, nursery)
        client.connect('mqtt.eclipse.org', 1883, 60)
        client.subscribe(topic)

        nursery.start_soon(test_read, client)
        nursery.start_soon(test_write, client)


print("Starting")
trio.run(main)
print("Finished")
