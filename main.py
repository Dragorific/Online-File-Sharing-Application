# Online File Sharing Program | 4DN4
# Sama Abd El Salam, Muhammad Umar Khan, Yasmeen Harb
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
    file_path = os.getcwd() + '\\server_files'
    CMD = {
        b'\x01' : "get",
        b'\x02' : "put",
        b'\x03' : "list",
    }

    def __init__(self, host, port, sdp_port):
        print(f"{time()}: We have created a Server object: {self}")
        # Read through the folder and print out all the folder contents
        self.contents = os.listdir(Server.file_path)
        self.host = host
        self.port = port
        self.sdp_port = sdp_port
        thread1 = threading.Thread(target=Server.udp_listen, args=(self.host, self.sdp_port))
        thread2 = threading.Thread(target=Server.tcp_listen, args=(self.host, self.port))

        print(f"{time()}: List of shared directory files: ")
        for item in self.contents:
            print(f"{time()}: -> {item}")

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()
        
    def udp_listen(host, port):
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


    def tcp_listen(host, port):
        # Set up TCP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))

        print(f"{time()}: Listening for TCP connections on host and port: {host}, {port}")
        try:
            s.listen()                  # Listen for incoming connections
            conn, addr = s.accept()     # Accept incoming connection
            print(f'{time()}: Connected to {addr}')
        except:
            print(f"{time()}: Server socket {s} is closed.")

        # Continuously listen for packets
        while True:
            data = conn.recv(1)  # look for 1 byte specifying the command, and handle data accordingly
            print(f'{time()}: Received packet from {addr}: {data}')
            # process the received data here
            if data == b'\x01':
                # Get command
                data = conn.recv(1)     # Receive size packet
                print(f'{time()}: Received file_size packet from {addr}: {data}')
                file_size = int.from_bytes(data, byteorder='big')
                
                data = conn.recv(file_size) # Receive file name
                filename = data.decode('utf-8')
                
                # Check if the file exists or not
                try:
                    file = open((Server.file_path + "\\" + filename), 'r').read()
                except FileNotFoundError:
                    print(f"{time()}: File not found, closing the connection.")
                    conn.close()

                file = open((Server.file_path + "\\" + filename), 'r').read()

                response = file.encode('utf-8')
                response_size = len(response).to_bytes(8, byteorder='big')

                # Send the filesize bytes first, then the file bytes itself
                try:
                    conn.sendall(response_size)
                    conn.sendall(response)
                except socket.error:
                    # If the client has closed the connection, close the
                    # socket on this end.
                    print(f"{time()}: Error sending packets, closing the connection.")
                    conn.close()
            elif data == b'\x02':
                # 1. receive file name size
                # 2. receive file name
                # 3. receive file size 
                # 4. receive file
                try:
                    data = conn.recv(1)                                     # receive file name size in bytes
                    file_name_size = int.from_bytes(data, byteorder='big')  # turn into int
                    data = conn.recv(file_name_size)                        # read the file name (str format)
                    filename = data.decode('utf-8')
                    data = conn.recv(8)  
                    file_size = int.from_bytes(data, byteorder='big')       # get the file size as int
                    data = conn.recv(file_size)
                    data = data.decode('utf-8')
                except:
                    print(f'{time()}: Error receiving bytes from client. ')

                try:    
                    with open((Server.file_path + "\\" + filename), 'w') as f:
                        f.write(data)
                except:
                    print(f'{time()}: Error writing to file of name: {filename}')            
                
                print(f'{time()}: Completed upload from client of file: {filename}')
            elif data == b'\x03':
                contents = os.listdir(Server.file_path)
                print(f'{time()}: Client has requested a list of server directory.')
                message = "Server directory: \n"
                for item in contents:
                    message += "-> " + item + "\n"

                conn.sendall(message.encode('utf-8'))
            elif not data:
                print(f"{time()}: The client has closed the connection.")
                break
            else:
                print(f"{time()}: The client has requested a command that is not handled yet.")


