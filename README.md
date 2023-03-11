# Computer-Networking Course Final Project
>Made by: [Yuval Shabat](https://github.com/yuvili) & [Alina Zahozi](https://github.com/AlinaZahozi)

## How To use
1. Navigate to ``DNS_Docs`` folder using your cd command (pycharm terminal). 
```sh
cd src/backend/DNS_Docs
```

2. Run ```dns_server.py``` with the `sudo` command.
```sh
sudo python3 dns_server.py
```
3. Next, navigate to ``src\frontend`` folder and run ```main.py```

## Introduction
This project contains 3 types of application layer servers:
- DHCP server
- DNS server
- HTTP server

### DHCP Server
This is an implementation of a DHCP server in Python. 
DHCP is a protocol used to assign IP addresses and other network configuration parameters to devices on a network. 
This server can assign IP addresses dynamically to devices on a network based on requests received from DHCP clients.

#### Requirements

- Python 3.x 
- socket module 
- struct module 
- random module 
- binascii module

#### Usage
To use this DHCP server, simply run the dhcp_server.py file. 
The server will listen for DHCP Discovery and DHCP Request messages on port 67, 
and respond with DHCP Offer and DHCP ACK messages, respectively.

You can customize the server configuration by modifying the following variables in the dhcp_server.py file:
- `SERVER_IP`: The IP address of the DHCP server
- `SUBNET_MASK`: The subnet mask for the network
- `ROUTER_IP`: The IP address of the default gateway/router for the network
- `DNS_SERVER_IP`: The IP address of the DNS server for the network
- `LEASE`: The lease time for assigned IP addresses, in seconds
- `available_addresses`: A list of available IP addresses that can be assigned by the server
Note that the server will only assign IP addresses from the available_addresses list, so be sure to update this list with the desired IP address range for your network.

### DNS Server
This is a DNS server written in Python that can handle DNS queries and respond with an IP address for a given hostname.

#### Requirements
- Python 3.x 
- socket module 
- struct module 
- time module 
- sys module

#### Usage

To start the DNS server, run the following command in a terminal:
```sh
  sudo python3 dns_server.py
  ```
This will start the server on the default DNS port (53) and listen for incoming DNS queries.
By default, the server will use a hard-coded IP address (127.0.0.1).

### HTTP Server

### GUI

### Unit-testing

## Sequence Diagram

## Hierarchy

## Links
