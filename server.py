import socket
from threading import Thread
from des import binary_to_text

# Inside the handle_client function
def handle_client(client_socket, addr, clients):
    try:
        print(f"New connection from {addr}")

        while True:
            # Receive a message from the client
            data = client_socket.recv(1024).decode('utf-8')

            if not data:
                break
            
            # Convert the received string back to a dictionary
            message_data = eval(data)

            length = message_data['length']
            encrypted_bin_message = message_data['encrypted_bin_message']
            print(f"message: {binary_to_text(encrypted_bin_message)}")

            # Broadcast the message to all clients
            for other_client, other_addr in clients:
                if other_client != client_socket:
                    try:
                        data = {
                            'length': length,
                            'encrypted_bin_message': encrypted_bin_message,
                            'source': f"{addr[0]}:{addr[1]}"  # Add both host and port to the data
                        }
                        other_client.send(str(data).encode('utf-8'))
                    except Exception as e:
                        print(f"Error broadcasting to {other_addr}: {e}")

    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        print(f"Connection from {addr} closed.")
        client_socket.close()
        
# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a specific address and port
host = '10.47.1.2'
port = 12345
server_socket.bind((host, port))

# Listen for incoming connections
server_socket.listen(5)
print(f"Server listening on {host}:{port}")

clients = []

try:
    while True:
        # Accept a connection from a client
        conn, addr = server_socket.accept()
        print(f"Connection from {addr}")

        # Add the new client to the list
        clients.append((conn, addr))

        # Start a new thread to handle the client
        client_thread = Thread(target=handle_client, args=(conn, addr, clients))
        client_thread.start()

finally:
    # Close the server socket when the server terminates
    server_socket.close()
