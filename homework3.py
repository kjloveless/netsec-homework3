import socket
import sys
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto import Random

### Homework 3
### Kyle Loveless & Matt OBzera

#setup server role
#TO-DO need to figure out how to decrypt, verify integrity, and store
def server():
    #create a socket to use
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 8081)
    print >>sys.stderr,'starting up on the %s port %s' % server_address
    sock.bind(server_address)
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
                data = connection.recv(4096)
                if data:
                    print >>sys.stderr, 'sending "%s" back to the client' % data
                    connection.sendall('received message: ' + data)
                else:
                    print >>sys.stderr, 'no more data from', client_address
                    break
        finally:
            connection.close()
        return

#setup client role
#TO-DO need to figure out how client will format packet of data to send
#I want to send an initial message containing the length of the packet the
#   server should expect to receive from the client so something like the
#   following: {Length of data packet}Server+
#Packet format should look like this -> {hash|encrypted data}Server+
def client():
    #set up connection to server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 8081)
    print >>sys.stderr, 'connecting to %s port %s' % server_address
    sock.connect(server_address)

    choice = raw_input("Would you like to send or retrieve data? ")
    if(choice == "send"):
        #begin communication with server and start performing data transfer
        try:
            filename = raw_input('Enter the filename you would like to encrypt and send: ')
            key_file = raw_input('Enter the key file you would like to encrypt with: ')

            encrypted_data = encrypt(filename, key_file)
            print(encrypted_data)

            hash_digest = hash(encrypted_data)
            #print hash for verification
            #print(hash_digest)

            #begin loop for client input
            message = "placeholder"
            while message != "exit":
                message = raw_input('Enter the message to send: ')
                if(message == "exit"):
                    break
                #the following is just being used for testing communication between
                #   client and server for now
                #print >>sys.stderr, 'sending "%s"' % message
                sock.sendall(message)
                amount_received = 0
                amount_expected = len(message)

                #loop of how much data to expect back from server
                while amount_received < amount_expected:
                    data = sock.recv(4096)
                    amount_received += len(data)
                    print >>sys.stderr, '"%s"' % data
        finally:
            print >>sys.stderr, 'closing socket'
            sock.close()
        return
    else:
        return

#used to create the hash digest for the encrypted message
def hash(data):
    h = SHA256.new()
    h.update(data)
    #print for testing
    #hash_value = h.hexdigest()
    #print("the hex digest of the data is: " + hash_value)
    return h.hexdigest()

#TO-DO: add server public key encryption as verify authorization of server
#   need to return the encrypted data for the client to use, also need to
#   generalize to allow specification of key file used to encrypt with
def encrypt(filename, key_file):
    try:
        #reads data in from file to encrypt
        message = open(filename, "rb").read()
        #imports clients public key to encrypt data
        public_client_key = RSA.import_key(open(key_file)).publickey()
        #sets up object used to encrypt
        cipher = PKCS1_OAEP.new(public_client_key)
        #returns encrypted data to let client/server handle
        return cipher.encrypt(message)
    except:
        #passes file not found exception
        pass
        return

#function used to decrypt data
#TO-DO need to decide on how i want to handle decrypting on server or
#   client side
def decrypt(filename):
    #opens file to decrypt data from
    file_in = open(filename, "rb").read()
    #creates file to write decrypted data to
    file_out = open(filename+"_decrypted", "wb")
    #imports private key to decrypt with
    private_server_key = RSA.import_key(open("rsa_server_key.pem").read())
    #sets up new object to decrypt with
    cipher = PKCS1_OAEP.new(private_server_key)
    #print("decrypted message: " + message)
    file_out.write(cipher.decrypt(file_in))
    return

#initializes an empty string to be used to validate role input
choice = ''

while choice not in ['server', 's', 'client', 'c']:
    choice = raw_input('Enter your role(server or client)').lower()

if choice in ['client', 'c']:
    client()

else:
    server()
