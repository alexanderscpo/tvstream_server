from __future__ import annotations

import os
import socket

from threading import Thread
from typing import Tuple, Set
from pathlib import Path

import requests

import tool
from settings import TEMP_DIR


class Client:
    max_index: int = 0
    thread: Thread
    channel: Channel

    def __init__(self, conn):
        self.conn: socket.socket = conn

    def update(self, max_index: int):
        self.max_index = max_index

    def start(self, channel, start_index: int):
        self.channel: Channel = channel
        self.send_response()
        self.thread = Thread(target=self.send_stream, args=[
                             start_index, self.channel.id_channel])
        self.thread.start()

    def send_response(self):
        f= 'HTTP/1.1 200 OK\r\nAccept-Ranges: bytes\r\nContent-Type: video/mp2t\r\nConnection: close\\r\n\r\n'.encode('utf-8')
        self.conn.sendall(f)
    
    def send_stream(self, start_index: int, id_channel: str):
        current_index = start_index

        while True:
            if current_index < self.max_index:
                path_file = TEMP_DIR / f'{self.channel.id_channel}' / f'{current_index}.bin'
                with open(path_file, mode='rb') as file:
                    try:
                        self.conn.sendall(file.read())
                    except socket.error:
                        self.conn.close()
                        self.channel.detach(self)
                        break

                current_index += 1


class Channel:
    def __init__(self, id_channel, url, user_agent):
        self.url: str = url
        self.id_channel: str = id_channel
        self.user_agent = user_agent
        self.start_chunk = 0
        self.clients: Set[Client] = set()
        self.clients_connected = 0
        self.task_thread = Thread(target=self.get_stream)
        self.task_thread.start()

    def attach(self, client: Client) -> None:
        client.start(self, self.start_chunk)
        self.clients.add(client)

    def detach(self, client: Client) -> None:
        self.clients.remove(client)

    def notify(self, max_index: int):
        for client in self.clients:
            client.update(max_index)

    def get_stream(self) -> None:
        """get_stream Obtener el stream del canal
        """
        size = 0
        headers = {}
        cwd = TEMP_DIR / f'{self.id_channel}'

        if not cwd.exists():
            cwd.mkdir(parents=True, exist_ok=True)

        if self.user_agent:
            headers = {
                'User-Agent': self.user_agent
            }
        r = requests.get(url=self.url, headers=headers, stream=True)


        for index, chunk in enumerate(r.iter_content(1024 * 1024)):
            if self.clients:
                path_file = cwd / f'{index}.bin'
                with open(path_file, 'wb+') as file:
                    file.write(chunk)
                self.notify(index)
                self.start_chunk = index
                size += 1
                if size == 20:
                    index_delete = (index + 1) - size
                    os.remove(cwd / f'{index_delete}.bin')
                    size -= 1
            else:
                break


class ChannelManager:
    channels = {}

    def __init__(self) -> None:
        tool.loads_m3u8()

    def get_channel(self, tv_id, channel_id) -> Channel:
        if channel_id not in self.channels:
            url, user_agent = tool.get_url_channel(tv_id, channel_id)
            self.channels[channel_id] = Channel(channel_id, url, user_agent)

        return self.channels[channel_id]
    
    
print((TEMP_DIR / '0.bin').exists())
