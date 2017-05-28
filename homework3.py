import socket
import sys
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto import Random

#setup server role
def server():
    #create a socket to use
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #define server address to use
    server_address = ('localhost', 8081)
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
                print >>sys.stderr, '"%s"' % data
                if data:
                    print >>sys.stderr, 'sending data back to the client'
                    connection.sendall('received message: ' + data)
                else:
                    print >>sys.stderr, 'no more data from', client_address
                    break
        finally:
            connection.close()
        return

#setup client role
def client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = ('localhost', 8081)

    print >>sys.stderr, 'connecting to %s port %s' % server_address
    sock.connect(server_address)

    try:
        message = raw_input('Enter the message you would like to send: ')
        while message != "exit":
            encrypt("test","test","test")
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

#TO-DO: add server public key encryption as verify authorization of server
def encrypt(filename):
    print("entered encrypt function")
    file_out = open(filename+"_encrypted", "wb")
    #imports clients public key to encrypt data
    public_client_key = RSA.import_key(open("rsa_server_key.pem")).publickey()

    #message to encrypt
    #message = "secret"
    message = open(filename, "rb").read()
    cipher = PKCS1_OAEP.new(public_client_key)

    file_out.write(cipher.encrypt(message))

    print("exiting encryption function")

    return

def decrypt(filename):
    print("entering decrypt function")

    file_in = open(filename, "rb").read()

    private_server_key = RSA.import_key(open("rsa_server_key.pem").read())

    cipher = PKCS1_OAEP.new(private_server_key)
    message = cipher.decrypt(file_in)

    print("decrypted message: " + message)
    print("exiting decrypt function")

    return

#initializes an empty string to be used to validate role input
choice = ''

while choice not in ['server', 's', 'client', 'c']:
    #TO-DO: move the encrypt function call into the client function
    encrypt("testtext.txt")
    decrypt("testtext.txt_encrypted")
    choice = raw_input('Enter your role(server or client)').lower()

if choice in ['client', 'c']:
    client()

else:
    server()
