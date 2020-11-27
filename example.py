#!/usr/bin/env python3

import time
import uuid

import paho.mqtt.client as mqtt
import trio

from trio_paho_mqtt import AsyncClient

client_id = 'trio-paho-mqtt/' + str(uuid.uuid4())
topic = client_id
n_messages = 3
print("Using client_id / topic: " + client_id)
print(f"Sending {n_messages} messages.")


async def test_read(client, nursery):
    """Read from the broker. Quit after all messages have been received."""
    count = 0
    async for msg in client.messages():
        # Got a message. Print the first few bytes.
        print(f"< Received msg: {msg.payload[:18]}")
        count += 1
        if count == n_messages:
            # We have received all the messages. Cancel.
            nursery.cancel_scope.cancel()


async def test_write(client):
    """Publish a long message. The message will typically be about 720k bytes, so it will take some time to send.
    Publishing asynchronously will cause this function to return almost immediately."""
    now = time.time()
    print(f"> Publishing: {now} * 40000")
    client.publish(topic, bytes(str(now), encoding='utf8') * 40000, qos=1)
    print(f"publish took {time.time() - now} seconds")


async def main():
    async with trio.open_nursery() as nursery:
        # Get a regular MQTT client
        sync_client = mqtt.Client()
        # Wrap it to create an asyncronous version
        client = AsyncClient(sync_client, nursery)
        # Connect to the broker, and subscribe to the topic
        client.connect('mqtt.eclipse.org', 1883, 60)
        client.subscribe(topic)

        # Start the reader
        nursery.start_soon(test_read, client, nursery)

        # Start a bunch of writers. Wait 5 seconds between them to demonstrate the asynchronous nature of reading and
        # writing:
        for i in range(n_messages):
            nursery.start_soon(test_write, client)
            await trio.sleep(5)


print("Starting")
trio.run(main)
print("Finished")
