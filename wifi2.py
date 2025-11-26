import socket
import sys

def sendWiFi():
    BROADCAST_IP = "192.168.68.255"
    PORT = 5005
    cmd = sys.argv[1] if len(sys.argv) > 1 else "D3"

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Optional: bind to your local IP if needed
    # sock.bind(("192.168.68.112", 0))

    sock.sendto(cmd.encode(), (BROADCAST_IP, PORT))
    sock.close()

    print(f"Broadcasted '{cmd}' to {BROADCAST_IP}:{PORT}")

if __name__ == "__main__":
    sendWiFi()
