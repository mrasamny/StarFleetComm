import socket
import selectors
import comm


def check_remove_disconnected_clients(sel: selectors, client_socket_list: list):
    index = 0
    while index < len(client_socket_list):
        client, addr = client_socket_list[index]
        if comm.is_socket_closed(client):  # client disconnected - close connection properly
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
    tcp_server = comm.start_tcp_server('127.0.0.1', 12000)
    sel.register(tcp_server, selectors.EVENT_READ, data='TCP_ACCEPT')


    while True:
        try:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data == 'TCP_ACCEPT':
                    check_remove_disconnected_clients(sel, tcp_client_socket);
                    client, addr = comm.accept_tcp_connection(key.fileobj)
                    tcp_client_socket.append((client, addr))
                    sel.register(client, selectors.EVENT_READ, data="MESG")
                    print('client registered!')
                    try:  # try sending to and receiving a greeting from tcp client
                        comm.send_message(client, comm.TEXT, 'hello')
                        msg_type, response = comm.get_message(client)
                    except Exception as e:  # if exception occurs, then stop server
                        print(e)
                        raise Exception
                elif key.data == 'MESG':
                    # send message from UDP client to TCP client for processing and return
                    # response from TCP client to UDP client
                    client = key.fileobj
                    comm.relay_message(client, tcp_client_socket)
        except ConnectionResetError as cre:
            print(cre)
        except Exception as e:
            sel.close()
            print(e)