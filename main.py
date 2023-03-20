# Online File Sharing Program | 4DN4
# Yasmeen Harb, Sama Youssef, Muhammad Umar Khan
# StudentID, StudentID, StudentID

########################################################################

import socket
import argparse
import os
import datetime
import threading

def time():
    return (datetime.datetime.now()).strftime("%H:%M:%S")

class Server:
    file_path = '/server_files'

    def __init__(self, host, port, sdp_port):
        print(f"{time()}: We have created a Server object: {self}")
        # Read through the folder and print out all the folder contents
        contents = os.listdir(Server.file_path)
        self.host = host
        self.port = port
        self.sdp_port = sdp_port
        thread1 = threading.Thread(target=Server.udp_listen, args=(self.host, self.sdp_port))
        thread2 = threading.Thread(target=Server.tcp_listen, args=(self.host, self.port))

        print(f"{time()}: List of shared directory files: ")
        for item in contents:
            print(f"- {item}")

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()
        
    def udp_listen(self, host, port):
        # Print the UDP Service Discovery message
        print(f"{time()}: Listening for Service Discovery messages on SDP port: {port}")
        # Set up UDP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((host, port))

        # Continuously listen for packets
        while True:
            data, addr = s.recvfrom(1024)  # 1024 is the buffer size
            print(f'{time()}: Received packet from {addr}: {data}')
            
            # process the received data here, 
            decoded_data = data.decode('utf-8')
            if(decoded_data == "SERVICE DISCOVERY"):
                # Send a response packet back to the client
                response = b"Sama and Meena's File Sharing Server"
                s.sendto(response, addr)


    def tcp_listen(self, host, port):
        # Set up TCP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        print(f"{time}: Listening for connections on port: {port}")
        s.listen()  # Listen for incoming connections

        # Continuously listen for packets
        while True:
            conn, addr = s.accept()  # Accept incoming connection
            data = conn.recv(1024)  # 1024 is the buffer size
            print(f'{time}: Received packet from {addr}: {data}')
            # process the received data here

class Client:
    file_path = '/client_files'

    def __init__(self, host, port):
        print(f"{time()}: We have created a Client object: {self}")  
        self.command = input(f"{time()}: Please enter a command: ")
        
        if(self.command == "scan"):
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((host, port))
            self.client_socket.sendall(self.student_number.encode('utf-8'))
        
        response = self.client_socket.recv(1024)

if __name__ == '__main__':
    roles = {'client': Client,'server': Server}
    parser = argparse.ArgumentParser()

    parser.add_argument('-r', '--role',
                        choices=roles, 
                        help='server or client role',
                        required=True, type=str)

    args = parser.parse_args()
    roles[args.role]()
