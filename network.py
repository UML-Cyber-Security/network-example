#!/usr/bin/env python3
import sys
import ssl
import socket
import argparse
from time import sleep
from multiprocessing import Process
from socketserver import BaseRequestHandler, TCPServer

parser = argparse.ArgumentParser(description='Basic python networking example')
parser.add_argument('--alt', action='store_true')
args = parser.parse_args()

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
    host = own_ip
    cntx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    cntx.load_cert_chain('cert.pem', 'cert.pem')

    server = TCPServer((host, port), tcp_handler)
    server.socket = cntx.wrap_socket(server.socket, server_side=True)
    try:
        server.serve_forever()
    except:
        print("listener shutting down")
        server.shutdown()


def tcp_client(port, data):
    host_ip = own_ip

    # Initialize a TCP client socket using SOCK_STREAM
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cntx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    cntx.load_verify_locations('cert.pem')
    cntx.load_cert_chain('cert.pem')

    s = cntx.wrap_socket(s, server_hostname='test.server')

    try:
        # Establish connection to TCP server and exchange data
        s.connect((host_ip, port))
        s.sendall(data.encode())
        # Read data from the TCP server and close the connection
        received = s.recv(1024)
    finally:
        s.close()

    print(f"Bytes Sent:     {data}")
    print(f"Bytes Received: {received.decode()}")


#######################################
#          Broadcast Example          #
#######################################
def broadcast_listener(socket):
    try:
        while True:
            data = socket.recvfrom(512)
            print("Broadcast received: ", data)
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
            s.sendto(msg.encode('ascii'), ('255.255.255.255', port))
            sleep(5)
    except KeyboardInterrupt:
        pass


#######################################
#               Driver                #
#######################################
def communication_manager():
    # find own ip
    init_ip()

    bcast_port = 1337 if args.alt else 1338
    tcp_listen = 9990 if args.alt else 9995
    tcp_port = 9995 if args.alt else 9990

    # broadcast to other users that you exist
    broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    broadcast_socket.bind(('', bcast_port))
    procs = []
    procs.append(Process(target=broadcast_listener,
                         name="broadcast_listener_worker",
                         args=(broadcast_socket,)))

    procs.append(Process(target=broadcast_sender,
                 name="broadcast_sender_worker",
                 args=(bcast_port,)))

    procs.append(Process(target=tcp_listener,
                 name="tcp_listener_worker",
                 args=(tcp_listen,)))

    try:
        for p in procs:
            print("Starting: {}".format(p.name))
            p.start()
        while True:
            tcp_client(tcp_port, input("Enter message to send: "))
            sleep(1)

    except KeyboardInterrupt:
        for p in procs:
            print("Terminating: {}".format(p.name))
            if p.is_alive():
                p.terminate()
                sleep(0.1)
            if not p.is_alive():
                print(p.join())


#######################################
#               Main                  #
#######################################
def main():
    communication_manager()


if __name__ == "__main__":
    main()
