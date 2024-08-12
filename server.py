import cv2
import socket
import struct
import pickle
import threading
import ssl

# Function to handle each client connection
def handle_client(client_socket, addr):
    print(f"Connected to client: {addr}")

    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

    try:
        while True:
            ret, frame = cam.read()
            frame = cv2.flip(frame, 1)
            result, image = cv2.imencode('.jpg', frame, encode_param)
            data = pickle.dumps(image, 0)
            size = len(data)
            
            # Send the frame size and frame data to the client
            client_socket.sendall(struct.pack(">L", size) + data)

            # Check if the client requested to stop streaming
            if client_exited[addr]:
                print(f"Client {addr} requested to exit stream.")
                break
    except Exception as e:
        print(f"Error: {e}")

    print(f"Connection with client {addr} closed")
    client_socket.close()

# Initialize the camera
cam = cv2.VideoCapture(0)

# Create an SSL context
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(certfile="server.crt", keyfile="server.key")

# Create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('192.168.43.147', 8485))  # Update with your IP and port
server_socket.listen(5)

print("Server is listening...")

# Dictionary to track client exit status
client_exited = {}

try:
    # Start streaming video immediately
    while True:
        # Accept client connections
        client_socket, addr = server_socket.accept()
        
        # Set the client exit status to False initially
        client_exited[addr] = False
        
        # Create a thread for each client connection
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()

except KeyboardInterrupt:
    # Clean up resources when Ctrl+C is pressed
    cam.release()
    server_socket.close()
    cv2.destroyAllWindows()