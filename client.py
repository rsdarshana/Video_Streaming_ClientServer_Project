import cv2
import socket
import struct
import pickle
import numpy as np
import threading
import ssl

# Function to receive and display the video stream
def receive_video_stream(client_socket):
    data = b""
    payload_size = struct.calcsize(">L")
    while True:
        while len(data) < payload_size:
            data += client_socket.recv(4096)

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]

        while len(data) < msg_size:
            data += client_socket.recv(4096)

        frame_data = data[:msg_size]
        data = data[msg_size:]

        frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

        cv2.imshow('Video Stream', frame)
        
        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting video stream.")
            # Send message to the server indicating client exit
            client_socket.sendall(b"exit")
            break

    # Close the connection
    client_socket.close()
    cv2.destroyAllWindows()

# Create an SSL context
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.load_verify_locations(cafile="server.crt")  # Verify the server's certificate

# Connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.79.167', 8485))  # Update with the server's IP and port

# Start a thread to receive and display the video stream
video_thread = threading.Thread(target=receive_video_stream, args=(client_socket,))
video_thread.start()