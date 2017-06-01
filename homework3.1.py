import socket
import sys
from Crypto.Cipher import AES
from Crypto.Hash import SHA256

#used to hash data and return hexdigest
def hasher(data):
    h = SHA256.new()
    h.update(data)
    return h.hexdigest()

#need to take in a key and IV instead of hardcoding
def encrypt_personal_data(filename):
    data = open(filename, "rb").read()
    encryption_suite = AES.new('This is my key!!', AES.MODE_CFB, 'This is my IV!!!')
    cipher_text = encryption_suite.encrypt(data)
    return cipher_text

#need to take in a key and IV instead of hardcoding
def decrypt_personal_data(data):
    decryption_suite = AES.new('This is my key!!', AES.MODE_CFB, 'This is my IV!!!')
    msg = decryption_suite.decrypt(data)
    return msg

#need to take in a key and IV instead of hardcoding
def encrypt(data):
    encryption_suite = AES.new('Sixteen byte key', AES.MODE_CFB, 'This is the IV!!')
    cipher_text = encryption_suite.encrypt(data)
    return cipher_text

#need to take in a key and IV instead of hardcoding
def decrypt(data):
    decryption_suite = AES.new('Sixteen byte key', AES.MODE_CFB, 'This is the IV!!')
    msg = decryption_suite.decrypt(data)
    return msg

#setup server role
def server():
    #create a socket to use
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 8080)
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
                data = connection.recv(1024)
                print >>sys.stderr, '%s' % data
                #TO-DO compare hash value against the one that was sent
                if data:
                    data = decrypt(data)
                    #print(data)
                    filename = data[:64]
                    print('This is the filename hash: ' + filename)
                    hash_value = data[64:128]
                    print('This is the encrypted file hash: ' + hash_value)
                    data = data[128:]
                    print('This is the encrypted file: ' + data)
                    #print(data)
                    connection.sendall(data)
                else:
                    break
        finally:
            connection.close()
        return

def send():
    file_to_encrypt = raw_input('Enter the filename you would like to encrypt: ')
    if file_to_encrypt in ['exit', 'x']:
        return
    filename_hash = hasher(file_to_encrypt)
    print('This is the filename hash: ' + filename_hash)
    my_encrypted_file = encrypt_personal_data(file_to_encrypt)
    print('This is the encrypted file: ' + my_encrypted_file)
    hash_value = hasher(my_encrypted_file)
    print('This is the encrypted file hash: ' + hash_value)
    #print(my_encrypted_file)
    #print(hash_value)
    packet = filename_hash + hash_value + my_encrypted_file
    message = encrypt(packet)
    return message

#setup client role
#TO-DO need to write retrieve code, try to create more functions to reduce redundancy
def client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = ('localhost', 8080)
    print >>sys.stderr, 'connecting to %s port %s' % server_address
    sock.connect(server_address)

    try:
        while True:
            choice = ''
            while choice not in ['send', 's', 'retrieve', 'r', 'exit', 'x']:
                choice = raw_input('Would you like to send or retrieve data? ').lower()
            if choice == 'exit':
                break
            if choice in ['send', 's']:
                message = send()

            elif choice in ['retrieve', 'r']:
                    break
            sock.sendall(message)

            #NEED TO HANDLE THE LENGTH CORRECTLY
            amount_received = 0
            amount_expected = len(message[128:])

            while amount_received < amount_expected:
                data = sock.recv(1024)
                amount_received += len(data)
                #print(data)
                msg = decrypt_personal_data(data)
                print(msg)
                #print >>sys.stderr, data
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
