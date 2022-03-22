#!/usr/bin/env python3

import argparse
import sys
import ssl
import socket
import signal
from threading import Thread
from time import sleep
from multiprocessing import Event, Process, Queue
from socketserver import BaseRequestHandler, TCPServer

parser = argparse.ArgumentParser(description='Basic python networking example')
parser.add_argument('rhost')
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


def tcp_listener(port, event):
    host = own_ip
    cntx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    cntx.load_cert_chain('cert.pem', 'cert.pem')

    server = TCPServer((host, port), tcp_handler)
    server.socket = cntx.wrap_socket(server.socket, server_side=True)

    # Spawn server in a separate thread so we can shut it down on signal
    Thread(target=lambda s: s.serve_forever(), args=(server,)).start()
    event.wait()
    server.shutdown()


def tcp_client(port, data):

    # Initialize a TCP client socket using SOCK_STREAM
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cntx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    cntx.check_hostname = False
    cntx.load_verify_locations('cert.pem')
    cntx.load_cert_chain('cert.pem')

    s = cntx.wrap_socket(s, server_hostname='test.server')

    try:
        # Establish connection to TCP server and exchange data
        s.connect((args.rhost, port))
        s.sendall(data.encode())
        # Read data from the TCP server and close the connection
        received = s.recv(1024)
    finally:
        s.close()

    print("Bytes Sent:     {}".format(data))
    print("Bytes Received: {}".format(received.decode()))


#######################################
#          Broadcast Example          #
#######################################
def broadcast_listener(port, event):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', port))
    s.settimeout(2)
    while not event.is_set():
        try:
            msg, sender = s.recvfrom(512)
            ip = sender[0]
            if ip != own_ip:
                print(f"Received data from broadcast: {msg}")
        except socket.timeout:
            pass


def broadcast_sender(sock, port, event, queue, name):
    while queue.empty():
        sleep(1)

    while not event.is_set() and not queue.empty():
        data = queue.get()
        msg = f'bcast_test from {name}: ' + data
        try:
            sock.sendto(msg.encode('ascii'), ('255.255.255.255', port))
        except Exception as e:
            print(f"Exiting sender: {e}")
        sleep(5)


def work_generator(queue, event):
    count = 0
    while not event.is_set():
        if queue.qsize() < 100:
            for _ in range(10):
                queue.put(str(count))
                count += 1


#######################################
#               Driver                #
#######################################
def communication_manager():
    # find own ip
    init_ip()
    bcast_port = 1337
    tcp_port = 9990

    default_handler = signal.getsignal(signal.SIGINT)
    # ignore SIGINT before procs are created so that they inherit this
    signal.signal(signal.SIGINT,signal.SIG_IGN)

    event = Event()
    queue = Queue()

    procs = []
    procs.append(Process(target=broadcast_listener,
                 name="broadcast_listener_worker",
                 args=(bcast_port, event,)))

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    procs.append(Process(target=broadcast_sender,
                 name="broadcast_sender_worker",
                 args=(s, bcast_port, event, queue, "worker1")))

    procs.append(Process(target=broadcast_sender,
                 name="broadcast_sender_worker2",
                 args=(s, bcast_port, event, queue, "worker2")))

    procs.append(Process(target=work_generator,
                 name="work_generator",
                 args=(queue, event)))

    procs.append(Process(target=tcp_listener,
                 name="tcp_listener_worker",
                 args=(tcp_port, event,)))

    try:
        for p in procs:
            print("Starting: {}".format(p.name))
            p.start()

        # Restore regular signal handler so that main proc can handle ctrl+C
        signal.signal(signal.SIGINT,default_handler)
        while True:
            tcp_client(tcp_port, input("Enter message to send: "))
            sleep(1)

    except KeyboardInterrupt:
        print("SIGINT received, please wait while program exits")
        event.set()
    finally:
        for p in procs:
            print("Terminating: {}".format(p.name))
            p.join()


if __name__ == "__main__":
    communication_manager()
