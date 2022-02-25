from comm import *


if __name__ == '__main__':
    client_socket = connect_to_relay()
    try:
        while True:
            message = input('Enter message: ')
            send_message(client_socket, TEXT, message)
            # wait for response
            msg_type, message = get_message(client_socket)
    except Exception as e:
        print(e)
        print('Relay server shut down!')
    finally:
        client_socket.shutdown(socket.SHUT_RDWR)
        client_socket.close()
