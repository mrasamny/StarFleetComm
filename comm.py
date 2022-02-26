import os
import re
import socket


TEXT = 0;
IMAGE = 1;
OTHER = 99;


def get_ip(ifaces=['wlan1', 'eth0', 'wlan0']):
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
        print('=======================')
        data = sock.recv(16, socket.MSG_DONTWAIT | socket.MSG_PEEK)
        print('=======================', len(data))
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


def is_data_available(sock: socket.socket):
    try:
        data = sock.recv(16, socket.MSG_DONTWAIT | socket.MSG_PEEK)
        if len(data) != 0:
            return True
    except Exception as e:
        print(e)
        return False
    return False


def start_tcp_server(ip,port):
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server_socket.bind((ip, port))
    tcp_server_socket.listen(2)
    tcp_server_socket.setblocking(False);
    print(f"The TCP server is ready on ({ip}, {port}).")
    return tcp_server_socket


def start_udp_server(ip, port):
    udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_server_socket.bind((ip, port))
    udp_server_socket.setblocking(False);
    print(f"The UDP server is ready on ({ip}, {port}).")
    return udp_server_socket


def accept_tcp_connection(tcp_server):
    tcp_connection_socket, addr = tcp_server.accept()
    tcp_connection_socket.setblocking(True)
    print(f"Accepted connection from {addr}!")
    return tcp_connection_socket, addr

def get_message(sock: socket.socket):
    header = sock.recv(6)
    size = header[:4]
    msg_type = header[4:]
    # size of payload includes 2 bytes for message type
    size = int.from_bytes(size, byteorder='little')-len(msg_type)
    msg_type = int.from_bytes(msg_type, byteorder='little')
    message = sock.recv(size).decode()
    print(msg_type, message)
    return msg_type, message


def send_message(sock: socket.socket, msg_type: int, message: bytes):
    msg_type = msg_type.to_bytes(2, byteorder='little')
    message = msg_type+message
    size = len(message).to_bytes(4, byteorder='little')
    sock.sendall(size+message)


def connect_to_relay(ip = '127.0.0.1', port = 12000):
    server = (ip, port)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server)
    # Get greetings from server and respond
    msg_type, message = get_message(client_socket)
    send_message(client_socket, msg_type, message.upper().encode())
    return client_socket