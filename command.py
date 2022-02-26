from comm import *
from PIL import Image


if __name__ == '__main__':
    client_socket = connect_to_relay()
    try:
        while True:
            msg_type, message = get_message(client_socket)
            if msg_type == TEXT:
                message = ('roger '+message).upper()
            elif msg_type == IMAGE:
                im = Image.frombytes(message)
                im.show()
                message = 'Image Received'
            # message = input('Enter message: ')
            send_message(client_socket, TEXT, message.encode())
    except Exception as e:
        print(e)
        print('Relay server shut down!')
    finally:
        client_socket.shutdown(socket.SHUT_RDWR)
        client_socket.close()
