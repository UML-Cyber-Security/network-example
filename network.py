#!/usr/bin/env python3
import sys
import ssl
import socket
from time import sleep
from multiprocessing import Process
from socketserver import BaseRequestHandler, TCPServer

own_ip = None

def init_ip():
    global own_ip
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    own_ip = s.getsockname()[0]
    s.close()


#######################################
#             TCP example             #
#######################################
class tcp_handler(BaseRequestHandler):
    def handle(self):
            self.data = self.request.recv(1024).strip()
            print("Echoing message from: {}".format(self.client_address[0]))
            print(self.data)
            self.request.sendall("ACK from server".encode())


def tcp_listener(port):
    host = "localhost"
    cntx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    cntx.load_cert_chain('cert.pem', 'cert.pem')

    server = TCPServer((host, port), tcp_handler)
    server.socket = cntx.wrap_socket(server.socket,server_side=True)
    try:
        server.serve_forever()
    except:
        print("listener shutting down")
        server.shutdown()


def tcp_client(port, data):
    host_ip = "127.0.0.1"

    # Initialize a TCP client socket using SOCK_STREAM
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cntx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    cntx.load_verify_locations('cert.pem')
    cntx.load_cert_chain('cert.pem')

    s = cntx.wrap_socket(s,server_hostname='test.server')

    try:
        # Establish connection to TCP server and exchange data
        s.connect((host_ip, port))
        s.sendall(data.encode())
        # Read data from the TCP server and close the connection
        received = s.recv(1024)
    finally:
        s.close()

    print ("Bytes Sent:     {}".format(data))
    print ("Bytes Received: {}".format(received.decode()))


#######################################
#          Broadcast Example          #
#######################################
def broadcast_listener(socket):
    try:
        while True:
            data = socket.recvfrom(512)
            print(data)
    except KeyboardInterrupt:
        pass


def broadcast_sender(port):
    count = 0
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while True:
            msg = 'bcast_test: ' + str(count)
            count += 1
            s.sendto(msg.encode('ascii'),('255.255.255.255', port))
            sleep(5)
    except KeyboardInterrupt:
        pass


#######################################
#               Driver                #
#######################################
def communication_manager(switch_ports=False):
    # find own ip
    init_ip()
    bcast_port = 1337 if switch_ports else 1338
    tcp_listen = 9990 if switch_ports else 9995
    tcp_port = 9995 if switch_ports else 9990

    # broadcast to other users that you exist
    broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    broadcast_socket.bind(('',bcast_port))

    broadcast_listener_worker = Process(target=broadcast_listener,
                                        name="broadcast_listener_worker",
                                        args=(broadcast_socket,))

    broadcast_sender_worker = Process(target=broadcast_sender,
                                      name="broadcast_sender_worker",
                                      args=(bcast_port,))

    tcp_listener_worker = Process(target=tcp_listener,
                                  name="tcp_listener_worker",
                                  args=(tcp_listen,))

    procs = [
             broadcast_listener_worker,
             broadcast_sender_worker,
             tcp_listener_worker,
            ]

    try:
        for p in procs:
            print("Starting: {}".format(p.name))
            p.start()
        while True:
            tcp_client(tcp_port, input())
            sleep(1)

    except KeyboardInterrupt:
        for p in procs:
            print("Terminating: {}".format(p.name))
            if p.is_alive():
                p.terminate()
                sleep(0.1)
            if not p.is_alive():
                print(p.join())

if len(sys.argv) > 1:
    communication_manager()
else:
    communication_manager(True)
