# Network Example for COMP 3611 Project (Milestone 4)

## 1. Change file permissions

In order to run the files from the command line, you need to use the 'chmod' program to change permissions to executable. This may or may not be set when you clone this repository.

```
network-example $ chmod +x basic_cert.sh 
network-example $ chmod +x network.py 
```

## 2. Create certificate

This script will create 'cert.pem'. 
Read more about certificates [here](https://www.sslshopper.com/article-most-common-openssl-commands.html).

```
network-example $ ./basic_cert.sh
Generating a RSA private key
.................................+++++
..................................+++++
writing new private key to 'cert.pem'
```

## 3. Running program

Run `network.py` to start the program.

```
network-example $ ./network.py
Starting: broadcast_listener_worker
Starting: broadcast_sender_worker
Starting: tcp_listener_worker
(b'bcast_test: 0', ('10.0.0.10', 53950))
```

Run the script in another terminal while the first one is running. This time with the `--alt` option.
This will start the program on a different port.

```
network-example $ ./network.py --alt
Starting: broadcast_listener_worker
Starting: broadcast_sender_worker
Starting: tcp_listener_worker
(b'bcast_test: 0', ('10.0.0.10', 51500))
```

## 4. Sending message

Type in the terminal window while the program is running to send a message.

```
...
test_message
Bytes Sent:     test_message
Bytes Received: ACK from server
...

(In other terminal)
Echoing message from: 127.0.0.1
b'test_message'
```

```
...
heythere
Bytes Sent:     heythere
Bytes Received: ACK from server
...

(In other terminal)
Echoing message from: 127.0.0.1
b'heythere'
```

## 5. Close program with 'CTRL + C'

```
^C
Terminating: broadcast_listener_worker
listener shutting down
None
Terminating: broadcast_sender_worker
None
Terminating: tcp_listener_worker
None
network-example $
```

## 6. Running on different hosts

Follow similar steps as above, just use network-remote.py instead of network.py.
Make sure that both servers have the same `cert.pem` file generated earlier.
For example, if running the program on two hosts, one with IP 10.0.0.10 and the other with 10.0.0.11, do the following:

```
Host 1:
./network-remote.py 10.0.0.10

Host 2:
./network-remote.py 10.0.0.11
```

Rest of usage is the same as the other example.
Note the usage of signal handlers and multiprocessing.Event.
It's not necessary for a simple shutdown of the program, but it can be useful for more complex programs.
