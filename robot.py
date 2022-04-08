import time
import comm
import sys
from PIL import Image
import cv2
from comm import *

if __name__ == '__main__':
    if (len(sys.argv) > 1):
        ip = sys.argv[1]
    else:
        ip = '127.0.0.1'
    client_socket = connect_to_relay(ip=ip)
    try:
        vid = cv2.VideoCapture(0)
        time.sleep(1)
        isDone = False
        while not isDone:
            ret, img = vid.read()
            if not ret:
                break
            img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            img.show()
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
