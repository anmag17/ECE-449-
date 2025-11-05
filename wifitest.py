import socket
import time

# ====== CONFIG ======
ESP32_IP = "192.168.68.150"  # Replace with your ESP32’s IP address
PORT = 4210                  # Must match the port in your ESP32 code

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def sendWiFi(message: str):
    """Send a string message to the ESP32 over UDP."""
    data = message.encode('utf-8')
    sock.sendto(data, (ESP32_IP, PORT))
    print(f"Sent: {message}")

# ====== MAIN TEST LOOP ======
if __name__ == "__main__":
    print("Starting WiFi test...")
    count = 0
    try:
        while True:
            msg = f"Ping {count}"
            sendWiFi(msg)
            sendWiFi("DETER")
            time.sleep(1)
            sendWiFi("OFF")
            count += 1
            time.sleep(2)  # send every 2 seconds
    except KeyboardInterrupt:
        print("\nTest stopped by user.")
    finally:
        sock.close()
        print("Socket closed.")
