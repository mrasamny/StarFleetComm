import os
import re
import time
import socket
from PIL import Image


TEXT = 0;
IMAGE = 1;
OTHER = 99;


def get_ip(ifaces=['wlan1', 'eth0', 'wlan0']) -> str:
    if isinstance(ifaces, str):
        ifaces = [ifaces]
    for iface in list(ifaces):
        search_str = f'ifconfig {iface}'
        result = os.popen(search_str).read()
        com = re.compile(r'(?<=inet )(.*)(?= netmask)', re.M)
        ipv4 = re.search(com, result)
        if ipv4:
            ipv4 = ipv4.groups()[0]
            return ipv4
    return ''


def is_socket_closed(sock: socket.socket) -> bool:
    try:
        data = sock.recv(16, socket.MSG_DONTWAIT | socket.MSG_PEEK)
        if len(data) == 0:
            return True
    except BlockingIOError as bioe:
        print(bioe)
        return False
    except ConnectionResetError as cre:
        print(cre)
        return True
    except BrokenPipeError as bpe:
        print(bpe)
        return True
    except Exception as e:
        print(e)
        return False
    return False


def is_data_available(sock: socket.socket) -> bool:
    try:
        data = sock.recv(16, socket.MSG_DONTWAIT | socket.MSG_PEEK)
        if len(data) != 0:
            return True
    except Exception as e:
        print(e)
        return False
    return False


def start_tcp_server(ip: str, port: int) -> socket.socket:
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server_socket.bind((ip, port))
    tcp_server_socket.listen(2)
    tcp_server_socket.setblocking(False);
    print(f"The TCP server is ready on ({ip}, {port}).")
    return tcp_server_socket


def start_udp_server(ip, port) -> socket.socket:
    udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_server_socket.bind((ip, port))
    udp_server_socket.setblocking(False);
    print(f"The UDP server is ready on ({ip}, {port}).")
    return udp_server_socket


def accept_tcp_connection(tcp_server: socket.socket) -> (socket.socket, (str, int)):
    tcp_connection_socket, addr = tcp_server.accept()
    tcp_connection_socket.setblocking(True)
    print(f"Accepted connection from {addr}!")
    return tcp_connection_socket, addr


def get_message(sock: socket.socket) -> (int, bytes):
    header = sock.recv(6)
    size = header[:4]
    msg_type = header[4:]
    # size of payload includes 2 bytes for message type
    size = int.from_bytes(size, byteorder='little')-len(msg_type)
    msg_type = int.from_bytes(msg_type, byteorder='little')
    message =b''
    num_of_bytes = min(size, 4096)
    while len(message) < size:
        message += sock.recv(num_of_bytes)
    return msg_type, message


def send_message(sock: socket.socket, msg_type: int, message: bytes):
    msg_type = msg_type.to_bytes(2, byteorder='little')
    message = msg_type+message
    size = len(message).to_bytes(4, byteorder='little')
    message = size+message
    size = len(message)
    num_of_bytes = min(size, 4096)
    total_bytes_sent = 0
    chunk = 1
    while total_bytes_sent < size:
        sock.sendall(message[(chunk-1)*num_of_bytes:chunk*num_of_bytes])
        total_bytes_sent += num_of_bytes
        chunk += 1


def connect_to_relay(ip = '127.0.0.1', port = 12000) -> socket.socket:
    server = (ip, port)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server)
    # Get greetings from server and respond
    msg_type, message = get_message(client_socket)
    send_message(client_socket, msg_type, message)
    print(f'Connection is established with relay server at {server}')
    print('Checking if relay session is ready.')
    # send ready message to see if relay is ready
    notReady = True
    while notReady:
        send_message(client_socket, TEXT, 'Ready'.encode())
        msg_type, message = get_message(client_socket)
        if msg_type == TEXT and message.decode() != 'RELAY_NOT_READY':
            notReady = False
        else:
            time.sleep(2)
    print('Relay session is ready! Live long and prosper!')
    return client_socket


def image_to_bytes(image: IMAGE) -> bytes:
    xsize, ysize = image.size
    xsize = xsize.to_bytes(2, byteorder='little')
    ysize = ysize.to_bytes(2, byteorder='little')
    image = image.tobytes()
    return xsize+ysize+image


def bytes_to_image(image_in_bytes: bytes) -> Image:
    width = image_in_bytes[:2]
    height = image_in_bytes[2:4]
    image_in_bytes = image_in_bytes[4:]
    width = int.from_bytes(width, byteorder='little')
    height = int.from_bytes(height, byteorder='little')
    image_in_bytes = Image.frombytes("RGB", (width, height), image_in_bytes)
    return image_in_bytes
