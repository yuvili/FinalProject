# Computer-Networking Course Final Project
>Made by: [Yuval Shabat](https://github.com/yuvili) & [Alina Zahozi](https://github.com/AlinaZahozi)

## How To use
Make sure you check our run of the project it this <a href="https://youtu.be/pYBoYVd-Fi4" target="_blank">link</a>.
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
The goal of this project is to develop a DHCP server, a DNS server, and an HTTP server. 
The DHCP server provides the option for clients to claim an IP address and release it when no longer needed. 
The DNS server enables clients to send DNS queries and receive responses. 
Lastly, the HTTP server is designed to redirect clients to a specific image through a URL.

The DHCP server assigns IP addresses dynamically, ensuring efficient use of available resources, 
while the DNS server simplifies the process of locating resources by mapping human-readable domain names to IP addresses. 
The HTTP server redirects clients to the desired image, enabling easy access to digital content.
Overall, this project aims to provide a comprehensive networking solution that simplifies the process of connecting to 
the network and accessing resources.

## Dependencies
- Python 3.x
- tkinter module
- costumetkinter module
- socket module 
- struct module 
- random module 
- binascii module
- threading module 

## DHCP
This is an implementation of a DHCP server in Python. 
DHCP is a protocol used to assign IP addresses and other network configuration parameters to devices on a network. 
This server can assign IP addresses dynamically to devices on a network based on requests received from DHCP clients.


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

## DNS 
This is a DNS server written in Python that can handle DNS queries and respond with an IP address for a given hostname.

To start the DNS server, run the following command in a terminal:
```sh
  sudo python3 dns_server.py
  ```
This will start the server on the default DNS port (53) and listen for incoming DNS queries.
By default, the server will use a hard-coded IP address (127.0.0.1).

## HTTP
### HTTP Server
This is a simple web server implemented in Python using socket programming. 
It handles with HTTP GET requests from client and respond with either an HTML file or an 
image file. The server contain the html file and send it to the client while receiving an HTML 
response, but this server don't have the png image file that needed for html file so while receiving png 
image file request the server redirect the client to another server (the image server) for downloading the image.

#### How it works
The server uses the socket library to create a socket object that listens for incoming packets on a specific IP address 
and port number. 
When a client sends an HTTP GET request to the server, the server uses the threading library to create a new thread to 
handle the client request. 
The thread reads the request, processes it, and sends a response back to the client. 
If the client requests an HTML file, the server reads the file from disk and sends it back to the client. 
If the client requests an image file, the server sends a redirection message to the client with the address of another server that contains the image file.

### HTTP Image Server

This is a simple server written in Python that serves a single image file to clients using the HTTP protocol.


#### How it works

The server is implemented using a loop that listens for incoming connections and spawns a new thread to handle each client request. 
The client_handler function handles the communication with the client, receiving the request and sending the response.
The image file is read from disk and sent to the client in chunks of 1024 bytes, using the sendall() method of the client socket.

### HTTP Client

This Python script provides a simple client that connects to a server to download an HTML file and an image file.

#### How it works
The client uses socket programming to establish a connection with the server and send HTTP requests. 
Specifically, it sends two requests:

An HTTP GET request for the HTML file:
```vbnet 
GET / HTTP/1.1
Host: 127:0:0:1
Accept: text/html,application/xhtml+xml
Connection: keep-alive
```

If the server responds with a status of HTTP/1.1 200 OK (text/html), the client extracts the HTML content from the response and saves it to a new file named new_html.html. It then opens this file in a web browser and sends a request for the image file.
An HTTP GET request for the image file:
```vbnet
GET /imgs/OurImage.png HTTP/1.1
Host: 127:0:0:1
Accept: image/webp,*/*
Connection: keep-alive
```
If the server responds with a status of HTTP/1.1 200 OK (JPEG JFIF image), 
the client extracts the image content from the response and saves it to a new file named 
OurImage.png.
If the server responds with a status of HTTP/1.1 301 Moved Permanently, 
it means that the image file is located on a different server. 
The client extracts the new server's IP address and port from the response and 
establishes a new connection with the new server to download the image file.

## GUI
### Main Screen
<img width="792" alt="welcome page" src="https://user-images.githubusercontent.com/77205478/224570304-894808ee-a642-42ef-a5dc-74f0453d921e.png">

### DHCP Screen
#### DHCP Main Screen
<img width="797" alt="dhcp main" src="https://user-images.githubusercontent.com/77205478/224570375-fe901918-a48d-45ff-9e4f-062817ac88fa.png">

#### DHCP OFFER Screen
<img width="800" alt="dhcp_got_ip" src="https://user-images.githubusercontent.com/77205478/224570413-a551b21b-8eae-43d3-934f-86c0c6c381c8.png">

#### DHCP ACK Screen
<img width="799" alt="dhcp_request_approve" src="https://user-images.githubusercontent.com/77205478/224570434-6872dbc5-5468-4830-bded-b326a2374781.png">

### DNS Screen
#### DNS Query
<img width="796" alt="dns_main" src="https://user-images.githubusercontent.com/77205478/224571030-4b9bc38a-488b-41bc-8e43-d7b0637d6d28.png">

#### DNS Response
<img width="800" alt="dns_got_ip" src="https://user-images.githubusercontent.com/77205478/224571054-32b04b5f-caaa-4128-b4d9-663ef8145835.png">

### HTTP Screen
<img width="797" alt="http_main" src="https://user-images.githubusercontent.com/77205478/224571078-c3d1966c-3832-48ca-ba75-c1afd6eb0534.png">
 When clicking "Get Image", a new browser tab will open with the desired image:
<img width="1440" alt="Screenshot 2023-03-13 at 19 59 11" src="https://user-images.githubusercontent.com/77205478/224788793-4ad8c7cd-0966-42be-92fb-1d8d8db944fa.png">

### Client Info Screen
<img width="803" alt="client info" src="https://user-images.githubusercontent.com/77205478/224571094-ecab6ac2-f5af-43af-a9a4-44d1ef3f1801.png">

## Sequence Diagram
### DHCP
![DHCP_Sequence_Diagram-DHCP_Sequence_Diagram](https://user-images.githubusercontent.com/77205478/224569367-71d2b0af-5e34-47cc-881b-32d79516684a.png)


### DNS
![DNS_Sequence_Diagram-DNS_Sequence_Diagram](https://user-images.githubusercontent.com/77205478/224569398-5a9b8800-17ab-4d00-a6c0-801a4e1ae0ec.png)

### HTTP
![HTTP_Sequence_Diagram-HTTP_Sequence_Diagram](https://user-images.githubusercontent.com/77205478/224569437-4fee7e68-9275-4132-ac7d-b37c6b545bcc.png)

## Hierarchy
![UML_Diagram](https://user-images.githubusercontent.com/77205478/224569531-54c19045-7472-4cc7-8e9f-eda2e401b54f.png)

## Links
- Basic idea of DHCP messages format - https://iponwire.com/dhcp-message-type/#DHCP_INFORM
- DHCP Lease operation - https://youtu.be/5QhnovYb6yM
- Interpret bytes as packed binary data - https://docs.python.org/3/library/struct.html
- DNS study - https://mislove.org/teaching/cs4700/spring11/handouts/project1-primer.pdf
- GUI documentation - https://github.com/TomSchimansky/CustomTkinter
- TCP CC - https://www.geeksforgeeks.org/tcp-congestion-control/
- TCP, HTTP, DNS - https://courses.campus.gov.il/courses/course-v1:ARIEL+ACD_RFP4_ARIEL_comm+2022_1/course/
- HTTP - https://www.youtube.com/watch?v=iYM2zFP3Zn0
- TCP - https://www.youtube.com/watch?v=HCHFX5O1IaQ

