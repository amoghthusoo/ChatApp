import socket as so
import threading as th

server_socket = so.socket()

print()
ip_address = input("Enter IP Address : ")
port = 9999

server_socket.bind((ip_address, port))
server_socket.listen(1)

client_socket, client_address = server_socket.accept()
print("Successfully Connected with Client.")
print("Start Messaging ...")

def send():
    while True:
        message = input()
        client_socket.send(message.encode())

def receive():
    while True:
        message = client_socket.recv(1024).decode()
        print(message)

sending_thread = th.Thread(target=send)
sending_thread.start()

receiving_thread = th.Thread(target=receive)
receiving_thread.start()