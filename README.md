# Network Example for COMP 3611 Project (Milestone 4)

## 1. Create certificate

When prompted, please fill in the information fields. This script will create 'cert.pem'. Read more about certificates [here](https://www.sslshopper.com/article-most-common-openssl-commands.html).

```
network-example $ ./basic_cert.sh
Generating a 2048 bit RSA private key
...........................+++
.........+++
writing new private key to 'cert.pem'
-----
...
-----
Country Name (2 letter code) []:US
State or Province Name (full name) []:Massachusetts
Locality Name (eg, city) []:Lowell
Organization Name (eg, company) []:UML
Organizational Unit Name (eg, section) []:100
Common Name (eg, fully qualified host name) []:test.server
Email Address []:server@gmail.com
```

## 2. Running program

Run this in a seperate terminal. This will start the program on port 53950.

```
network-example $ ./network.py
Starting: broadcast_listener_worker
Starting: broadcast_sender_worker
Starting: tcp_listener_worker
(b'bcast_test: 0', ('10.0.0.10', 53950))
```

Run this in another terminal while the first one is running. This will start the program on port 51500.

```
network-example $ ./network.py anything
Starting: broadcast_listener_worker
Starting: broadcast_sender_worker
Starting: tcp_listener_worker
(b'bcast_test: 0', ('10.0.0.10', 51500))
```

## 3. Sending message

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

## 4. Close program with 'CTRL + C'

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
