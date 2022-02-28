import socket
import selectors
import comm


def relay_message(sel: selectors, client: socket.socket, tcp_client_list: list):
    mesg_type, message = comm.get_message(client)
    if len(message) < 1:
        index = tcp_client_list.index(client)
        if index >= 0:
            del tcp_client_list[index]
        raise Exception(f'Lost connection to {client}')
    if len(tcp_client_list) < 2:  # dump message and send relay not ready
        mesg_type = comm.TEXT
        message = 'RELAY_NOT_READY'
        comm.send_message(client, mesg_type, message.encode())
    else:
        index = 0
        while index < len(tcp_client_list):
            receiver = tcp_client_list[index]
            try:
                if client != receiver:
                    comm.send_message(receiver, mesg_type, message)
                index += 1
            except BrokenPipeError as e:
                print(e)
                del tcp_client_list[index]
                sel.unregister(receiver)


if __name__ == "__main__":
    tcp_client_socket= []
    sel = selectors.DefaultSelector()
    # Get IP address from user
    ip = input('Enter an IP address (return for localhost):')
    if len(ip.strip()) < 1:
        ip = '127.0.0.1'
    # start up tcp and udp servers and register them with selectors
    tcp_server = comm.start_tcp_server(ip, 12000)
    sel.register(tcp_server, selectors.EVENT_READ, data='TCP_ACCEPT')

    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data == 'TCP_ACCEPT':
                client, addr = comm.accept_tcp_connection(key.fileobj)
                tcp_client_socket.append(client)
                sel.register(client, selectors.EVENT_READ, data="MESG")
                try:  # try sending to and receiving a greeting from tcp client
                    comm.send_message(client, comm.TEXT, 'hello'.encode())
                    msg_type, response = comm.get_message(client)
                except Exception as e:  # if exception occurs, then stop server
                    print(e)
                    sel.unregister(client)
            elif key.data == 'MESG':
                # send message from UDP client to TCP client for processing and return
                # response from TCP client to UDP client
                client = key.fileobj
                try:
                    relay_message(sel, client, tcp_client_socket)
                except Exception as e:  # if exception occurs, then stop server
                    print(e)
                    sel.unregister(client)
    sel.close()