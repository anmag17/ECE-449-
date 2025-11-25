import socket
import sys
# You might need the 'netifaces' library here, but a simpler method is often to use the 'ip' library result.
# For simplicity, we'll try a common trick:

def get_wlan0_ip():
    # Placeholder: In a real system, you'd use 'socket.gethostbyname(socket.gethostname())'
    # or an external library/command to reliably get the wlan0 IP.
    # For now, let's assume the router is .1 and we're looking for the broadcast source IP.
    
    # A reliable way on a Pi is to look up the IP of the wlan0 interface.
    # Let's use a try-catch and rely on the IP being in the range 192.168.68.X
    try:
        # Create a temporary socket to determine the local IP used for external communication
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("192.168.68.1", 1)) # Connect to the router/gateway on the network
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        print("Warning: Could not automatically determine local IP. Using 0.0.0.0.")
        return '0.0.0.0' # Fail-safe


def sendWiFi():
    ESP_IP = "192.168.68.255"
    PORT = 5005
    cmd = sys.argv[1] if len(sys.argv) > 1 else "D3"
    local_source_ip = get_wlan0_ip() # <-- NEW: Get the source IP

    print("Attempting to send WiFi command...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        # *** CRITICAL FIX: Explicitly bind the socket to the local Wi-Fi interface's IP ***
        sock.bind((local_source_ip, 0)) # 0 means use any available port

        sock.sendto(cmd.encode(), (ESP_IP, PORT))
        sock.close()
        print(f"WiFi broadcast '{cmd}' sent from {local_source_ip} to {ESP_IP}")
        
    except Exception as e:
        # The script is crashing here. This print statement will now show you the error!
        print(f"FATAL: Failed to send WiFi, CRASH ERROR: {e}")
        # To prevent silent crashing in service mode, you MUST have this catch block!