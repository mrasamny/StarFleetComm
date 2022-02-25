import os
import re
import socket
import selectors


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


def sendMessage(client: socket.socket, tcp_client_list: list):
    message_size = client.recv(4)
    message = client.recv(int.from_bytes(message_size, byteorder='little'))
    if len(tcp_client_list) < 2:
        message = 'Waiting for relay partner(s).'
        client.sendall(len(message).to_bytes(4, byteorder='little')+message.encode())
    else:
        for receiver, addr in tcp_client_list:
            if client == receiver:
                continue
            try:
                receiver.sendall(message_size+message)
            except Exception as e:
                print("Unable to send message from client {addr}")
                print(e)


def send_greeting(connection_socket):
    connection_socket.setblocking(True)
    greet = "hello".encode()
    connection_socket.sendall(len(greet).to_bytes(4, 'little'))
    connection_socket.sendall(greet)
    size = connection_socket.recv(4)
    greet = connection_socket.recv(int.from_bytes(size, byteorder='little'))
    print(f'GREETING: {greet.decode()}!')
    connection_socket.setblocking(False)


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
    except Exception as e:
        print(e)
        return False
    return False


def check_remove_disconnected_clients(sel: selectors, client_socket_list: list):
    index = 0
    while index < len(client_socket_list):
        client, addr = client_socket_list[index]
        if is_socket_closed(client):  # client disconnected - close connection properly
            sel.unregister(client)
            del client_socket_list[index]
        else:
            index += 1


if __name__ == "__main__":
    tcp_client_socket= []
    sel = selectors.DefaultSelector()
    # Get IP address from user
    ip = input('Enter an IP address (return for localhost):')
    if len(ip.strip()) < 1:
        ip = '127.0.0.1'
    # start up tcp and udp servers and register them with selectors
    tcp_server = start_tcp_server('127.0.0.1', 12000)
    sel.register(tcp_server, selectors.EVENT_READ, data='TCP_ACCEPT')
    #udp_server = start_udp_server('127.0.0.1', 12000)
    #sel.register(udp_server, selectors.EVENT_READ, data='UDP')


    while True:
        try:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data == 'TCP_ACCEPT':
                    check_remove_disconnected_clients(sel, tcp_client_socket);
                    client, addr = accept_tcp_connection(key.fileobj)
                    tcp_client_socket.append((client, addr))
                    sel.register(client,selectors.EVENT_READ,data="MESG")
                    try:  # try sending to and receiving a greeting from tcp client
                        send_greeting(client)
                    except Exception as e:  # if exception occurs, then stop server
                        print(e)
                        raise Exception
                elif key.data == 'MESG':
                    # send message from UDP client to TCP client for processing and return
                    # response from TCP client to UDP client
                    client = key.fileobj
                    sendMessage(client, tcp_client_socket)
        except ConnectionResetError as cre:
            print(cre)
        except Exception as e:
            sel.close()
            print(e)