import socket

SOURCE_IP = "192.168.68.112"   # your Pi IP
DEST_IP   = "192.168.68.150"   # your ESP IP
PORT      = 5005
MESSAGE   = "D3"

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind to your Pi's IP so the packet uses the correct interface
sock.bind((SOURCE_IP, 0))

# Connect to the ESP so OS chooses correct routing/path (nc behavior)
sock.connect((DEST_IP, PORT))

# Send the message
sock.send(MESSAGE.encode())

print(f"Sent '{MESSAGE}' from {SOURCE_IP} -> {DEST_IP}:{PORT}")

sock.close()