import socket
import sys
from Crypto.Cipher import AES

def encrypt():
    data = open("test_text", "rb").read()
    encryption_suite = AES.new('Sixteen byte key', AES.MODE_CFB, 'This is the IV!!')
    cipher_text = encryption_suite.encrypt(data)
    return cipher_text

def decrypt(data):
    decryption_suite = AES.new('Sixteen byte key', AES.MODE_CFB, 'This is the IV!!')
    msg = decryption_suite.decrypt(data)
    return msg

#setup server role
def server():
    #create a socket to use
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #define server address to use
    server_address = ('localhost', 8080)
    print >>sys.stderr,'starting up on the %s port %s' % server_address
    #bind the socket to the server address
    sock.bind(server_address)

    #only allow one connection
    sock.listen(1)

    #loop to find connection requests
    while True:
        print >>sys.stderr, 'waiting for a connection'
        #accepts connection request from client
        connection, client_address = sock.accept()

        try:
            print >>sys.stderr, 'connection from', client_address

            #loop to receive messages from the client
            while True:
                #store message from client in data variable
                data = connection.recv(1024)
                print >>sys.stderr, '%s' % data
                if data:
                    data = decrypt(data)
                    connection.sendall('received message: ' + data)
                else:
                    break
        finally:
            connection.close()
        return

#setup client role
def client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = ('localhost', 8080)
    print >>sys.stderr, 'connecting to %s port %s' % server_address
    sock.connect(server_address)

    try:
        while True:
            message = raw_input('Enter the message you would like to send: ')
            if message == 'exit':
                sock.close()
                break
            message = encrypt()
            print >>sys.stderr, 'sending "%s"' % message
            sock.sendall(message)

            amount_received = 0
            amount_expected = len(message)

            while amount_received < amount_expected:
                data = sock.recv(1024)
                amount_received += len(data)
                print >>sys.stderr, '"%s"' % data
    finally:
        print >>sys.stderr, 'closing socket'
        sock.close()
    return

#initializes an empty string to be used to validate role input
choice = ''

while choice not in ['server', 's', 'client', 'c']:
    choice = raw_input('Enter your role(server or client)').lower()

if choice in ['client', 'c']:
    client()
else:
    server()
