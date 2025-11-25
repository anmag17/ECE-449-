import socket
import sys

    # function to send message to deter ESP32 via wifi
def sendWiFi():
    ESP_PORT = 5005
    # Use the Broadcast IP for your subnet. 
    # If your IP is 192.168.68.x, the broadcast is usually .255
    BROADCAST_IP = "192.168.68.255" 
    
    cmd = "D3" # Default command
    
    # Safety check for sys.argv to prevent crashes if args are missing
    if len(sys.argv) > 1:
        cmd = sys.argv[1]

    try:
        # Create socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Set option to allow Broadcast packets (Essential!)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        print(f"Sending WiFi command '{cmd}' to {BROADCAST_IP}...")
        sock.sendto(cmd.encode(), (BROADCAST_IP, ESP_PORT))
        sock.close()
        print("WiFi packet sent.")
        
    except Exception as e:
        print(f"Error sending WiFi: {e}")

if __name__ == "__main__":
    sendWiFi()
