import socket

def get_message(sock: socket.socket):
    size = sock.recv(4)
    size = int.from_bytes(size, byteorder='little')
    message = sock.recv(size).decode()
    print(message)
    return message


def send_message(sock: socket.socket, message: str):
    size = len(message).to_bytes(4, byteorder='little')
    sock.sendall(size+message.encode())


def connect(ip = '127.0.0.1', port = 12000):
    server = (ip, port)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server)
    # Get greetings from server and respond
    message = get_message(client_socket).upper()
    send_message(client_socket, message)
    return client_socket

if __name__ == '__main__':
    client_socket = connect()
    try:
        while True:
            message = get_message(client_socket)
            message = ('roger'+message).upper()
            # message = input('Enter message: ')
            send_message(client_socket, message)
    except Exception as e:
        print(e)
        print('Relay server shut down!')
    finally:
        client_socket.shutdown(socket.SHUT_RDWR)
        client_socket.close()
