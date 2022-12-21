import socket
import logging

from pathlib import Path

from channel import ChannelManager, Client
from v import App
from settings import ADDRESS

channel_manager = ChannelManager()

logging.basicConfig(
    format='%(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


patt = App()


@patt.get(pattern='\/tv\/(\d+)\/channel\/(\d+)\/*')
def funcs(tv_id, channel_id):
    return tv_id, channel_id


@patt.get(pattern='/tv/list/(\d+).m3u8')
def get_m3u8(path):
    print(path)

def parser(data):
    data = data.decode('utf-8')
    data = data.split('\r\n')
    data = data[0].split(' ')

    return data

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind(ADDRESS)
    server.listen()
    print(f'*********************** SERVIDOR INICIADO - {ADDRESS} ***********************')
    while True:
        conn, addr = server.accept()
        client = Client(conn)
        logger.info(f'Nuevo cliente conectado {addr}')
        data = conn.recv(1024)
        if data:
            data = parser(data)
            logger.info(data)
            patt.url = data[1]
            channel = channel_manager.get_channel(*funcs())
            channel.attach(client)