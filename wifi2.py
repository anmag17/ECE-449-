import socket

def sendWiFi():
    for i in range(0, 256):
        ESP_IP = f"192.168.68.{i}"
        PORT = 5005
        cmd = "D3"
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(cmd.encode(), (ESP_IP, PORT))
        sock.close()
        print(f"Sent '{cmd}' to {ESP_IP}:{PORT}")

if __name__ == "__main__":
    sendWiFi()