class Client:
    file_path = os.getcwd() + '\\client_files'
    CMD = {
        "get" : b'\x01',
        "put" : b'\x02',
        "list" : b'\x03',
    }

    def __init__(self):
        print(f"{time()}: We have created a Client object: {self}") 
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        
        while True:
            self.command = input(f"{time()}: Please enter a command: ")
            if(self.command == "scan"):
                # Set up UDP socket for broadcasting (sending)
                broadcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                broadcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                broadcast_sock.settimeout(2.0)      # Set timeout for receiving responses
                broadcast_port = 30000              # The well-known port for Service Discovery broadcasts

                # Set up Service Discovery Packet (SDP)
                sdp_data = b'SERVICE DISCOVERY'  

                # Broadcast the SDP to the network
                broadcast_sock.sendto(sdp_data, ('255.255.255.255', broadcast_port))

                # Continuously listen for responses
                while True:
                    try:
                        # Receive response from file sharing server using unicast
                        data, addr = broadcast_sock.recvfrom(1024)  # 1024 is the buffer size
                        print(f'{time()}: Received response from file sharing server {addr}: {data}')
                        # process the received response data here
                        print(data.decode('utf-8'))
                        if data:
                            break
                    except socket.timeout:
                        # Timeout occurred, no more responses expected
                        print(f"{time()}: Socket timeout.")
                        break
            elif (self.command == "llist"):
                # local list which is client files
                files = os.listdir(Client.file_path)
                print(f"{time()}: Local directory: ")
                for file in files:
                    print(f'-> {file}')

            elif (self.command == "rlist"):
                # remote list which is server files
                # Check if TCP socket is open, otherwise it wont work
                is_connected = False
                try:
                    self.client_socket.getpeername()
                    is_connected = True
                except socket.error:
                    print(f"{time()}: The server is not connected")
                    pass  # Handle socket error

                if is_connected:
                    self.client_socket.sendall(Client.CMD["list"])
                    response = self.client_socket.recv(1024).decode()
                    print(response)

            elif (self.command == "bye"):
                print(f'{time()}: Server Connection Closed')
                self.client_socket.close()
                break
                
            # Assume the command is more than one word, i.e. "connect <ipAddr> <port>"
            try:
                command_parts = self.command.split(" ")
            except:
                print(f"{time()}: Could not split, invalid command.")
                break
            
            # If the command has 3 parts; connect <ipAddr> <port>
            if(len(command_parts) == 3):
                if(command_parts[0] == "connect"):
                    host = command_parts[1]
                    port = int(command_parts[2])
                    print(command_parts)
                    try:
                        self.client_socket.connect((host, port))
                        print(f"{time()}: Successfully connected to the server.")
                    except:
                        print(f"{time()}: Could not connect to the server.")

            # If the command has 2 parts; it is a get or put command
            elif(len(command_parts) == 2):
                try:
                    if(self.client_socket.getpeername()):
                        if(command_parts[0] == "get"):
                            # "Get" command processing here for downloading a file from the server
                            cmd_bytes = Client.CMD[command_parts[0]]                                                # 1 byte for command
                            file_name_size = len(command_parts[1].encode('utf-8')).to_bytes(1, byteorder='big')     # 1 byte for the size of the filename
                            file_name = command_parts[1].encode('utf-8')                                            # some bytes representing the filename
                            
                            print(cmd_bytes, file_name_size, file_name)

                            self.client_socket.sendall(cmd_bytes)
                            self.client_socket.sendall(file_name_size)
                            self.client_socket.sendall(file_name)
                            
                            try:
                                data = self.client_socket.recv(8)           # file size in bytes
                                recv_size = int.from_bytes(data, byteorder='big')   # turn into int
                                data = self.client_socket.recv(recv_size)   # read the full file (str format)
                                recv_file = data.decode('utf-8')
                            except:
                                print(f'{time()}: Error accessing file of name: {command_parts[1]} from server. ')
                                
                            with open((Client.file_path + "\\" + command_parts[1]), 'w') as f:
                                f.write(recv_file)
                            
                            print("Download complete")
                            
                        elif(command_parts[0] == "put"):
                            
                            # Put processing here
                            cmd_bytes = Client.CMD[command_parts[0]]                                                # 1 byte for command
                            file_name_size = len(command_parts[1].encode('utf-8')).to_bytes(1, byteorder='big')     # 1 byte for the size of the filename
                            file_name = command_parts[1].encode('utf-8')                                            # some bytes representing the filename
                            
                            print(cmd_bytes, file_name_size, file_name)

                            try:
                                file = open((Client.file_path + "\\" + command_parts[1]), 'r').read() 
                            except FileNotFoundError:
                                print(f"{time()}: File not found, closing the connection...")
                                self.client_socket.close()
                            
                            file = open((Client.file_path + "\\" + command_parts[1]), 'r').read()
                            file_data = file.encode('utf-8')     
                            file_size = len(file_data).to_bytes(8, byteorder='big')

                            # Upload a file to the server

                            # Send the filesize bytes first, then the file bytes itself
                            try:
                                print(f"{time()}: Uploading file: ", {command_parts[1]})
                                # 1. Send command byte
                                self.client_socket.sendall(cmd_bytes)
                                # 2. send filename size, 
                                self.client_socket.sendall(file_name_size)
                                # 3. send filename, 
                                self.client_socket.sendall(file_name)
                                # 4. send file size, 
                                self.client_socket.sendall(file_size)
                                # 5. send file.
                                self.client_socket.sendall(file_data)
                                print("Upload complete")
                            except socket.error:
                                # If the client has closed the connection, close the
                                # socket on this end.
                                print(f"{time()}: Error sending packets, uploading incomplete...")
                                self.client_socket.close()      

                except socket.error:
                    print(f"{time()}: The server is not connected")

        
if __name__ == '__main__':
    roles = {'client': Client,'server': Server}
    parser = argparse.ArgumentParser()
    defaultHost = "10.0.0.222"        # change this to ur ipv4 address

    parser.add_argument('-r', '--role', choices=roles, help='server or client role', required=True, type=str)
    parser.add_argument('--host', default=defaultHost, help="Server Host", type=str)
    parser.add_argument('--port', default=30001, help="Server Port", type=int)
    parser.add_argument('--sdp', default=30000, help="Server Port", type=int)

    args = parser.parse_args()

    if(args.role == 'client'):
        roles[args.role]()
    else:
        roles[args.role](args.host, args.port, args.sdp)
