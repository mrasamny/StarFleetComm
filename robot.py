from PIL import Image
import numpy as np
import cv2
from comm import *


if __name__ == '__main__':
    client_socket = connect_to_relay()
    try:
        while True:
            #message = input('Enter message: ')
            img = cv2.imread('pic.jpeg')
            # im = Image.open('pic.jpeg')
            im = Image.fromarray(img,mode='RGB')
            im.show()
            send_message(client_socket, IMAGE, img.tobytes())
            # wait for response
            msg_type, message = get_message(client_socket)
    except Exception as e:
        print(e)
        print('Relay server shut down!')
    finally:
        client_socket.shutdown(socket.SHUT_RDWR)
        client_socket.close()
