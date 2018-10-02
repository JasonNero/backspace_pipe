import socket
import sys

HOST = "127.0.0.1"
PORT = 7002
ADDR = (HOST, PORT)

def send(command):
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.connect(ADDR)
	client.send(command.encode("ascii"))
	response = client.recv(1024)
	client.close()
	return str(response)

if __name__ == '__main__':
	args = sys.argv[1]
	print(send(args))