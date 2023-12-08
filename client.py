import socket
from threading import Thread
from des import binary_to_text, encrypt, decrypt, generateKeys, text_to_binary
from rsa import *

public_key_table = {}

# Inside the receive_messages function


def receive_messages(client_socket):
    try:

        while True:
            # Receive and print messages from the server
            recieved_data = client_socket.recv(1024).decode('utf-8')

            if not recieved_data:
                break

            # Convert the received string back to a dictionary
            data = eval(recieved_data)

            if 'encrypted_bin_message' in data:
                length = data['length']
                encrypted_bin_message = data['encrypted_bin_message']
                source = data['source']

                # Decrypt the message
                decrypted_bin_message = ''
                for i in range(0, len(encrypted_bin_message), 64):
                    chunk = encrypted_bin_message[i:i+64]
                    decrypted_chunk = decrypt(chunk, round_key)
                    decrypted_bin_message += decrypted_chunk

                # Trim the message to its original length
                decrypted_message = binary_to_text(decrypted_bin_message)

                print(f"Received from {source}:")
                print(f"Raw         : {binary_to_text(encrypted_bin_message)}")
                print(f"Decrypted   : {decrypted_message[:length]}")
            else:
                public_key_table[data['addr']] = {
                    'public_key': data['public_key'],
                    'username': data['username']
                }
                print("===update===")
                print(public_key_table)

    except Exception as e:
        print(f"Error receiving messages: {e}")
    finally:
        # Close the client socket when the thread terminates
        client_socket.close()


if __name__ == '__main__':
    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    host = '127.0.0.1'
    port = 12345
    client_socket.connect((host, port))

    # Start a thread for receiving messages
    receive_thread = Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    public_key, private_key, n = setkeys()
    # print(public_key, private_key, n)

    whoami = str(input("What is your name?"))

    # key = 'abcd7890'
    # bin_key = text_to_binary(key)[0]
    # round_key = generateKeys(bin_key)

    try:
        client_socket.send(str({
            'public_key': public_key,
            'username': whoami
        }).encode('utf-8'))

        # Recieve Public Keys Table
        recv_pubs_table = client_socket.recv(1024).decode('utf-8')
        public_key_table_data = eval(recv_pubs_table)
        public_key_table.update(public_key_table_data['public_key_table'])

        print(public_key_table)
        print("Enter your message (Ctrl+C to exit): ")
        while True:
            # Get user input for the message
            message_to_send = str(input())

            # Break the loop if the user presses Ctrl+C
            if not message_to_send:
                break

            # client_socket.send(message_to_send.encode('utf-8'))

            bin_message = text_to_binary(message_to_send)
            encrypted_bin_message = ''
            for chunk in bin_message:
                encrypted_bin_message += encrypt(chunk, round_key)

            # Create a dictionary with message length and encrypted message
            data = {
                'length': len(message_to_send),
                'encrypted_bin_message': encrypted_bin_message
            }

            # Send the dictionary as a string to the server
            client_socket.send(str(data).encode('utf-8'))
    except KeyboardInterrupt:
        print("\nTerminating client...")
    finally:
        # Close the connection with the server
        client_socket.close()
