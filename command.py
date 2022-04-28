import sys
import comm
from comm import *
from PIL import Image


if __name__ == '__main__':
    if len(sys.argv) > 1:
        ip = sys.argv[1]
    else:
        ip = input('Enter an IP address of Relay Server (return for localhost):')
        if len(ip) < 1:
            ip = '127.0.0.1'
    client_socket = connect_to_relay(ip=ip)
    print('Connection established and relay server is ready!')
    try:
        while True:
            msg_type, message = get_message(client_socket)
            if msg_type == TEXT:
                message = ('roger '+message.decode()).upper()
            elif msg_type == IMAGE:
                im = comm.bytes_to_image(message)
                im.show()
                message = input('Enter response: ')
            send_message(client_socket, TEXT, message.encode())
    except Exception as e:
        print(e)
        print('Relay server shut down!')
    finally:
        client_socket.shutdown(socket.SHUT_RDWR)
        client_socket.close()
