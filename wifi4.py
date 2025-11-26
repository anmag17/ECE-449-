import socket
import sys
# You might need the 'netifaces' library here, but a simpler method is often to use the 'ip' library result.
# For simplicity, we'll try a common trick:



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