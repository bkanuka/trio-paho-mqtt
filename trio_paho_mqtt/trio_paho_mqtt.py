#!/usr/bin/env python3

import socket

import paho.mqtt.client as mqtt
import trio


class AsyncClient:
    def __init__(self, sync_client: mqtt.Client, parent_nursery: trio.Nursery, max_buffer=100):
        self._client = sync_client
        self._nursery = parent_nursery

        self.socket = self._client.socket()

        self._cancel_scopes = []

        self._event_connect = trio.Event()
        self._event_large_write = trio.Event()
        self._event_should_read = trio.Event()
        self._event_should_read.set()

        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_socket_open = self._on_socket_open
        self._client.on_socket_close = self._on_socket_close
        self._client.on_message = self._on_message
        self._client.on_socket_register_write = self._on_socket_register_write
        self._client.on_socket_unregister_write = self._on_socket_unregister_write

        self._msg_send_channel, self._msg_receive_channel = trio.open_memory_channel(max_buffer)

        self.subscribe = self._client.subscribe
        self.publish = self._client.publish
        self.unsubscribe = self._client.unsubscribe
        self.will_set = self._client.will_set
        self.will_clear = self._client.will_clear
        self.proxy_set = self._client.proxy_set
        self.tls_set = self._client.tls_set
        self.tls_insecure_set = self._client.tls_insecure_set
        self.tls_set_context = self._client.tls_set_context
        self.user_data_set = self._client.user_data_set
        self.username_pw_set = self._client.username_pw_set
        self.ws_set_options = self._client.ws_set_options

    def _start_all_loop(self):
        self._nursery.start_soon(self._loop_read)
        self._nursery.start_soon(self._loop_write)
        self._nursery.start_soon(self._loop_misc)
        return self

    def _stop_all_loop(self):
        for cs in self._cancel_scopes:
            cs.cancel()

    async def _loop_misc(self):
        cs = trio.CancelScope()
        self._cancel_scopes.append(cs)
        await self._event_connect.wait()
        with cs:
            while self._client.loop_misc() == mqtt.MQTT_ERR_SUCCESS:
                await trio.sleep(1)

    async def _loop_read(self):
        cs = trio.CancelScope()
        self._cancel_scopes.append(cs)
        with cs:
            while True:
                await self._event_should_read.wait()
                await trio.hazmat.wait_readable(self.socket)
                self._client.loop_read()

    async def _loop_write(self):
        cs = trio.CancelScope()
        self._cancel_scopes.append(cs)
        with cs:
            while True:
                await self._event_large_write.wait()
                await trio.hazmat.wait_writable(self.socket)
                self._client.loop_write()

    def connect(self, host, port=1883, keepalive=60, bind_address="", bind_port=0, **kwargs):
        self._start_all_loop()
        self._client.connect(host, port, keepalive, bind_address, bind_port, **kwargs)

    def _on_connect(self, client, userdata, flags, rc):
        self._event_connect.set()

    async def messages(self):
        self._event_should_read.set()
        cs = trio.CancelScope()
        self._cancel_scopes.append(cs)
        with cs:
            while True:
                msg = await self._msg_receive_channel.receive()
                yield msg
                self._event_should_read.set()

    def _on_message(self, client, userdata, msg):
        try:
            self._msg_send_channel.send_nowait(msg)
        except trio.WouldBlock:
            print("Buffer full. Discarding an old msg!")
            # Take the old msg off the channel, discard it, and put the new msg on
            old_msg = self._msg_receive_channel.receive_nowait()
            # TODO: Store this old msg?
            self._msg_send_channel.send_nowait(msg)
            # Stop reading until the messages are read off the mem channel
            self._event_should_read = trio.Event()

    def disconnect(self, reasoncode=None, properties=None):
        self._client.disconnect(reasoncode, properties)
        self._stop_all_loop()

    def _on_disconnect(self, client, userdata, rc):
        self._event_connect = trio.Event()
        self._stop_all_loop()

    def _on_socket_open(self, client, userdata, sock):
        self.socket = sock
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)

    def _on_socket_close(self, client, userdata, sock):
        pass

    def _on_socket_register_write(self, client, userdata, sock):
        # large write request - start write loop
        self._event_large_write.set()

    def _on_socket_unregister_write(self, client, userdata, sock):
        # finished large write - stop write loop
        self._event_large_write = trio.Event()

