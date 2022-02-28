import time
import comm
from PIL import Image
from comm import *

if __name__ == '__main__':
    ip = input('Enter an IP address (return for localhost):')
    if len(ip.strip()) < 1:
        ip = '127.0.0.1'
    client_socket = connect_to_relay(ip=ip)
    client_socket = connect_to_relay()
    try:
        isDone = False
        while not isDone:
            # load image into memory
            img = Image.open('pic.jpeg')
            # convert the image to a byte string for transport over network
            img = comm.image_to_bytes(img)
            # send message over network to relay server
            send_message(client_socket, IMAGE, img)
            # wait for response back from command through relay server
            msg_type, message = get_message(client_socket)
            if msg_type == TEXT:  # message should be a text message; if not, ignore
                message = message.decode()
                print(message)
                if message == 'stop':
                    isDone = True
    except Exception as e:
        print(e)
        print('Relay server shut down!')
    finally:
        client_socket.shutdown(socket.SHUT_RDWR)
        client_socket.close()
